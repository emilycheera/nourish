from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from werkzeug.utils import secure_filename
from sqlalchemy import desc

from datetime import datetime
import os

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, Dietitian, Patient, Goal, Post, Comment


app = Flask(__name__)
app.secret_key = "b_xd3xf9095~xa68x90E^O1xd3R"

UPLOAD_FOLDER = "static/images/uploads/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

app.jinja_env.undefined = StrictUndefined



@app.route("/", methods=["GET"])
def index():
    """Homepage that shows login form."""

    patient_id = session.get("patient_id")
    dietitian_id = session.get("dietitian_id")

    if patient_id:
        return redirect(f"/patient/{patient_id}")

    if dietitian_id:
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

    if session.get("dietitian_id"):
        del session["dietitian_id"]
        flash("Logout successful.")

    elif session.get("patient_id"):
        del session["patient_id"]
        flash("Logout successful.")
    
    return redirect("/")


########################   DIETITIAN ROUTES   ########################

@app.route("/register", methods=["GET"])
def show_dietitian_registration_form():
    """Show form for dietitian registration."""
    
    return render_template("dietitian-registration.html")


@app.route("/register", methods=["POST"])
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


@app.route("/dietitian/<int:dietitian_id>/account")
def show_dietitian_account(dietitian_id):
    """Show a dietitian their account information"""

    if not check_dietitian_authorization(dietitian_id):
        return render_template("unauthorized.html")

    dietitian = get_current_dietitian()
    patients_list = dietitian.patients

    return render_template("dietitian-account.html",
                            dietitian=dietitian,
                            patients=patients_list)


@app.route("/dietitian/<int:dietitian_id>/edit", methods=["GET"])
def view_edit_dietitian_information(dietitian_id):
    """Edit a dietitian's account information."""

    if not check_dietitian_authorization(dietitian_id):
        return render_template("unauthorized.html")

    dietitian = get_current_dietitian()
    patients_list = dietitian.patients

    return render_template("dietitian-account-edit.html",
                            dietitian=dietitian,
                            patients=patients_list)



@app.route("/dietitian/<int:dietitian_id>/edit", methods=["POST"])
def edit_dietitian_information(dietitian_id):
    """Process edit of a dietitian's account information."""

    dietitian = get_current_dietitian()

    dietitian.fname = request.form.get("fname")
    dietitian.lname = request.form.get("lname")
    dietitian.email = request.form.get("email")
    dietitian.street_address = request.form.get("street-address")
    dietitian.city = request.form.get("city")
    dietitian.state = request.form.get("state")
    dietitian.zipcode = request.form.get("zipcode")

    db.session.add(dietitian)
    db.session.commit()

    return redirect(f"/dietitian/{dietitian_id}/account")


@app.route("/dietitian/<int:dietitian_id>/reset-password", methods=["GET"])
def view_reset_dietitian_password_form(dietitian_id):
    """Reset a dietitian's password."""

    if not check_dietitian_authorization(dietitian_id):
        return render_template("unauthorized.html")

    dietitian = get_current_dietitian()
    patients_list = dietitian.patients

    return render_template("dietitian-resetpw.html",
                            dietitian=dietitian,
                            patients=patients_list)


@app.route("/dietitian/<int:dietitian_id>/reset-password", methods=["POST"])
def reset_dietitian_password(dietitian_id):
    """Process reset of a dietitian's password."""

    dietitian = get_current_dietitian()

    password = request.form.get("password")

    dietitian.set_password(password)

    db.session.add(dietitian)
    db.session.commit()
    
    flash("Password successfully reset.")
    return redirect(f"/dietitian/{dietitian_id}/account")


@app.route("/dietitian/<int:dietitian_id>/new-patient", methods=["GET"])
def show_patient_registration_form(dietitian_id):
    """Show form for new patient registration."""
    
    if not check_dietitian_authorization(dietitian_id):
        return render_template("unauthorized.html")

    dietitian = get_current_dietitian()
    patients_list = dietitian.patients

    return render_template("patient-registration.html",
                            dietitian=dietitian,
                            patients=patients_list)


@app.route("/dietitian/<int:dietitian_id>/new-patient", methods=["POST"])
def process_patient_registration(dietitian_id):
    """Process new patient registration."""

    fname = request.form.get("fname")
    lname = request.form.get("lname")
    email = request.form.get("email")
    password = request.form.get("password")
    street_address = request.form.get("street-address")
    city = request.form.get("city")
    state = request.form.get("state")
    zipcode = request.form.get("zipcode")
    phone = request.form.get("phone")
    birthdate = request.form.get("birthdate")

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

    patient_id = new_patient.patient_id

    flash(f"Successfully registered new patient {fname} {lname}.")
    return redirect(f"/dietitian/{dietitian_id}/{patient_id}")


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


