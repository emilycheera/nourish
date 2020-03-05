
from datetime import datetime, timedelta
import os

from flask import (Flask, render_template, request, flash, redirect,
                   session, jsonify, Markup)
from jinja2 import StrictUndefined
from sqlalchemy import desc
from werkzeug.utils import secure_filename

from flask_debugtoolbar import DebugToolbarExtension

from comments import (add_post_comment, edit_post_comment, delete_comment,
                      create_comment_dict)
from decorators import (dietitian_auth, patient_or_dietitian_auth, 
                        patient_belongs_to_dietitian, patient_auth,
                        dietitian_redirect)
from goals import (edit_patient_goal, delete_goal, create_goal_dict,
                   add_goal_and_get_dict)
from helpers import sort_date_desc
from jinja_filters import datetimeformat, dateformat, htmldateformat
from model import connect_to_db, db, Dietitian, Patient, Goal, Post, Comment
from posts import (create_new_post, edit_post, delete_post,
                   get_all_patients_posts, save_customized_patient_post_form,
                   get_post_object, create_post_dict)
from ratings import get_ratings_dict, get_sundays_with_data
from users import (create_new_dietitian_account, update_dietitian_account,
                   create_new_patient_account, update_patient_account,
                   reset_password, get_current_dietitian, get_current_patient,
                   get_user_type_from_session, get_dietitian_and_patients_list)



app = Flask(__name__)
app.secret_key = "b_xd3xf9095~xa68x90E^O1xd3R"

app.jinja_env.filters['datetime'] = datetimeformat
app.jinja_env.filters['date'] = dateformat
app.jinja_env.filters['htmldatetime'] = htmldateformat
app.jinja_env.undefined = StrictUndefined

UPLOAD_FOLDER = "static/images/uploads/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


@app.route("/", methods=["GET"])
def index():
    """Homepage that shows login form."""

    patient_id = session.get("patient_id")
    if patient_id:
        return redirect(f"/patient/{patient_id}")

    dietitian_id = session.get("dietitian_id")
    if session.get("dietitian_id"):
        return redirect(f"/dietitian/{dietitian_id}")

    return render_template("homepage.html")


@app.route("/patient-login", methods=["POST"])
def handle_patient_login():
    """Log in a patient user."""

    email = request.form.get("email")
    password = request.form.get("password")

    patient = Patient.query.filter_by(email=email).first()

    if not patient: 
        flash(f"""No account with {email}. Contact your dietitian 
                  to create or update your account.""")
        return redirect("/")

    if not patient.check_password(password):
        flash("Incorrect password.")
        return redirect("/")

    session["patient_id"] = patient.patient_id
    flash("Login successful.")
    return redirect(f"/patient/{patient.patient_id}")


@app.route("/dietitian-login", methods=["POST"])
def handle_dietitian_login():
    """Log in a dietitian user."""

    email = request.form.get("email")
    password = request.form.get("password")

    dietitian = Dietitian.query.filter_by(email=email).first()

    if not dietitian:
        flash(f"""No account with {email}. Please register 
                  a new dietitian account.""")
        return redirect("/")

    if not dietitian.check_password(password):
        flash("Incorrect password.")
        return redirect("/")

    session["dietitian_id"] = dietitian.dietitian_id
    flash("Login successful.")
    return redirect(f"/dietitian/{dietitian.dietitian_id}")


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
def handle_dietitian_registration():
    """Process dietitian registration form."""
    
    email = request.form.get("email")
    if Dietitian.query.filter_by(email=email).first():
        flash("An account with this email address already exists.")
        return redirect("/register")

    form_data = request.form
    dietitian_id = create_new_dietitian_account(form_data)

    # Log in new dietitian
    session["dietitian_id"] = dietitian_id

    flash(f"Successfully registered {email}.")
    return redirect(f"/dietitian/{dietitian_id}")


@app.route("/dietitian/<int:dietitian_id>")
@dietitian_auth
def show_dietitian_homepage(dietitian_id):
    """Show a dietitian's homepage."""

    diet_and_pats = get_dietitian_and_patients_list()
    posts = get_all_patients_posts(diet_and_pats["dietitian"])

    return render_template("dietitian-home-posts.html",
                            dietitian=diet_and_pats["dietitian"],
                            patients=diet_and_pats["sorted_patients"],
                            posts=posts)


