from functools import wraps

from flask import render_template, session, request, redirect

from users import (check_dietitian_authorization, check_patient_authorization,
                   get_user_type_from_session, get_dietitian_and_patients_list,
                   get_current_dietitian, get_current_patient)
from model import Patient


def dietitian_auth(fn):
    """Check if a logged in dietitian is authorized to view the current page."""
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        user_type = get_user_type_from_session()
        if user_type == "patient":
            patient = get_current_patient()
            return render_template("unauthorized.html", patient=patient)

        dietitian_id = kwargs["dietitian_id"]
        if not check_dietitian_authorization(dietitian_id):
            dietitian = get_current_dietitian()
            return render_template("unauthorized.html", dietitian=dietitian)
                
        return fn(*args, **kwargs)
    return decorated_view


def dietitians_only(fn): 
    """Check if a dietitian is logged in to the session."""   
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        user_type = get_user_type_from_session()
        if user_type != "dietitian":
            patient = get_current_patient()
            return render_template("unauthorized.html", patient=patient)
        return fn(*args, **kwargs)
    return decorated_view


def patient_or_dietitian_auth(fn):
    """Check if a patient or dietitian is authorized to view the page."""
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        
        user_type = get_user_type_from_session()
        patient_id = kwargs["patient_id"]
        
        if user_type == "dietitian":
            patient = Patient.query.get(patient_id)
            dietitian = get_current_dietitian()
            
            if not patient or (patient.dietitian_id != session.get("dietitian_id")):
                return render_template("unauthorized.html", dietitian=dietitian)

        else:
            if not check_patient_authorization(patient_id):
                patient = get_current_patient()
                return render_template("unauthorized.html", patient=patient)

        return fn(*args, **kwargs)
    return decorated_view


def patient_belongs_to_dietitian(fn):
    """Check that a dietitian is authorized to view a certain patient's page."""
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        
        user_type = get_user_type_from_session()

        if user_type == "patient":
            patient = get_current_patient()
            return render_template("unauthorized.html", patient=patient)

        patient_id = kwargs["patient_id"]
        patient = Patient.query.get(patient_id)

        if not patient or (patient.dietitian_id != session.get("dietitian_id")):
            dietitian = get_current_dietitian()
            return render_template("unauthorized.html", dietitian=dietitian)

        return fn(*args, **kwargs)
    return decorated_view


def patient_auth(fn):
    """Check that the page is being visited by the logged in patient."""
    @wraps(fn)
    def decorated_view(*args, **kwargs):

        user_type = get_user_type_from_session()
        if user_type == "dietitian":
            dietitian = get_current_dietitian()
            return render_template("unauthorized.html", dietitian=dietitian)
        
        patient_id = kwargs["patient_id"]
        if not check_patient_authorization(patient_id):
            patient = get_current_patient()
            return render_template("unauthorized.html", patient=patient)

        return fn(*args, **kwargs)
    return decorated_view


def dietitian_redirect(fn):
    """If user is a dietitian, redirect to patient's account information."""
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        user_type = get_user_type_from_session()
        if user_type == "dietitian":
            patient_id = kwargs["patient_id"]
            return redirect(f"/patient/{patient_id}/account")
        return fn(*args, **kwargs)
    return decorated_view