@app.route("/dietitian/<int:dietitian_id>/<int:patient_id>/edit")
def view_edit_patient_information_form(dietitian_id, patient_id):
    """Edit a patient's basic information as a dietitian."""

    if not check_dietitian_authorization(dietitian_id):
        return render_template("unauthorized.html")

    dietitian = get_current_dietitian()
    patients_list = dietitian.patients
    patient = Patient.query.get(patient_id)

    if not patient:
        return redirect(f"/dietitian/{dietitian_id}")

    return render_template("dietitian-home-patient-edit.html",
                            dietitian=dietitian,
                            patients=patients_list,
                            patient=patient)


@app.route("/dietitian/<int:dietitian_id>/<int:patient_id>/edit", methods=["POST"])
def edit_single_patient_information(dietitian_id, patient_id):
    """Process edit of a single patient's basic information."""

    patient = Patient.query.get(patient_id)

    patient.fname = request.form.get("fname")
    patient.lname = request.form.get("lname")
    patient.email = request.form.get("email")
    patient.street_address = request.form.get("street-address")
    patient.city = request.form.get("city")
    patient.state = request.form.get("state")
    patient.zipcode = request.form.get("zipcode")
    patient.phone = request.form.get("phone")
    patient.birthdate = request.form.get("birthdate")

    db.session.add(patient)
    db.session.commit()

    return redirect(f"/dietitian/{dietitian_id}/{patient_id}")


@app.route("/dietitian/<int:dietitian_id>/<int:patient_id>/reset-password", methods=["GET"])
def view_dietitian_reset_patient_password_form(dietitian_id, patient_id):
    """Reset a patient's password as a dietitian."""

    if not check_dietitian_authorization(dietitian_id):
        return render_template("unauthorized.html")

    dietitian = get_current_dietitian()
    patients_list = dietitian.patients
    patient = Patient.query.get(patient_id)

    if not patient:
        return redirect(f"/dietitian/{dietitian_id}")

    return render_template("dietitian-home-patient-resetpw.html",
                            dietitian=dietitian,
                            patients=patients_list,
                            patient=patient)


@app.route("/dietitian/<int:dietitian_id>/<int:patient_id>/reset-password", methods=["POST"])
def dietitian_reset_patient_password(dietitian_id, patient_id):
    """Process reset of a patient's password as a dietitian."""

    patient = Patient.query.get(patient_id)

    password = request.form.get("password")

    patient.set_password(password)

    db.session.add(patient)
    db.session.commit()

    flash("Password successfully reset.")
    return redirect(f"/dietitian/{dietitian_id}/{patient_id}")


@app.route("/dietitian/<int:dietitian_id>/<int:patient_id>/goals", methods=["GET"])
def show_single_patient_goals(dietitian_id, patient_id):
    """Show page where dietitian can add and view goals for a patient."""

    if not check_dietitian_authorization(dietitian_id):
        return render_template("unauthorized.html")

    dietitian = get_current_dietitian()
    patients_list = dietitian.patients
    patient = Patient.query.get(patient_id)

    if not patient:
        return redirect(f"/dietitian/{dietitian_id}")

    if patient.goals:
        current_patient_goal = patient.goals[-1]
        past_goals = patient.goals[:-1]
        past_goals.reverse()
    else: 
        current_patient_goal = None
        past_goals = None
    

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
    goal_body = request.form.get("goal-body")

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

    if not patient:
        return redirect(f"/dietitian/{dietitian_id}")

    patient_posts = patient.posts
    patient_posts.reverse()

    return render_template("dietitian-home-patient-posts.html",
                            dietitian=dietitian,
                            patients=patients_list,
                            patient=patient,
                            posts=patient_posts)


@app.route("/dietitian/<int:dietitian_id>/<int:post_id>", methods=["POST"])
def add_post_comment_dietitian_homepage(dietitian_id, post_id):
    """Add a comment to a post on the dietitian's homepage."""

    time_stamp = datetime.now()
    comment_body = request.form.get("comment")

    new_comment = Comment(post_id=post_id,
                          time_stamp=time_stamp,
                          comment_body=comment_body)

    db.session.add(new_comment)
    db.session.commit()

    return redirect(f"/dietitian/{dietitian_id}")


@app.route("/dietitian/<int:dietitian_id>/<int:patient_id>/posts/<int:post_id>", methods=["POST"])
def add_post_comment_single_patient_page(dietitian_id, patient_id, post_id):
    """Add a comment to a post on a single patient's page."""

    time_stamp = datetime.now()
    comment_body = request.form.get("comment")

    new_comment = Comment(post_id=post_id,
                          time_stamp=time_stamp,
                          comment_body=comment_body)

    db.session.add(new_comment)
    db.session.commit()

    return redirect(f"/dietitian/{dietitian_id}/{patient_id}/posts")


########################   PATIENT ROUTES   ########################

@app.route("/patient/<int:patient_id>")
def show_patient_homepage(patient_id):
    """Show a patient's homepage."""

    if not check_patient_authorization(patient_id):
        return render_template("unauthorized.html")

    patient = get_current_patient()
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M")

    if patient.goals:
        current_goal = patient.goals[-1]
    else: 
        current_goal = None

    return render_template("patient-home-main.html",
                            patient=patient,
                            goal=current_goal,
                            current_time=current_time)