@app.route("/dietitian/<int:dietitian_id>/account")
@dietitian_auth
def show_dietitian_account(dietitian_id):
    """Show a dietitian their account information"""

    diet_and_pats = get_dietitian_and_patients_list()

    return render_template("dietitian-account.html",
                            dietitian=diet_and_pats["dietitian"],
                            patients=diet_and_pats["sorted_patients"])


@app.route("/dietitian/<int:dietitian_id>/account/edit", methods=["GET"])
@dietitian_auth
def view_edit_dietitian_information(dietitian_id):
    """Edit a dietitian's account information."""

    diet_and_pats = get_dietitian_and_patients_list()

    return render_template("dietitian-account-edit.html",
                            dietitian=diet_and_pats["dietitian"],
                            patients=diet_and_pats["sorted_patients"])


@app.route("/dietitian/<int:dietitian_id>/account/edit", methods=["POST"])
def edit_dietitian_information(dietitian_id):
    """Process edit of a dietitian's account information."""

    update_dietitian_account(dietitian_id, request.form)
 
    flash("Account successfully updated.")
    return redirect(f"/dietitian/{dietitian_id}/account")


@app.route("/dietitian/<int:dietitian_id>/account/reset-password", methods=["GET"])
@dietitian_auth
def view_reset_dietitian_password_form(dietitian_id):
    """Reset a dietitian's password."""

    diet_and_pats = get_dietitian_and_patients_list()

    return render_template("dietitian-resetpw.html",
                            dietitian=diet_and_pats["dietitian"],
                            patients=diet_and_pats["sorted_patients"])


@app.route("/dietitian/<int:dietitian_id>/account/reset-password", methods=["POST"])
def reset_dietitian_password(dietitian_id):
    """Process reset of a dietitian's password."""

    password = request.form.get("password")
    dietitian = get_current_dietitian()
    reset = reset_password(password, dietitian)
      
    flash("Password successfully reset.")
    return redirect(f"/dietitian/{dietitian_id}/account")


@app.route("/patient/new-patient", methods=["GET"])
def show_patient_registration_form():
    """Show form for new patient registration."""
    
    user_type = get_user_type_from_session()

    if user_type != "dietitian":
        return render_template("unauthorized.html")

    diet_and_pats = get_dietitian_and_patients_list()

    return render_template("patient-registration.html",
                            dietitian=diet_and_pats["dietitian"],
                            patients=diet_and_pats["sorted_patients"])


@app.route("/patient/new-patient", methods=["POST"])
def process_patient_registration():
    """Process new patient registration."""

    email = request.form.get("email")

    if Patient.query.filter_by(email=email).first():
        flash("An account with this email address already exists.")
        return redirect("/patient/new-patient")

    patient_id = create_new_patient_account(request.form)

    flash(f"Successfully registered new patient.")
    return redirect(f"/patient/{patient_id}")


@app.route("/patient/<int:patient_id>/account")
@patient_or_dietitian_auth
def show_single_patient_overview(patient_id):
    """Show information about a single patient."""

    user_type = get_user_type_from_session()
    patient = Patient.query.get(patient_id)

    if user_type == "dietitian":
        diet_and_pats = get_dietitian_and_patients_list()
        return render_template("dietitian-home-patient-overview.html",
                            dietitian=diet_and_pats["dietitian"],
                            patients=diet_and_pats["sorted_patients"],
                            patient=patient)

    return render_template("patient-account.html",
                            patient=patient)


@app.route("/patient/<int:patient_id>/account/edit")
@patient_or_dietitian_auth
def view_edit_patient_information_form(patient_id):
    """Edit a patient's basic information."""

    user_type = get_user_type_from_session()
    patient = Patient.query.get(patient_id)

    if user_type == "dietitian":
        diet_and_pats = get_dietitian_and_patients_list()
        return render_template("dietitian-home-patient-edit.html",
                                dietitian=diet_and_pats["dietitian"],
                                patients=diet_and_pats["sorted_patients"],
                                patient=patient)

    return render_template("patient-account-edit.html",
                            patient=patient)


@app.route("/patient/<int:patient_id>/account/edit", methods=["POST"])
def edit_single_patient_information(patient_id):
    """Process edit of a single patient's basic information."""

    update_patient_account(patient_id, request.form)
    
    flash("Account successfully updated.")
    return redirect(f"/patient/{patient_id}/account")


@app.route("/patient/<int:patient_id>/account/reset-password", methods=["GET"])
@patient_auth
def view_reset_patient_password_form(patient_id):
    """Reset a patient's password."""

    patient = get_current_patient()

    return render_template("patient-resetpw.html",
                            patient=patient)


