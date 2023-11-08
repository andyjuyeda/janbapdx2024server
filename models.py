from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import enum
from main import db, app


class EventName(enum.Enum):
    CLASSIC = "Classic"
    MIXED = "Mixed"
    TEAM = "Team"
    DOUBLES = "Doubles"
    SINGLES = "Singles"


class Gender(enum.Enum):
    M = "M"
    F = "F"


class Bowler(db.Model):
    __tablename__ = "bowlers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    gender = db.Column(db.Enum(Gender), nullable=False)
    average = db.Column(db.Integer, nullable=False)
    is_senior = db.Column(db.Boolean, default=False)
    is_vet = db.Column(db.Boolean, default=False)
    is_in_all_events = db.Column(db.Boolean, default=False)
    is_in_senior_all_events = db.Column(db.Boolean, default=False)

    # Relationships
    events = db.relationship(
        "Event", secondary="bowler_events", back_populates="bowlers"
    )


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.Enum(Gender), nullable=True)
    event_name = db.Column(db.Enum(EventName), nullable=False)
    division = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=True)

    # Relationships
    bowlers = db.relationship(
        "Bowler", secondary="bowler_events", back_populates="events"
    )


class BowlerEvent(db.Model):
    __tablename__ = "bowler_events"

    id = db.Column(db.Integer, primary_key=True)
    bowler_id = db.Column(db.Integer, db.ForeignKey("bowlers.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)


class EventData(db.Model):
    __tablename__ = "event_data"

    id = db.Column(db.Integer, primary_key=True)
    bowler_id = db.Column(db.Integer, db.ForeignKey("bowlers.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    score = db.Column(db.Integer, nullable=True)
    lane = db.Column(db.Integer, nullable=True)

    bowler = db.relationship("Bowler", backref=db.backref("event_data", lazy=True))
    event = db.relationship("Event", backref=db.backref("event_data", lazy=True))


# * Uncomment the line below if you're running this code for the first time to create the tables in your database
# with app.app_context():
#     db.create_all()
