from flask import session
from helpers import alphabetize_by_lname
from model import db, Dietitian, Patient


def create_new_dietitian_account(form_data):
    """Add a dietitian to the database."""

    fname = form_data.get("fname")
    lname = form_data.get("lname")
    email = form_data.get("email")
    password = form_data.get("password")
    street_address = form_data.get("street-address")
    city = form_data.get("city")
    state = form_data.get("state")
    zipcode = form_data.get("zipcode")

    new_dietitian = Dietitian(fname=fname,
                              lname=lname,
                              email=email,
                              street_address=street_address,
                              city=city,
                              state=state,
                              zipcode=zipcode)

    new_dietitian.set_password(password)

    db.session.add(new_dietitian)
    db.session.commit()

    return new_dietitian.dietitian_id


def update_dietitian_account(dietitian_id, form_data):
    """Update a dietitian in the database."""

    dietitian = Dietitian.query.get(dietitian_id)

    dietitian.fname = form_data.get("fname")
    dietitian.lname = form_data.get("lname")
    dietitian.email = form_data.get("email")
    dietitian.street_address = form_data.get("street-address")
    dietitian.city = form_data.get("city")
    dietitian.state = form_data.get("state")
    dietitian.zipcode = form_data.get("zipcode")

    db.session.add(dietitian)
    db.session.commit()

    return "Success"


def create_new_patient_account(form_data):
    """Add a patient to the database."""

    email = form_data.get("email")
    dietitian_id = form_data.get("dietitian_id")
    fname = form_data.get("fname")
    lname = form_data.get("lname")
    password = form_data.get("password")
    street_address = form_data.get("street-address")
    city = form_data.get("city")
    state = form_data.get("state")
    zipcode = form_data.get("zipcode")
    phone = form_data.get("phone")
    birthdate = form_data.get("birthdate")

    new_patient = Patient(dietitian_id=dietitian_id,
                          fname=fname,
                          lname=lname,
                          email=email,
                          street_address=street_address,
                          city=city,
                          state=state,
                          zipcode=zipcode,
                          phone=phone,
                          birthdate=birthdate)

    new_patient.set_password(password)

    db.session.add(new_patient)
    db.session.commit()

    return new_patient.patient_id


def update_patient_account(patient_id, form_data):

    patient = Patient.query.get(patient_id)

    patient.fname = form_data.get("fname")
    patient.lname = form_data.get("lname")
    patient.email = form_data.get("email")
    patient.street_address = form_data.get("street-address")
    patient.city = form_data.get("city")
    patient.state = form_data.get("state")
    patient.zipcode = form_data.get("zipcode")
    patient.phone = form_data.get("phone")
    patient.birthdate = form_data.get("birthdate")

    db.session.add(patient)
    db.session.commit()

    return "Success"


def reset_password(password, user_object):
    """Reset a user's password in the database."""

    user_object.set_password(password)

    db.session.add(user_object)
    db.session.commit()

    return "Success"


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


def get_dietitian_and_patients_list():
    """Return a dictionary with the dietitian and sorted list of patients."""

    dietitian = get_current_dietitian()
    patients_list = dietitian.patients
    sorted_patients = alphabetize_by_lname(patients_list)

    diet_and_pats = {"dietitian": dietitian,
                     "sorted_patients": sorted_patients}

    return diet_and_pats



