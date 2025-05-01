# Standard Library Imports
import os
import uuid
import datetime
import base64
import random
import json
import string
from dotenv import load_dotenv
from enum import Enum

# Load environment variables from .env file
load_dotenv()

# Third-Party Imports
from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    send_from_directory,
    redirect,
    url_for,
    current_app,
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
    LoginManager
)
from flask_bcrypt import Bcrypt # For password hashing
from flask_migrate import Migrate

from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize the Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Initialize the database
db = SQLAlchemy(app)

# Register Flask-Migrate
migrate = Migrate(app, db)  

# Initialize the Bcrypt
bcrypt = Bcrypt(app)

# Initialize the LoginManager
login_manager = LoginManager()
login_manager.init_app(app)  # Associate it with the app
login_manager.login_view = 'login'  # Redirect unauthorized users to the login page


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(user_id=user_id).first()


# Route to render the index page
@app.route('/')
def index():
    return render_template('app/semester_1/average_index.html')


# ========================
# Database Models
# ========================

class FacultyEnum(Enum):
    COMPUTER_SCIENCE = "Computer Science"
    PETROLEUM_ENGINEERING = "Petroleum Engineering"
    CHEMICAL_ENGINEERING = "Chemical Engineering"
    GEOPHYSICS_ENGINEERING = "Geophysics Engineering"

class YearEnum(Enum):
    YEAR_2016 = "2016"
    YEAR_2017 = "2017"
    YEAR_2018 = "2018"
    YEAR_2019 = "2019"
    YEAR_2020 = "2020"
    YEAR_2021 = "2021"
    YEAR_2022 = "2022"
    YEAR_2023 = "2023"
    YEAR_2024 = "2024"
    YEAR_2025 = "2025"

class SemesterEnum(Enum):
    SEMESTER_1 = "1"
    SEMESTER_2 = "2"

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True, default="static/images/default_profile.png")
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    last_updated = db.Column(db.DateTime, default=datetime.datetime.now())
    last_login = db.Column(db.DateTime, default=datetime.datetime.now())
    is_deleted = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)

    # University related fields as Enums
    faculty = db.Column(db.Enum(FacultyEnum), nullable=True)
    year = db.Column(db.Enum(YearEnum), nullable=True)
    semester = db.Column(db.Enum(SemesterEnum), nullable=True)

    # Relationships with cascading delete
    reset_tokens = db.relationship(
        'PasswordResetToken',
        backref='user',
        cascade='all, delete-orphan'
    )
    security_codes = db.relationship(
        'LoginSecurityCode',
        backref='user',
        cascade='all, delete-orphan'
    )

    def __str__(self) -> str:
        return f"{self.id} : {self.username}"
    
    def get_id(self) -> str:
        return self.user_id 

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(150),
        db.ForeignKey('users.user_id'),
        nullable=False
    )
    token = db.Column(db.String(150), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())


class LoginSecurityCode(db.Model):
    __tablename__ = 'login_security_codes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(150),
        db.ForeignKey('users.user_id'),
        nullable=False
    )
    security_code = db.Column(db.String(150), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

class AverageScores(db.Model):
    __tablename__ = 'average_scores'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(150),
        db.ForeignKey('users.user_id'),
        nullable=False
    )
    scores_base64 = db.Column(db.String(2000), nullable=False)
    semester = db.Column(db.Enum(SemesterEnum), nullable=False)
    faculty = db.Column(db.Enum(FacultyEnum), nullable=False)
    average_score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now())
    user = db.relationship('User', backref='average_scores')
    def __str__(self) -> str:
        return f"{self.user.username} - Semester:{self.semester} - Score: {self.average_score}"

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    elif request.method == 'POST':
        data = request.json

        if not data.get('username') or not data.get('email') or not data.get('password') or not data.get('faculty') or not data.get('year') or not data.get('semester'):
            return jsonify({'error': 'All fields are required'}), 400
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')


        faculty = FacultyEnum(data.get('faculty'))
        year = YearEnum(data.get('year'))
        semester = SemesterEnum(data.get('semester'))

        # Check for missing fields
        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400

        # Check if user exists
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            return jsonify({'error': 'User already exists'}), 400

        # Uuid for user_id
        user_id = str(uuid.uuid4())
        
        # Hash the password using Bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create new user
        new_user = User(user_id=user_id, username=username, email=email, password=hashed_password, faculty=faculty, year=year, semester=semester)
        db.session.add(new_user)
        db.session.commit()

        # email_sender = SendEmail()
        # email_sender.register_welcome(receiver_email=email,username=username) 

        return jsonify({'message': 'User registered successfully'}), 201

