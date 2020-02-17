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


@app.route("/dietitian/<int:dietitian_id>/account/edit", methods=["GET"])
def view_edit_dietitian_information(dietitian_id):
    """Edit a dietitian's account information."""

    if not check_dietitian_authorization(dietitian_id):
        return render_template("unauthorized.html")

    dietitian = get_current_dietitian()
    patients_list = dietitian.patients

    return render_template("dietitian-account-edit.html",
                            dietitian=dietitian,
                            patients=patients_list)


@app.route("/dietitian/<int:dietitian_id>/account/edit", methods=["POST"])
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

    flash("Account successfully updated.")
    return redirect(f"/dietitian/{dietitian_id}/account")


@app.route("/dietitian/<int:dietitian_id>/account/reset-password", methods=["GET"])
def view_reset_dietitian_password_form(dietitian_id):
    """Reset a dietitian's password."""

    if not check_dietitian_authorization(dietitian_id):
        return render_template("unauthorized.html")

    dietitian = get_current_dietitian()
    patients_list = dietitian.patients

    return render_template("dietitian-resetpw.html",
                            dietitian=dietitian,
                            patients=patients_list)


@app.route("/dietitian/<int:dietitian_id>/account/reset-password", methods=["POST"])
def reset_dietitian_password(dietitian_id):
    """Process reset of a dietitian's password."""

    dietitian = get_current_dietitian()

    password = request.form.get("password")

    dietitian.set_password(password)

    db.session.add(dietitian)
    db.session.commit()
    
    flash("Password successfully reset.")
    return redirect(f"/dietitian/{dietitian_id}/account")


@app.route("/patient/new-patient", methods=["GET"])
def show_patient_registration_form():
    """Show form for new patient registration."""
    
    user_type = get_user_type_from_session()

    if user_type != "dietitian":
        return render_template("unauthorized.html")

    dietitian = get_current_dietitian()
    patients_list = dietitian.patients

    return render_template("patient-registration.html",
                            dietitian=dietitian,
                            patients=patients_list)


@app.route("/patient/new-patient", methods=["POST"])
def process_patient_registration():
    """Process new patient registration."""

    dietitian_id = request.form.get("dietitian_id")
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
    return redirect(f"/patient/{patient_id}")


@app.route("/patient/<int:patient_id>/account")
def show_single_patient_overview(patient_id):
    """Show information about a single patient."""

    user_type = get_user_type_from_session()

    if user_type == "dietitian":
        dietitian = get_current_dietitian()
        patients_list = dietitian.patients
        patient = Patient.query.get(patient_id)

        if not patient in patients_list:
            return render_template("unauthorized.html")

        return render_template("dietitian-home-patient-overview.html",
                            dietitian=dietitian,
                            patients=patients_list,
                            patient=patient)


    if not check_patient_authorization(patient_id):
        return render_template("unauthorized.html")

    patient = get_current_patient()

    return render_template("patient-account.html",
                            patient=patient)


@app.route("/patient/<int:patient_id>/account/edit")
def view_edit_patient_information_form(patient_id):
    """Edit a patient's basic information."""

    user_type = get_user_type_from_session()

    if user_type == "dietitian":
        dietitian = get_current_dietitian()
        patients_list = dietitian.patients
        patient = Patient.query.get(patient_id)

        if not patient in patients_list:
            return render_template("unauthorized.html")

        return render_template("dietitian-home-patient-edit.html",
                                dietitian=dietitian,
                                patients=patients_list,
                                patient=patient)

    if not check_patient_authorization(patient_id):
        return render_template("unauthorized.html")

    patient = get_current_patient()

    return render_template("patient-account-edit.html",
                            patient=patient)


@app.route("/patient/<int:patient_id>/account/edit", methods=["POST"])
def edit_single_patient_information(patient_id):
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
    
    flash("Account successfully updated.")
    return redirect(f"/patient/{patient_id}/account")


