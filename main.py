from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import enum
from faker import Faker
from random import randint, choice, getrandbits
from flask_cors import CORS
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
db = SQLAlchemy(app)

app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
mail = Mail(app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/api/bowlers")
def show_bowlers():
    from db_utils import get_all_bowlers, get_bowler_info

    query = request.args.get("id", default="all", type=str)

    if query == "all":
        return jsonify(get_all_bowlers())
    else:
        return jsonify(get_bowler_info(int(query)))


@app.route("/api/event")
def show_event_data():
    from db_utils import get_bowlers_in_event

    # Get the event, divisions, and gender from the query parameters
    event = request.args.get("event")
    divisions = request.args.getlist("div")  # Allows multiple "div" parameters
    gender = request.args.get("gender")

    # Convert divisions to integers if provided
    if divisions:
        divisions = [int(division) for division in divisions]

    # Call the function with the provided parameters
    bowlers = get_bowlers_in_event(event=event, divisions=divisions, gender=gender)

    return jsonify(bowlers)


@app.route("/api/mail", methods=["POST"])
def send_mail():
    data = request.get_json()  # Get data as JSON
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    subject = data.get("subject")
    message = data.get("message")

    msg = Message(
        sender=email,
        recipients=["andyjuyeda2@gmail.com"],  # Replace with your email
        body=f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}",
        subject=subject,
    )

    try:
        mail.send(msg)
        return jsonify({"success": True, "message": "Email sent successfully"}), 200
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