# Login Endpoints
def generate_security_code():
    return f"{random.randint(100000, 999999)}"

    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    elif request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'All fields are required'}), 400

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not bcrypt.check_password_hash(user.password, password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        login_user(user)
        user.last_login = datetime.datetime.now()
        db.session.commit()

        return jsonify({'message': 'Login successful'}), 200



@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == "GET":
        return render_template('forgot-password.html')
    if request.method == "POST":
        data = request.json
        email = data.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate a password reset link
            email_sender = SendEmail()
            new_password_reset_token = PasswordResetToken.query.filter_by(user_id=user.user_id).first()
            if not new_password_reset_token:
                string = str(uuid.uuid4()) + str(uuid.uuid4())
                encoded_string = base64.b64encode(string.encode('utf-8')).decode('utf-8')

                # Create and save the PasswordResetToken
                new_password_reset_token = PasswordResetToken(user_id=user.user_id, token=encoded_string)
                db.session.add(new_password_reset_token)  # Add to session here

            # Generate the reset link
            reset_link = f'https://kyklos.site/reset-password?token={new_password_reset_token.token}'
            # reset_link = f'http://127.0.0.1:5000/reset-password?token={new_password_reset_token.token}'
            
            # Send the password reset email
            email_sender.password_reset(email, user.username, reset_link)

        db.session.commit()  # Commit all changes to the database
        return jsonify({'message': 'Password reset email sent successfully'}), 200

    
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == "GET":
        token = request.args.get('token')
        if not token:
            return 'Invalid or expired token', 400
        return render_template('reset-password.html', token=token)

    if request.method == "POST":
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')
        new_password_confirm = data.get('new_password_confirm')

        if not token or not new_password or not new_password_confirm:
            return jsonify({'error': 'All fields are required'}), 400

        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        if not reset_token:
            return jsonify({'error': 'Invalid token'}), 400

        # Check for token expiration
        # if datetime.datetime.now() - reset_token.created_at > timedelta(hours=1):  # Adjust expiry duration
        #     return jsonify({'error': 'Token has expired'}), 400

        user = User.query.filter_by(user_id=reset_token.user_id).first()
        if not user:
            return jsonify({'error': 'Invalid token'}), 400

        if new_password != new_password_confirm:
            return jsonify({'error': 'Passwords do not match'}), 400

        # Update the user password
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        # Optionally, delete the reset token after use
        db.session.delete(reset_token)
        db.session.commit()

        return jsonify({'message': 'Password reset successfully'}), 200


# User Profile
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'GET':
        return render_template('users/profile.html')

    elif request.method == 'POST':
        # Update user profile
        data = request.json
        user = current_user

        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)

        # Convert string values to Enum instances for faculty, year, and semester
        faculty_value = data.get("faculty")
        if faculty_value:
            user.faculty = FacultyEnum(faculty_value)

        year_value = data.get("year")
        if year_value:
            user.year = YearEnum(year_value)  # Enum names are prefixed with "YEAR_"

        semester_value = data.get("semester")
        if semester_value:
            user.semester = SemesterEnum(semester_value)  # Enum names are prefixed with "SEMESTER_"

        db.session.commit()
        return jsonify({"message": "Profile updated successfully!"}), 200
    
@app.route('/get-profile', methods=['GET'])
@login_required
def get_profile():
    user = current_user
    data = {
        "username": user.username,
        "email": user.email,
        "faculty": user.faculty.value if user.semester else None,  # Convert Enum to string
        "year": user.year.value if user.semester else None,          # Convert Enum to string
        "semester": user.semester.value if user.semester else None  # Convert Enum to string
    }
    print(data)
    return jsonify(data), 200


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-profile-picture', methods=['POST'])
@login_required
def upload_profile_picture():
    if 'profile_picture' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['profile_picture']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static/uploads/profile_pictures')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # Update user's profile picture in the database
        user = current_user
        user.profile_picture = f"static/uploads/profile_pictures/{filename}"
        db.session.commit()

        return jsonify({"message": "Profile picture uploaded successfully!", "profile_picture_url": user.profile_picture}), 200
    
    return jsonify({"error": "Invalid file type"}), 400



# User scores
@app.route('/save-score', methods=['POST'])
def save_score():
    if not current_user.is_authenticated:
        return jsonify({"message": "You can get better experience if you register and login", "code": "not_logged_in"}), 200
    
    # Check if the request contains JSON data
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    if not data.get('semester'):
        return jsonify({"error": "Semester is required"}), 400
    if not data.get('faculty'):
        return jsonify({"error": "Faculty is required"}), 400
    if not data.get('average_score'):
        return jsonify({"error": "Average score is required"}), 400

    faculty = FacultyEnum(data.get('faculty'))
    semester = SemesterEnum(data.get('semester'))
    average = data.get('average_score')


    scores = data.get('scores')
    # Convert the dictionary to a JSON string
    scores_json = json.dumps(scores)

    # Convert the JSON string to bytes
    scores_bytes = scores_json.encode('utf-8')

    # Base64 encode the bytes
    scores_base64 = base64.b64encode(scores_bytes).decode('utf-8')

    average_score = AverageScores.query.filter_by(user_id=current_user.user_id, semester=semester, faculty=faculty).first()

    if average_score:
        # Update existing record
        average_score.scores_base64 = scores_base64
        average_score.average_score = average
        average_score.updated_at = datetime.datetime.now()
        db.session.commit()

    else:
        # Create a new record
        average_scores = AverageScores(
            user_id=current_user.user_id,
            scores_base64=scores_base64,
            semester=semester,
            average_score=average,
            faculty=faculty,
        )
        db.session.add(average_scores)
        db.session.commit()

    return jsonify({"message": "Score saved successfully!"}), 200