@app.route("/patient/<int:patient_id>/new-post", methods=["POST"])
def add_new_patient_post(patient_id):
    """Add a new patient post from patient's homepage."""

    if request.files:
        file = request.files.get("meal-image")

    if not allowed_image(file.filename):
        flash("Only .png, .jpg, or .jpeg images are accepted.")
        return redirect(f"/patient/{patient_id}")

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img_path = f"/static/images/uploads/{filename}"

    post_time = datetime.now()
    meal_time = request.form.get("meal-time")
    meal_setting = request.form.get("meal-setting")
    TEB = request.form.get("TEB")
    hunger = request.form.get("hunger")
    fullness = request.form.get("fullness")
    satisfaction = request.form.get("satisfaction")
    meal_notes = request.form.get("meal-notes")

    new_post = Post(patient_id=patient_id,
                    post_time=post_time,
                    meal_time=meal_time,
                    TEB=TEB,
                    meal_setting=meal_setting)

    # Save optional fields if completed in form.
    if img_path:
        new_post.img_path = img_path

    if hunger:
        new_post.hunger = hunger

    if fullness:
        new_post.fullness = fullness

    if satisfaction:
        new_post.satisfaction = satisfaction

    if meal_notes:
        new_post.meal_notes = meal_notes

    
    db.session.add(new_post)
    db.session.commit()

    flash("Post added successfully.")
    return redirect(f"/patient/{patient_id}")


@app.route("/patient/<int:patient_id>/posts")
def view_all_posts(patient_id):
    """Show a patient all of their past posts."""

    if not check_patient_authorization(patient_id):
        return render_template("unauthorized.html")

    patient = get_current_patient()

    posts = patient.posts
    posts.reverse()

    return render_template("patient-posts.html",
                            patient=patient,
                            posts=posts)


@app.route("/patient/<int:patient_id>/goals")
def view_all_goals(patient_id):
    """Show a patient all of their past goals."""

    if not check_patient_authorization(patient_id):
        return render_template("unauthorized.html")

    patient = get_current_patient()

    goals = patient.goals
    goals.reverse()

    return render_template("patient-goals.html",
                            patient=patient,
                            goals=goals)


@app.route("/patient/<int:patient_id>/account")
def show_patient_account(patient_id):
    """Show a patient their account information"""

    if not check_patient_authorization(patient_id):
        return render_template("unauthorized.html")

    patient = get_current_patient()

    return render_template("patient-account.html",
                            patient=patient)


@app.route("/patient/<int:patient_id>/edit", methods=["GET"])
def view_edit_patient_information(patient_id):
    """Edit a patient's account information."""

    if not check_patient_authorization(patient_id):
        return render_template("unauthorized.html")

    patient = get_current_patient()

    return render_template("patient-account-edit.html",
                            patient=patient)



@app.route("/patient/<int:patient_id>/edit", methods=["POST"])
def edit_patient_information(patient_id):
    """Process edit of a patient's account information."""

    patient = get_current_patient()

    patient.fname = request.form.get("fname")
    patient.lname = request.form.get("lname")
    patient.email = request.form.get("email")
    patient.street_address = request.form.get("street-address")
    patient.city = request.form.get("city")
    patient.state = request.form.get("state")
    patient.zipcode = request.form.get("zipcode")
    patient.phone = request.form.get("phone")
    patient.birthdate = request.form.get("birthdate")

    db.session.add(patient)
    db.session.commit()

    return redirect(f"/patient/{patient_id}/account")


@app.route("/patient/<int:patient_id>/reset-password", methods=["GET"])
def view_reset_patient_password_form(patient_id):
    """Reset a patient's password."""

    if not check_patient_authorization(patient_id):
        return render_template("unauthorized.html")

    patient = get_current_patient()

    return render_template("patient-resetpw.html",
                            patient=patient)


@app.route("/patient/<int:patient_id>/reset-password", methods=["POST"])
def reset_patient_password(patient_id):
    """Process reset of a patient's password."""

    patient = get_current_patient()

    password = request.form.get("password")

    patient.set_password(password)

    db.session.add(patient)
    db.session.commit()
    
    flash("Password successfully reset.")
    return redirect(f"/patient/{patient_id}/account")




########################   HELPER FUNCTIONS   ########################


def get_current_dietitian():
    """Returns dietitian object for current dietitian_id."""

    dietitian_id = session.get("dietitian_id")

    return Dietitian.query.get(dietitian_id)


def get_current_patient():
    """Returns patient object for current patient_id."""

    patient_id = session.get("patient_id")
    return Patient.query.get(patient_id)


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


def allowed_image(filename):
    """Check if image file has one of the allowed extensions."""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Add jinja datetime filters to format datetime object in posts and comments.
def datetimeformat(value, format="%b %-d, %Y at %-I:%M %p"):
    return value.strftime(format)

app.jinja_env.filters['datetime'] = datetimeformat

def dateformat(value, format="%m-%d-%Y"):
    return value.strftime(format)

app.jinja_env.filters['date'] = dateformat



if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
