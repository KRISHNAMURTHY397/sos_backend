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
account_sid = str(environ.get("ACCOUNT_ID"))
auth_token = str(environ.get("AUTH_ID"))
twilio_phone_number = str(environ.get("TWILIO_NUM"))
destination_number = str(environ.get("SEND_NUM"))

# Database configuration
db_config = {
    'host': environ.get("DB_HOST", "localhost"),
    'user': environ.get("DB_USER", "root"),
    'password': environ.get("DB_PASS", "sarankrishna123"),
    'database': environ.get("DB_NAME", "sos_feed"),
    'port': environ.get("DB_PORT", "3306")
}

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    name = data.get('name')
    age = data.get('age')
    feedback = data.get('feedback')

    if not (name and age and feedback):
        return jsonify({"error": "All fields are required"}), 400

    try:
        print("Connecting to database...")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        print("Connected to database. Inserting data...")
        cursor.execute(
            "INSERT INTO feed (name, age, feedback) VALUES (%s, %s, %s)",
            (name, age, feedback)
        )
        conn.commit()
        cursor.close()
        conn.close()
        print("Data inserted successfully.")
        return jsonify({"message": "Feedback submitted successfully"}), 200
    except mysql.connector.Error as err:
        print("Database Error:", err)
        return jsonify({"error": "Database connection failed"}), 500

if __name__ == "__main__":
    port = int(environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
