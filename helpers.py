from datetime import timedelta, date
from flask import session
from model import db, Dietitian, Patient, Post



def get_current_dietitian():
    """Returns dietitian object for current dietitian_id."""

    dietitian_id = session.get("dietitian_id")
    return Dietitian.query.get(dietitian_id)


def get_current_patient():
    """Returns patient object for current patient_id."""

    patient_id = session.get("patient_id")
    return Patient.query.get(patient_id)


def get_user_type_from_session():
    """Check to see if logged in user is a dietitian or a patient"""

    if session.get("dietitian_id"):
        return "dietitian"

    if session.get("patient_id"):
        return "patient"


def check_dietitian_authorization(dietitian_id):
    """Check to see if the logged in dietitian is authorized to view page."""

    # Get the current user's dietitian_id.
    user_id = session.get("dietitian_id")

    # If correct dietitian is not logged in, show unauthorized template.
    if user_id != dietitian_id:
        return False

    return True


def check_patient_authorization(patient_id):
    """Check to see if the logged in patient is authorized to view page."""

    # Get the current user's patient_id.
    user_id = session.get("patient_id")

    # If correct patient is not logged in, show unauthorized template.
    if user_id != patient_id:
        return False

    return True


def sort_date_desc(lst):
    """Sort a list of objects with attribute time_stamp by date descending."""

    return sorted(lst, key=lambda x: x.time_stamp, reverse=True)


def alphabetize_by_lname(lst):
    """Alphabetize a list of objects by their attribute lname."""

    return sorted(lst, key=lambda x: x.lname)


def get_list_of_ratings(patient_obj, post_rating, from_date_obj, to_date_obj):
    """Return a list of dates and ratings as dictionaries."""

    dates_ratings_tuples = (db.session.query(Post.meal_time, post_rating)
                             .filter(Post.patient == patient_obj, 
                             post_rating != None, 
                             Post.meal_time.between(from_date_obj, to_date_obj))
                             .all())

    dates_ratings_dicts = []

    for meal_time, rating in dates_ratings_tuples:
        dates_ratings_dicts.append({"meal_time": meal_time.isoformat(),
                                    "rating": rating})

    return dates_ratings_dicts


def get_sundays_with_data(patient):
    """Get a list of past Sundays where the following week has ratings data."""

    dates_with_data = (db.session.query(Post.meal_time)
                         .filter(Post.patient==patient, 
                          ( (Post.hunger != None) | (Post.fullness !=None) | 
                            (Post.satisfaction != None) ))).all()

    sundays_with_data = set()

    for day, in dates_with_data:
        
        # Get the previous Sunday.
        idx = (day.date().weekday() + 1) % 7
        previous_sunday = day.date() - timedelta(idx)
        
        # If the previous Sunday is not in the set, add it.
        if previous_sunday not in sundays_with_data:
            sundays_with_data.add(previous_sunday.isoformat())

    sundays_with_data_list = list(sundays_with_data)
    sorted_data = sorted(sundays_with_data_list)
    
    return sorted_data[::-1]



