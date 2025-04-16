from flask import Flask, render_template, request, jsonify, Response, send_from_directory
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



@app.route('/sw.js')
def serve_sw():
    try:
        # Define the path to the service worker file
        file_path = os.path.join(app.root_path, 'sw.js')

        # Check if the file exists
        if not os.path.exists(file_path):
            return Response("Service worker not found.", status=404)

        # Serve the file with the correct MIME type
        return send_from_directory(app.root_path, 'sw.js', mimetype='application/javascript')
    except Exception as e:
        return Response(f"An error occurred: {str(e)}", status=500)

# L1S1
@app.route('/cs_average')
def cs_average():
    return render_template('app/cs_average.html')

@app.route('/ce_average')
def ce_average():
    return render_template('app/ce_average.html')

@app.route('/ge_average')
def ge_average():
    return render_template('app/ge_average.html')

@app.route('/pe_average')
def pe_average():
    return render_template('app/pe_average.html')

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
    return render_template('app/average_index.html')



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
