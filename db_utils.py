from models import Bowler, Event, EventData, EventName, Gender
from faker import Faker
from random import choice, randint, getrandbits
from main import app, db
from pprint import pprint


def upsert_bowler(
    name,
    gender,
    average,
    is_senior=False,
    is_vet=False,
    is_in_all_events=False,
    is_in_senior_all_events=False,
):
    with app.app_context():
        # Try to find an existing bowler with the same name
        existing_bowler = Bowler.query.filter_by(name=name).first()

        if existing_bowler:
            # Update the existing bowler's attributes
            existing_bowler.gender = gender
            existing_bowler.average = average
            existing_bowler.is_senior = is_senior
            existing_bowler.is_vet = is_vet
            existing_bowler.is_in_all_events = is_in_all_events
            existing_bowler.is_in_senior_all_events = is_in_senior_all_events
        else:
            # Create a new Bowler object
            new_bowler = Bowler(
                name=name,
                gender=gender,
                average=average,
                is_senior=is_senior,
                is_vet=is_vet,
                is_in_all_events=is_in_all_events,
                is_in_senior_all_events=is_in_senior_all_events,
            )

            # Add the new bowler to the database session
            db.session.add(new_bowler)

        # Commit the session to save changes
        db.session.commit()


# * Create fake bowlers for testing
# def fake_bowlers(n):  # n = number of bowlers to create
#     fake = Faker()
#     with app.app_context():
#         for i in range(n):
#             bowler_data = {
#                 "name": fake.name(),
#                 "gender": choice(["M", "F"]),
#                 "average": randint(130, 250),
#                 "is_senior": bool(getrandbits(1)),
#                 "is_vet": bool(getrandbits(1)),
#                 "is_in_all_events": bool(getrandbits(1)),
#                 "is_in_senior_all_events": bool(getrandbits(1)),
#             }
#             bowler = Bowler(**bowler_data)
#             db.session.add(bowler)
#         db.session.commit()

# fake_bowlers(200)


# * Return list of all bowlers
def get_all_bowlers():
    with app.app_context():
        bowlers = [
            {
                "id": bowler.id,
                "name": bowler.name,
                "gender": bowler.gender.value,
                "average": bowler.average,
            }
            for bowler in Bowler.query.all()
        ]
    return bowlers

def get_bowler_info(bowler_id):
    with app.app_context():
        bowler = Bowler.query.get(bowler_id)
        if bowler:
            return {
                "id": bowler.id,
                "name": bowler.name,
                "gender": bowler.gender.value,
                "average": bowler.average,
                "is_senior": bowler.is_senior,
                "is_vet": bowler.is_vet,
                "is_in_all_events": bowler.is_in_all_events,
                "is_in_senior_all_events": bowler.is_in_senior_all_events,
            }


# * Initialize events in database
# def add_events():
#     events = [EventName.CLASSIC, EventName.MIXED, EventName.TEAM, EventName.DOUBLES, EventName.SINGLES]
#     genders = [Gender.M, Gender.F]
#     with app.app_context():
#         for event in events:
#             for i in range(1, 7):
#                 if event == EventName.MIXED:
#                     new_event = Event(
#                         gender=None, event_name=event, division=i
#                     )
#                     db.session.add(new_event)
#                 else:
#                     for gender in genders:
#                         new_event = Event(
#                             gender=gender, event_name=event, division=i
#                         )
#                         db.session.add(new_event)

#         db.session.commit()

# add_events()


def add_bowler_to_event(bowler_name, event_name, division, lane):
    """
    Add a bowler to an event.

    This function looks up the bowler and event records in the database, creates a new EventData record
    linking the bowler to the event, and commits the new record to the database.

    Parameters:
    bowler_name (str): The name of the bowler to add.
    event_name (EventName): The name of the event to add the bowler to.
    division (int): The division of the event.
    lane (int): The lane assigned to the bowler for this event.

    Raises:
    Exception: If no bowler is found with the given name, or no event is found with the given name and division.
    """
    with app.app_context():
        # Find the bowler record
        bowler = Bowler.query.filter_by(name=bowler_name).first()
        if not bowler:
            raise Exception(f"No bowler found with name {bowler_name}")

        if event_name == EventName.MIXED:
            event = Event.query.filter_by(
                event_name=event_name, division=division
            ).first()
        else:
            # Find the event record
            event = Event.query.filter_by(
                gender=bowler.gender, event_name=event_name, division=division
            ).first()

        if not event:
            raise Exception(
                f"No event found with name {event_name} and division {division}"
            )

        # Create a new EventData record for the bowler and event
        new_event_data = EventData(bowler_id=bowler.id, event_id=event.id, lane=lane)
        db.session.add(new_event_data)

        db.session.commit()


def get_bowlers_in_event(event: str, divisions: list = None, gender: str = None):
    """
    Query the database to get bowlers in a specific event and optionally filtered by divisions and gender.

    Parameters:
    event (str): The event name as a string. Must match one of the values in the EventName enum (case-insensitive).
    divisions (list, optional): The division numbers as a list of ints.
    gender (str, optional): The gender as a string. Must match one of the values in the Gender enum (case-insensitive).
                             If not specified, the function will return bowlers of all genders.

    Returns:
    list: A sorted list of dictionaries, where each dictionary contains a bowler's details. The list is sorted by lane number.
    """

    event = EventName[event.upper()]  # Convert string to EventName enum
    gender = (
        Gender[gender.upper()] if gender else None
    )  # Convert string to Gender enum if it's not None

    with app.app_context():
        query = (
            db.session.query(Bowler, EventData, Event)
            .select_from(EventData)
            .join(Bowler)
            .join(Event)
            .filter(Event.event_name == event)
        )

        # Add division filter if divisions are specified
        if divisions:
            query = query.filter(Event.division.in_(divisions))

        # Add gender filter if gender is specified
        if gender:
            query = query.filter(Event.gender == gender)

        bowlers_in_event = query.all()

        # Create a list of dictionaries {"name": name, "average": average, "lane": lane, "division": division}
        bowlers = [
            {
                "bowler_id": bowler.id,
                "instance_id": event_data.id,
                "name": bowler.name,
                "gender": str(bowler.gender),
                "average": bowler.average,
                "lane": event_data.lane,
                "division": event.division,
            }
            for bowler, event_data, event in bowlers_in_event
        ]

        # Sort the list of dictionaries by lane number
        bowlers = sorted(bowlers, key=lambda x: x["lane"])

        return bowlers


# pprint(get_bowlers_in_event(event="team", divisions=[1], gender="m"))
