from flask import Flask, render_template, request, jsonify
import logging
from datetime import datetime
import os

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


if __name__ == '__main__':

    app.run(debug=True)
