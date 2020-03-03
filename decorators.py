from functools import wraps

from flask import render_template, session, request

from helpers import (check_dietitian_authorization, check_patient_authorization,
                     get_user_type_from_session, get_dietitian_and_patients_list)
from model import Patient


def dietitian_auth(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        dietitian_id = kwargs["dietitian_id"]
        if not check_dietitian_authorization(dietitian_id):
            return render_template("unauthorized.html")
        return fn(*args, **kwargs)
    return decorated_view


def patient_or_dietitian_auth(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        
        user_type = get_user_type_from_session()
        patient_id = kwargs["patient_id"]
        
        if user_type == "dietitian":
            patient = Patient.query.get(patient_id)
            
            if not patient or (patient.dietitian_id != session.get("dietitian_id")):
                return render_template("unauthorized.html")

        else:
            if not check_patient_authorization(patient_id):
                return render_template("unauthorized.html")

        return fn(*args, **kwargs)
    return decorated_view