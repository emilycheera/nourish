from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from sqlalchemy import desc

from datetime import datetime

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, Dietitian, Patient, Goal, Post, Comment


app = Flask(__name__)
app.secret_key = "b_xd3xf9095~xa68x90E^O1xd3R"

app.jinja_env.undefined = StrictUndefined



@app.route("/", methods=["GET"])
def index():
    """Homepage that shows login form."""

    ### EDIT REDIRECT WHEN ROUTE CREATED###
    if get_current_patient_id():
        return redirect(f"/dietitian/{dietitian_id}")

    if get_current_dietitian_id():
        dietitian_id = get_current_dietitian_id()
        return redirect(f"/dietitian/{dietitian_id}")


    return render_template("homepage.html")


@app.route("/", methods=["POST"])
def handle_login():
    """Login a dietitian or patient user."""

    email = request.form.get("email")
    password = request.form.get("password")
    user_type = request.form.get("user-type")

    if user_type == "patient":
        user = Patient.query.filter_by(email=email).first()
    else:
        user = Dietitian.query.filter_by(email=email).first()

    if not user:
        if user_type == "dietitian":
            flash(f"No account with {email}. Please register a new dietitian account.")
            return redirect("/")
        elif user_type == "patient":
            flash(f"No account with {email}. Contact your dietitian to create or update your account.")
            return redirect("/")

    if not user.check_password(password):
        flash("Incorrect password.")
        return redirect("/")

    if user_type == "dietitian":
        session["dietitian_id"] = user.dietitian_id
        flash("Login successful.")
        return redirect(f"/dietitian/{user.dietitian_id}")

    if user_type == "patient":
        session["patient_id"] = user.patient_id
        flash("Login successful.")
        return redirect(f"/patient/{user.patient_id}")


@app.route("/logout")
def logout():
    """Log out."""

    if get_current_dietitian_id():
        del session["dietitian_id"]
        flash("Logout successful.")

    elif get_current_patient_id():
        del session["patient_id"]
        flash("Logout successful.")
    
    return redirect("/")


@app.route('/register', methods=["GET"])
def show_dietitian_registration_form():
    """Show form for dietitian registration."""
    
    return render_template("dietitian-registration.html")


@app.route('/register', methods=["POST"])
def process_dietitian_registration():
    """Process dietitian registration."""
    
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    email = request.form.get("email")
    password = request.form.get("password")
    street_address = request.form.get("street-address")
    city = request.form.get("city")
    state = request.form.get("state")
    zipcode = request.form.get("zipcode")

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

    dietitian_id = new_dietitian.dietitian_id

    # Log in new dietitian
    session["dietitian_id"] = dietitian_id

    flash(f"Successfully registered {email}.")
    return redirect(f"/dietitian/{dietitian_id}")


@app.route("/dietitian/<int:dietitian_id>")
def show_dietitian_homepage(dietitian_id):
    """Show a dietitian's homepage."""

    if not check_dietitian_authorization(dietitian_id):
        return render_template("unauthorized.html")

    dietitian = get_current_dietitian()
    patients_list = dietitian.patients
    posts = (Post.query.filter(Patient.dietitian_id == dietitian.dietitian_id)
            .join(Patient)
            .join(Dietitian)
            .order_by(Post.post_time.desc())
            .limit(30).all())

    return render_template("dietitian-home-posts.html",
                            dietitian=dietitian,
                            patients=patients_list,
                            posts=posts)


@app.route("/dietitian/<int:dietitian_id>/<int:patient_id>")
def show_single_patient_overview(dietitian_id, patient_id):
    """Show a dietitian's view of a single patient."""

    if not check_dietitian_authorization(dietitian_id):
        return render_template("unauthorized.html")

    dietitian = get_current_dietitian()
    patients_list = dietitian.patients
    patient = Patient.query.get(patient_id)

    if not patient:
        return redirect(f"/dietitian/{dietitian_id}")

    return render_template("dietitian-home-patient-overview.html",
                            dietitian=dietitian,
                            patients=patients_list,
                            patient=patient)


@app.route("/dietitian/<int:dietitian_id>/<int:patient_id>/goals", methods=["GET"])
def show_single_patient_goals(dietitian_id, patient_id):
    """Show page where dietitian can add and view goals for a patient."""

    if not check_dietitian_authorization(dietitian_id):
        return render_template("unauthorized.html")

    dietitian = get_current_dietitian()
    patients_list = dietitian.patients
    patient = Patient.query.get(patient_id)
    current_patient_goal = patient.goals[-1]
    past_goals = patient.goals[:-1]
    

    return render_template("dietitian-home-patient-goals.html",
                            dietitian=dietitian,
                            patients=patients_list,
                            patient=patient,
                            current_goal=current_patient_goal,
                            past_goals=past_goals)

@app.route("/dietitian/<int:dietitian_id>/<int:patient_id>/goals", methods=["POST"])
def add_new_patient_goal(dietitian_id, patient_id):
    """Process new goals form."""

    time_stamp = datetime.now()
    goal_body = request.form.get("goal_body")

    new_goal = Goal(patient_id=patient_id,
                    time_stamp=time_stamp,
                    goal_body=goal_body)

    db.session.add(new_goal)
    db.session.commit()

    flash("Successfully added goal.")
    return redirect(f"/dietitian/{dietitian_id}/{patient_id}/goals")



@app.route("/dietitian/<int:dietitian_id>/<int:patient_id>/posts")
def show_single_patient_posts(dietitian_id, patient_id):
    """Show a dietitian's view of a single patient's posts."""

    if not check_dietitian_authorization(dietitian_id):
        return render_template("unauthorized.html")

    dietitian = get_current_dietitian()
    patients_list = dietitian.patients
    patient = Patient.query.get(patient_id)
    patient_posts = patient.posts

    return render_template("dietitian-home-patient-posts.html",
                            dietitian=dietitian,
                            patients=patients_list,
                            patient=patient,
                            posts=patient_posts)


def get_current_dietitian_id():
    """Returns current dietitian id."""

    return session.get("dietitian_id")


def get_current_dietitian():
    """Returns dietitian object for current dietitian_id."""

    return Dietitian.query.get(get_current_dietitian_id())


def get_current_patient_id():
    """Returns current patient id."""

    return session.get("patient_id")


def get_current_patient():
    """Returns patient object for current patient_id."""

    return Patient.query.get(get_current_patient_id())


def check_dietitian_authorization(dietitian_id):
    """Check to see if the logged in dietitian is authorized to view page."""

    # Get the current user's dietitian_id.
    user_id = get_current_dietitian_id()

    # If correct dietitian is not logged in, show unauthorized template.
    if user_id != dietitian_id:
        return False

    return True


# Add jinja datetime filter to format datetime in patient posts
def datetimeformat(value, format='%b %-d, %Y at %-I:%M %p'):
    return value.strftime(format)

app.jinja_env.filters['datetime'] = datetimeformat



if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
