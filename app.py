from flask import Flask, render_template, request, jsonify
import logging
from datetime import datetime
import os
import subprocess
from bot import Bot
from dotenv import load_dotenv


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder='static')

# Configure logging for better error reporting
logging.basicConfig(level=logging.DEBUG)

# Route to render the index page
@app.route('/')
def index():
    return render_template('app/index.html')

# Route to render the CV without CSS
@app.route('/cvnocss')
def cvnocss():
    return render_template('pw1/cvnocss.html')

# Route to render the CV with CSS
@app.route('/cvwithcss')
def cvwithcss():
    return render_template('pw1/cvwithcss.html')

@app.route('/pw2')
def pw2():
    return render_template('pw2/pw2.html')

@app.route('/pw2tail')
def pw2tail():
    return render_template('pw2/pw2_tail.html')


@app.route('/pw3')
def pw3():
    return render_template('pw3/pw3.html')

@app.route('/pw5')
def pw5():
    return render_template('pw5/pw5.html')


@app.route('/pw6')
def pw6():
    
    return render_template('pw6/home.html')

@app.route('/pw6/ex1')
def pw6_ex1():
    return render_template('pw6/ex1.html')

@app.route('/pw6/ex2')
def pw6_ex2():
    return render_template('pw6/ex2.html')

@app.route('/pw6/ex3')
def pw6_ex3():
    return render_template('pw6/ex3.html')
# Home Work Project

@app.route('/step_1e')
def step_1e():
    return render_template('hw/step_1e.html')

@app.route('/step_2a')
def step_2a():
    return render_template('hw/step_2a.html')

@app.route('/step_3a')
def step_3a():
    return render_template('hw/step_3a.html')

@app.route('/step_3')
def step_3():
    return render_template('hw/step_3.html')

#AI

@app.route('/submit', methods=['POST'])
def submit():
    bot = Bot(api_key=OPENAI_API_KEY)

    user_input  = request.json.get('user_input')

    answer = bot.response(user_input)
    return answer



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
    
# Route to render the admin console
@app.route('/console-admin/<password_slug>')
def console_admin(password_slug):

    with open('password.txt', 'r') as file:
        password = file.read().strip()
    if password_slug == password:

        return render_template('app/console.html')  
    else:
        return render_template('app/index.html')
    

# Route to handle JSON data submission for terminal commands
@app.route("/execute-command", methods=["POST"])
def execute_command():
    try:
        # Get the command from the request
        data = request.get_json()
        command = data.get("command")

        if not command:
            return jsonify({"success": False, "message": "No command provided"}), 400

        # Execute the command using subprocess
        app.logger.debug(f"Executing command: {command}")
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            output = result.stdout
            app.logger.info(f"Command executed successfully: {output}")
        else:
            output = result.stderr
            app.logger.error(f"Command execution failed: {output}")

        return jsonify({"success": True, "output": output}), 200

    except Exception as e:
        app.logger.error(f"Error executing command: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Error executing the command"}), 500


if __name__ == '__main__':

    app.run(debug=True, port=5050)