@app.route("/patient/<int:patient_id>/account/reset-password", methods=["POST"])
def reset_patient_password(patient_id):
    """Process reset of a patient's password."""

    password = request.form.get("password")
    patient = Patient.query.get(patient_id)
    reset = reset_password(password, patient)

    flash("Password successfully reset.")
    return redirect(f"/patient/{patient_id}/account")


@app.route("/patient/<int:patient_id>/account/customize-posts")
@patient_belongs_to_dietitian
def customize_patient_post_form(patient_id):
    """Allow dietitian to select form fields available on a patient's post."""

    diet_and_pats = get_dietitian_and_patients_list()
    patient = Patient.query.get(patient_id)

    return render_template("dietitian-customize-post-form.html",
                            dietitian=diet_and_pats["dietitian"],
                            patients=diet_and_pats["sorted_patients"],
                            patient=patient)


@app.route("/patient/<int:patient_id>/account/customize-posts", methods=["POST"])
def process_customized_patient_post_form(patient_id):
    """Process customize post form and redirect to patient's account."""

    save_customized_patient_post_form(patient_id, request.form)

    flash("Form customization saved.")
    return redirect(f"/patient/{patient_id}/account")


@app.route("/patient/<int:patient_id>/goals", methods=["GET"])
@patient_or_dietitian_auth
def show_patient_goals(patient_id):
    """Show goals for a patient and allow dietitian to update goals."""

    user_type = get_user_type_from_session()
    patient = Patient.query.get(patient_id)
    sorted_goals = sort_date_desc(patient.goals)

    if user_type == "dietitian":
        diet_and_pats = get_dietitian_and_patients_list()
        current_goal = sorted_goals[0] if sorted_goals else None
        past_goals = sorted_goals[1:] if sorted_goals else None

        return render_template("dietitian-home-patient-goals.html",
                                dietitian=diet_and_pats["dietitian"],
                                patients=diet_and_pats["sorted_patients"],
                                patient=patient,
                                current_goal=current_goal,
                                past_goals=past_goals)

    return render_template("patient-goals.html",
                            patient=patient,
                            goals=sorted_goals)


@app.route("/patient/<int:patient_id>/add-goal.json", methods=["POST"])
def add_new_patient_goal(patient_id):
    """Process form to add a new goal."""

    goals = add_goal_and_get_dict(patient_id, request.form)

    return jsonify(goals)


@app.route("/goal/<int:goal_id>/edit.json", methods=["POST"])
def proccess_edit_of_a_patient_goal(goal_id):
    """Edit a patient goal."""

    goal = edit_patient_goal(goal_id, request.form)

    edited_goal_dict = {}
    goal_dict = create_goal_dict("current_goal", goal, edited_goal_dict)

    return jsonify(goal_dict)


@app.route("/delete-goal", methods=["POST"])
def handle_delete_goal_process():
    """Handle process to delete a goal."""

    goal_id = request.form.get("goal")
    deleted = delete_goal(goal_id)

    return deleted


@app.route("/patient/<int:patient_id>/posts")
@patient_or_dietitian_auth
def show_single_patient_posts(patient_id):
    """Show a patient's posts."""

    user_type = get_user_type_from_session()
    patient = Patient.query.get(patient_id)
    sorted_posts = sort_date_desc(patient.posts)

    if user_type == "dietitian":
        diet_and_pats = get_dietitian_and_patients_list()
        return render_template("dietitian-home-patient-posts.html",
                                dietitian=diet_and_pats["dietitian"],
                                patients=diet_and_pats["sorted_patients"],
                                patient=patient,
                                posts=sorted_posts)
    
    dietitian = patient.dietitian
    return render_template("patient-posts.html",
                            patient=patient,
                            dietitian=dietitian,
                            posts=sorted_posts)


@app.route("/post/<int:post_id>/add-comment.json", methods=["POST"])
def handle_adding_post_comment(post_id):
    """Handle adding a comment to a post."""

    new_comment = add_post_comment(post_id, request.form)
    comment_dict = create_comment_dict(new_comment)

    return jsonify(comment_dict)


@app.route("/comment/<int:comment_id>/edit.json", methods=["POST"])
def process_edit_post_comment_form(comment_id):
    """Process update of a comment on a post."""

    comment = edit_post_comment(comment_id, request.form)
    comment_dict = create_comment_dict(comment)

    return jsonify(comment_dict)


@app.route("/delete-comment", methods=["POST"])
def handle_delete_comment_process():
    """Handle process to delete a comment."""

    comment_id = request.form.get("comment")
    deleted = delete_comment(comment_id)

    return deleted


