from flask import Flask, request, jsonify
from twilio.rest import Client
import geocoder
from flask_cors import CORS
import mysql.connector
from os import environ
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for the Flask app

# Twilio settings
account_sid = str(environ.get("ACCOUNT_ID"))  # Your Twilio Account SID
auth_token = str(environ.get("AUTH_ID"))       # Your Twilio Auth Token
twilio_phone_number = str(environ.get("TWILIO_NUM"))
destination_number = str(environ.get("SEND_NUM"))  # Destination phone number

# Database configuration
db_config = {
    'host': environ.get("DB_HOST", "localhost"),
    'user': environ.get("DB_USER", "root"),
    'password': environ.get("DB_PASS", "sarankrishna123"),
    'database': environ.get("DB_NAME", "sos_feed"),
    'port': environ.get("DB_PORT", "3306")
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
    if not location:  # If location isn't sent, fallback to approximate IP geolocation
        g = geocoder.ip('me')
        location = g.latlng if g else 'Unknown Location'

    # Send the SMS message
    if send_sms(location, message):
        return jsonify({'status': 'success', 'message': 'SOS sent successfully!'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send SOS'}), 500

# Route to handle feedback submission
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    name = data.get('name')
    age = data.get('age')
    feedback = data.get('feedback')

    if not (name and age and feedback):
        return jsonify({"error": "All fields are required"}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO feed (name, age, feedback) VALUES (%s, %s, %s)",
            (name, age, feedback)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Feedback submitted successfully"}), 200
    except mysql.connector.Error as err:
        print("Error:", err)
        return jsonify({"error": "Database connection failed"}), 500

if __name__ == "__main__":
    port = int(environ.get("PORT", 8080))  # Default to 8080 if PORT not set
    app.run(host="0.0.0.0", port=port)
