from flask import session
from model import Dietitian, Patient


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