@app.route("/patient/<int:patient_id>")
@dietitian_redirect
@patient_auth
def show_patient_homepage(patient_id):
    """Show a patient's homepage."""

    patient = get_current_patient()
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M")

    sorted_goals = sort_date_desc(patient.goals)
    current_goal = sorted_goals[0] if sorted_goals else None

    return render_template("patient-home-main.html",
                            patient=patient,
                            goal=current_goal,
                            current_time=current_time)


@app.route("/post/new-post", methods=["POST"])
def process_new_post_form():
    """Handle adding a new post."""
    
    img_path = save_image()
    patient_id = session.get("patient_id")

    if img_path == "Bad Extension":
        flash("Only .png, .jpg, or .jpeg images are accepted.")
        return redirect(f"/patient/{patient_id}")

    create_new_post(patient_id, img_path, request.form)

    flash(Markup(f"""Post added successfully. 
                     <a href='/patient/{patient_id}/posts'>
                     Click here to see it.</a>"""))
    return redirect(f"/patient/{patient_id}")


@app.route("/post/edit/<int:post_id>", methods=["POST"])
def handle_edit_post_form(post_id):
    """Handle edits made to a patient's post."""

    img_path = save_image()
    patient_id = post.patient.patient_id

    if img_path == "Bad Extension":
        flash("Only .png, .jpg, or .jpeg images are accepted.")
        return redirect(f"/patient/{patient_id}/posts")

    edit_post(post_id, img_path, request.form)

    flash("Post updated successfully.")
    return redirect(f"/patient/{patient_id}/posts")


@app.route("/delete-post", methods=["POST"])
def handle_delete_post_process():
    """Handle process to delete a post."""

    post_id = request.form.get("post")
    delete = delete_post(post_id)

    return delete


@app.route("/patient/<int:patient_id>/ratings-chart")
@patient_or_dietitian_auth
def get_ratings_chart_template(patient_id):
    """Shows page containing rating chart div."""

    user_type = get_user_type_from_session()
    patient = Patient.query.get(patient_id)

    if user_type == "dietitian":
        diet_and_pats = get_dietitian_and_patients_list()

        return render_template("dietitian-ratings-chart.html",
                                dietitian=diet_and_pats["dietitian"],
                                patients=diet_and_pats["sorted_patients"],
                                patient=patient)

    return render_template("patient-ratings-chart.html",
                            patient=patient)


@app.route("/patient/<int:patient_id>/recent-ratings.json")
def get_patients_weekly_ratings(patient_id):
    """Get a patient's hunger/fullness/satisfaction ratings from last 7 days."""

    sundays_with_data = get_sundays_with_data(patient_id)

    # Assign start and end dates for ratings database query to the most recent
    # week that has ratings data.
    from_date_isoformat = sundays_with_data[0]
    from_date = datetime.strptime(from_date_isoformat, "%Y-%m-%d")
    to_date = from_date + timedelta(days=7)

    # Get a dictionary of hunger, fullness, and satisfaction ratings from a
    # specific patient over a specific period of time.
    recent_ratings_dict = get_ratings_dict(patient_id, from_date_isoformat, 
                                           from_date, to_date)
    
    # Get dates to populate dropdown menu for searching previous weeks'
    # ratings data.
    recent_ratings_dict["dropdown"] = {"dropdown_dates": sundays_with_data}

    return jsonify(recent_ratings_dict)


@app.route("/patient/<int:patient_id>/past-ratings.json")
def get_patients_past_ratings(patient_id):
    """Get hunger/fullness/satisfaction ratings from a previous week."""

    # Assign start and end dates for ratings database query.
    from_date_isoformat = request.args.get("chart-date")
    from_date = datetime.strptime(from_date_isoformat, "%Y-%m-%d")
    to_date = from_date + timedelta(days=7)

    past_ratings_dict = get_ratings_dict(patient_id, from_date_isoformat, 
                                         from_date, to_date)

    return jsonify(past_ratings_dict)


@app.route("/patient/<int:patient_id>/get-post.json")
def get_post_from_chart(patient_id):
    """Get a post as JSON from clicking on a point on the ratings chart."""

    point_data = request.args
    post = get_post_object(point_data, patient_id)

    post_dict = create_post_dict(patient_id, post)

    return jsonify(post_dict)


def allowed_image(filename):
    """Check if image file has one of the allowed extensions."""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image():
    """Save uploaded image to upload folder and return filepath."""

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




if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