@app.route("/patient/<int:patient_id>/account/reset-password", methods=["GET"])
def view_reset_patient_password_form(patient_id):
    """Reset a patient's password."""

    user_type = get_user_type_from_session()

    if user_type == "dietitian":
        dietitian = get_current_dietitian()
        patients_list = dietitian.patients
        patient = Patient.query.get(patient_id)

        if not patient in patients_list:
            return render_template("unauthorized.html")

        return render_template("dietitian-home-patient-resetpw.html",
                                dietitian=dietitian,
                                patients=patients_list,
                                patient=patient)


    if not check_patient_authorization(patient_id):
        return render_template("unauthorized.html")

    patient = get_current_patient()

    return render_template("patient-resetpw.html",
                            patient=patient)


@app.route("/patient/<int:patient_id>/account/reset-password", methods=["POST"])
def reset_patient_password(patient_id):
    """Process reset of a patient's password."""

    patient = Patient.query.get(patient_id)

    password = request.form.get("password")

    patient.set_password(password)

    db.session.add(patient)
    db.session.commit()

    flash("Password successfully reset.")
    return redirect(f"/patient/{patient_id}/account")


@app.route("/patient/<int:patient_id>/goals", methods=["GET"])
def show_patient_goals(patient_id):
    """Show goals for a patient and allow dietitian to update goals."""

    user_type = get_user_type_from_session()

    if user_type == "dietitian":
        dietitian = get_current_dietitian()
        patients_list = dietitian.patients
        patient = Patient.query.get(patient_id)

        if not patient in patients_list:
            return render_template("unauthorized.html")

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

    if not check_patient_authorization(patient_id):
        return render_template("unauthorized.html")

    patient = get_current_patient()

    goals = patient.goals
    goals.reverse()

    return render_template("patient-goals.html",
                            patient=patient,
                            goals=goals)


@app.route("/patient/<int:patient_id>/add-goal", methods=["POST"])
def add_new_patient_goal(patient_id):
    """Process form to add a new goal."""

    time_stamp = datetime.now()
    goal_body = request.form.get("goal-body")

    new_goal = Goal(patient_id=patient_id,
                    time_stamp=time_stamp,
                    goal_body=goal_body)

    db.session.add(new_goal)
    db.session.commit()

    flash("Successfully added goal.")
    return redirect(f"/patient/{patient_id}/goals")


@app.route("/patient/<int:patient_id>/edit/<int:goal_id>", methods=["POST"])
def edit_patient_goal(patient_id, goal_id):
    """Edit a patient goal."""

    goal = Goal.query.get(goal_id)

    goal_body = request.form.get("goal-body")

    goal.goal_body = goal_body

    db.session.add(goal)
    db.session.commit()

    return redirect(f"/patient/{patient_id}/goals")


@app.route("/delete-goal", methods=["POST"])
def delete_goal():
    """Delete a goal."""

    goal_id = request.form.get("goal")

    goal = Goal.query.get(goal_id)

    db.session.delete(goal)
    db.session.commit()

    return "Success"


@app.route("/patient/<int:patient_id>/posts")
def show_single_patient_posts(patient_id):
    """Show a patient's posts."""

    user_type = get_user_type_from_session()

    if user_type == "dietitian":
        dietitian = get_current_dietitian()
        patients_list = dietitian.patients
        patient = Patient.query.get(patient_id)

        if not patient in patients_list:
            return render_template("unauthorized.html")

        patient_posts = patient.posts
        patient_posts.reverse()

        return render_template("dietitian-home-patient-posts.html",
                                dietitian=dietitian,
                                patients=patients_list,
                                patient=patient,
                                posts=patient_posts)

    if not check_patient_authorization(patient_id):
        return render_template("unauthorized.html")

    patient = get_current_patient()

    posts = patient.posts
    posts.reverse()

    return render_template("patient-posts.html",
                            patient=patient,
                            posts=posts)


@app.route("/post/<int:post_id>/add-comment", methods=["POST"])
def add_post_comment(post_id):
    """Add a comment to a post."""

    time_stamp = datetime.now()
    comment_body = request.form.get("comment")
    current_page = request.form.get("current-page")

    new_comment = Comment(post_id=post_id,
                          time_stamp=time_stamp,
                          comment_body=comment_body)

    db.session.add(new_comment)
    db.session.commit()

    if current_page == "home":
        dietitian_id = session.get("dietitian_id")
        return redirect(f"/dietitian/{dietitian_id}")

    post = Post.query.get(post_id)
    patient_id = post.patient.patient_id
    return redirect(f"/patient/{patient_id}/posts")