@app.route('/stats', methods=['GET'])
@login_required
def stats():
    return render_template('users/stats.html')

@app.route('/statistics-data', methods=['GET'])
def statistics_data():
    # Overall Leaderboard
    overall_leaderboard = AverageScores.query \
        .with_entities(AverageScores.user_id, db.func.avg(AverageScores.average_score).label('average_score')) \
        .group_by(AverageScores.user_id) \
        .order_by(db.func.avg(AverageScores.average_score).desc()) \
        .limit(10) \
        .all()

    overall_data = [
        {
            'alias': f"User {item.user_id[:5]}***",  # Anonymize user
            'average_score': round(item.average_score, 2)
        }
        for item in overall_leaderboard
    ]

    # Subject-Wise Leaderboard
    subject_leaderboard = []
    for record in AverageScores.query.all():
        scores = json.loads(base64.b64decode(record.scores_base64).decode('utf-8'))
        for subject, score in scores.items():
            subject_leaderboard.append({
                'alias': f"User {record.user_id[:5]}***",  # Anonymize user
                'subject': subject,
                'score': score
            })

    subject_leaderboard = sorted(subject_leaderboard, key=lambda x: x['score'], reverse=True)[:10]

    # Semester Leaderboard
    semester_data = AverageScores.query \
        .with_entities(AverageScores.semester, db.func.avg(AverageScores.average_score).label('average_score')) \
        .group_by(AverageScores.semester) \
        .order_by(AverageScores.semester) \
        .all()

    semester_chart_data = {
        'labels': [f"Semester {item.semester.value}" for item in semester_data],
        'scores': [round(item.average_score, 2) for item in semester_data],
    }

    return jsonify({
        'overall': overall_data,
        'subjects': subject_leaderboard,
        'semester': semester_chart_data
    })

# L1S1
@app.route('/cs_average')
def cs_average():
    return render_template('app/semester_1/cs_average.html')

@app.route('/ce_average')
def ce_average():
    return render_template('app/semester_1/ce_average.html')

@app.route('/ge_average')
def ge_average():
    return render_template('app/semester_1/ge_average.html')

@app.route('/pe_average')
def pe_average():
    return render_template('app/semester_1/pe_average.html')

#L1S2

@app.route('/cs_average_s2')
def cs_average_s2():
    return render_template('app/semester_2/cs_average_s2.html')

@app.route('/ce_average_s2')
def ce_average_s2():
    return render_template('app/semester_2/ce_average_s2.html')

@app.route('/ge_average_s2')
def ge_average_s2():
    return render_template('app/semester_2/ge_average_s2.html')

@app.route('/pe_average_s2')
def pe_average_s2():
    return render_template('app/semester_2/pe_average_s2.html')

@app.route('/average')
def index_average():
    return render_template('app/semester_1/average_index.html')



# Route to handle JSON data submission for contact form
@app.route("/send-email", methods=["POST"])
def save_message():
    try:
        # Get JSON data from the request body
        data = request.get_json()
        app.logger.debug(f"Received JSON data: {data}")

        # Extract the fields from JSON
        name = data.get("name")
        email = data.get("email")
        message = data.get("message")

        # Validate JSON data
        if not name or not email or not message:
            app.logger.warning("Missing required fields in JSON data")
            return jsonify({"success": False, "message": "All fields are required."}), 400

        # Ensure the messages.txt file is present in the correct directory
        file_path = os.path.join(os.getcwd(), "messages.txt")

        # Save message to a text file safely
        with open(file_path, "a") as file:
            file.write(f"Name: {name}\n")
            file.write(f"Email: {email}\n")
            file.write(f"Message: {message}\n")
            file.write(f"Date: {datetime.now()}\n")
            file.write("-" * 50 + "\n")

        app.logger.info(f"Message saved successfully for {name}")

        return jsonify({"success": True, "message": "Message saved successfully"}), 200

    except Exception as e:
        app.logger.error(f"Error saving message: {e}", exc_info=True)
        return jsonify({"success": False, "message": "There was an error saving the message."}), 500
    

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=True, port=5050, host='0.0.0.0')
