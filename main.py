from flask import Flask, request, jsonify
from twilio.rest import Client
import geocoder
from flask_cors import CORS
from os import environ
from dotenv import load_dotenv
import mysql.connector  # Import MySQL connector for database operations

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for the Flask app

# Twilio settings
account_sid = str(environ.get("ACCOUNT_ID"))  # Your Twilio Account SID
auth_token = str(environ.get("AUTH_ID"))      # Your Twilio Auth Token
twilio_phone_number = str(environ.get("TWILIO_NUM"))
destination_number = str(environ.get("SEND_NUM"))  # Twilio phone number

# Database configuration
db_config = {
    'host': "localhost",
    'user': "root",
    'password': "sarankrishna123",
    'database': "sos_feed",
    'port': 3306
}

# Function to send SMS via Twilio
def send_sms(location, message):
    client = Client(account_sid, auth_token)
    try:
        client.messages.create(
            body=f"Emergency Alert!\nLocation: {location}\nMessage: {message}",
            from_=twilio_phone_number,
            to=destination_number
        )
        return True
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        return False

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/send_sos', methods=['POST'])
def send_sos():
    data = request.json
    message = data.get('message', 'Emergency SOS')  # Default message if not provided

    # Get the location (use GPS data from Flutter, fallback to IP geolocation for testing)
    location = data.get('location', None)
    if not location:
        g = geocoder.ip('me')  # Replace this with actual GPS location from the frontend
        location = g.latlng if g else 'Unknown Location'

    if send_sms(location, message):
        return jsonify({'status': 'success', 'message': 'SOS sent successfully!'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send SOS'}), 500

# New endpoint to receive and store feedback data
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    name = data.get('name')
    age = data.get('age')
    feedback = data.get('feedback')

    if not all([name, age, feedback]):
        return jsonify({'status': 'error', 'message': 'Please fill in all fields'}), 400

    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert feedback data into the database
        cursor.execute("INSERT INTO feed (name, age, feedback) VALUES (%s, %s, %s)", (name, age, feedback))
        conn.commit()

        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Feedback submitted successfully'}), 200
    except mysql.connector.Error as err:
        print("Database Error:", err)
        return jsonify({'status': 'error', 'message': 'Failed to submit feedback'}), 500

if __name__ == "__main__":
    port = int(environ.get("PORT", 8080))  # Default to 8080 if PORT not set
    app.run(host="0.0.0.0", port=port)