@app.route("/comment/<int:comment_id>/edit", methods=["POST"])
def edit_post_comment(comment_id):
    """Update a comment on a post."""

    comment = Comment.query.get(comment_id)

    comment_body = request.form.get("comment")
    current_page = request.form.get("current-page")

    comment.comment_body = comment_body

    db.session.add(comment)
    db.session.commit()

    if current_page == "home":
        dietitian_id = session.get("dietitian_id")
        return redirect(f"/dietitian/{dietitian_id}")

    patient_id = request.form.get("patient-id")
    return redirect(f"/patient/{patient_id}/posts")


@app.route("/delete-comment", methods=["POST"])
def delete_comment():
    """Delete a comment."""

    comment_id = request.form.get("comment")

    comment = Comment.query.get(comment_id)

    db.session.delete(comment)
    db.session.commit()

    return "Success"


@app.route("/patient/<int:patient_id>")
def show_patient_homepage(patient_id):
    """Show a patient's homepage."""

    user_type = get_user_type_from_session()

    # If user is a dietitian, redirect to patient's account information.
    if user_type == "dietitian":
        return redirect(f"/patient/{patient_id}/account")

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


@app.route("/post/new-post", methods=["POST"])
def add_new_post():
    """Add a new post."""

    img_path = save_image()

    if img_path == "Bad Extension":
        flash("Only .png, .jpg, or .jpeg images are accepted.")
        return redirect(f"/patient/{patient_id}")

    patient_id = request.form.get("patient-id")
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


@app.route("/post/edit/<int:post_id>", methods=["POST"])
def edit_post(post_id):
    """Save edits made to a patient's post."""

    post = Post.query.get(post_id)
    patient_id = post.patient.patient_id

    img_path = save_image()

    if img_path == "Bad Extension":
        flash("Only .png, .jpg, or .jpeg images are accepted.")
        return redirect(f"/patient/{patient_id}/posts")

    meal_time = request.form.get("meal-time")
    meal_setting = request.form.get("meal-setting")
    TEB = request.form.get("TEB")
    hunger = request.form.get("hunger")
    fullness = request.form.get("fullness")
    satisfaction = request.form.get("satisfaction")
    meal_notes = request.form.get("meal-notes")

    if meal_time:
        post.meal_time = meal_time

    if img_path:
        post.img_path = img_path

    if meal_setting:
        post.meal_setting = meal_setting

    if TEB:
        post.TEB = TEB

    if hunger:
        post.hunger = hunger

    if fullness:
        post.fullness = fullness

    if satisfaction:
        post.satisfaction = satisfaction

    if meal_notes:
        post.meal_notes = meal_notes

    
    db.session.add(post)
    db.session.commit()

    flash("Post updated successfully.")
    return redirect(f"/patient/{patient_id}/posts")


@app.route("/delete-post", methods=["POST"])
def delete_post():
    """Delete a post."""

    post_id = request.form.get("post")

    post = Post.query.get(post_id)
    comments = post.comments

    for comment in comments:
        db.session.delete(comment)

    db.session.delete(post)
    db.session.commit()

    return "Success"


########################   HELPER FUNCTIONS   ########################


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


def allowed_image(filename):
    """Check if image file has one of the allowed extensions."""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image():

    if not request.files:
        return None

    if request.files:
        file = request.files.get("meal-image")

    if file.filename == "":
        return None

    if not allowed_image(file.filename):
        return "Bad Extension"

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img_path = f"/static/images/uploads/{filename}"

    return img_path


# Add jinja datetime filters to format datetime object in posts and comments.
def datetimeformat(value, format="%b %-d, %Y at %-I:%M %p"):
    return value.strftime(format)
app.jinja_env.filters['datetime'] = datetimeformat

def dateformat(value, format="%m-%d-%Y"):
    return value.strftime(format)
app.jinja_env.filters['date'] = dateformat

def htmldateformat(value, format="%Y-%m-%dT%H:%M"):
    return value.strftime(format)
app.jinja_env.filters['htmldatetime'] = htmldateformat



if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
