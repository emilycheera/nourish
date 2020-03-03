
from datetime import datetime, timedelta
import os

from flask import (Flask, render_template, request, flash, redirect,
    session, jsonify, Markup)
from jinja2 import StrictUndefined
from sqlalchemy import desc
from werkzeug.utils import secure_filename

from flask_debugtoolbar import DebugToolbarExtension

from decorators import dietitian_auth, patient_or_dietitian_auth
from helpers import (get_current_dietitian, get_current_patient,
     get_user_type_from_session, check_patient_authorization, sort_date_desc,
     alphabetize_by_lname, get_list_of_ratings, get_sundays_with_data, 
     get_dietitian_and_patients_list, create_new_dietitian_account, 
     create_new_patient_account, reset_password, create_new_goal, 
     create_goal_dict, get_all_patients_posts)
from jinja_filters import datetimeformat, dateformat, htmldateformat
from model import connect_to_db, db, Dietitian, Patient, Goal, Post, Comment


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
def handle_dietitian_registration_form():
    """Process dietitian registration form."""
    
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    email = request.form.get("email")
    password = request.form.get("password")
    street_address = request.form.get("street-address")
    city = request.form.get("city")
    state = request.form.get("state")
    zipcode = request.form.get("zipcode")

    if Dietitian.query.filter_by(email=email).first():
        flash("An account with this email address already exists.")
        return redirect("/register")

    dietitian_id = create_new_dietitian_account(fname, lname, email, password,
                                                street_address, city, state, 
                                                zipcode)

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
    reset_password(password, dietitian)
    
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

    if Patient.query.filter_by(email=email).first():
        flash("An account with this email address already exists.")
        return redirect("/patient/new-patient")

    patient_id = create_new_patient_account(dietitian_id, fname, lname, email, 
                                            street_address, city, state,
                                            zipcode, phone, birthdate)

    flash(f"Successfully registered new patient {fname} {lname}.")
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

    if not check_patient_authorization(patient_id):
        return render_template("unauthorized.html")

    patient = get_current_patient()

    return render_template("patient-resetpw.html",
                            patient=patient)


@app.route("/patient/<int:patient_id>/account/reset-password", methods=["POST"])
def reset_patient_password(patient_id):
    """Process reset of a patient's password."""

    password = request.form.get("password")
    patient = Patient.query.get(patient_id)
    reset_password(password, patient)

    flash("Password successfully reset.")
    return redirect(f"/patient/{patient_id}/account")


@app.route("/patient/<int:patient_id>/account/customize-posts")
def customize_patient_post_form(patient_id):
    """Allow dietitian to select form fields available on a patient's post."""

    diet_and_pats = get_dietitian_and_patients_list()
    patient = Patient.query.get(patient_id)

    if not patient in diet_and_pats["sorted_patients"]:
        return render_template("unauthorized.html")

    return render_template("dietitian-customize-post-form.html",
                            dietitian=diet_and_pats["dietitian"],
                            patients=diet_and_pats["sorted_patients"],
                            patient=patient)


@app.route("/patient/<int:patient_id>/account/customize-posts", methods = ["POST"])
def save_customized_patient_post_form(patient_id):
    """Save which form fields the dietitian selected for a specific patient."""

    patient = Patient.query.get(patient_id)

    patient.hunger_visible = bool(request.form.get("hunger-visible"))
    patient.fullness_visible = bool(request.form.get("fullness-visible"))
    patient.satisfaction_visible = bool(request.form.get("satisfaction-visible"))

    db.session.add(patient)
    db.session.commit()

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

    # Get list of the patient's goals before new goal is added to check if 
    # there's a previous current goal that needs to be moved to the past 
    # goals section.
    patient = Patient.query.get(patient_id)
    sorted_goals = sort_date_desc(patient.goals)

    if sorted_goals:
        new_past_goal = sorted_goals[0]
        goals = create_goal_dict("goal", new_past_goal)

    time_stamp = datetime.now()
    goal_body = request.form.get("goal-body")
    new_goal = create_new_goal(patient_id, time_stamp, goal_body)

    goals = create_goal_dict("current_goal", new_goal, goals)

    return jsonify(goals)


@app.route("/goal/<int:goal_id>/edit.json", methods=["POST"])
def edit_patient_goal(goal_id):
    """Edit a patient goal."""

    goal = Goal.query.get(goal_id)
    goal_body = request.form.get("goal-body")

    goal.goal_body = goal_body
    goal.edited = True

    db.session.add(goal)
    db.session.commit()

    edited_goal_dict = {}
    goal_dict = create_goal_dict("current_goal", goal, edited_goal_dict)

    return jsonify(goal_dict)


@app.route("/delete-goal", methods=["POST"])
def delete_goal():
    """Delete a goal."""

    goal_id = request.form.get("goal")

    goal = Goal.query.get(goal_id)

    db.session.delete(goal)
    db.session.commit()

    return "Success"


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
def add_post_comment(post_id):
    """Add a comment to a post."""

    time_stamp = datetime.now()
    comment_body = request.form.get("comment")

    user_type = get_user_type_from_session()

    if user_type == "patient":
        author_type = "pat"
        patient = get_current_patient()
        author_id = patient.patient_id
        fname = patient.fname
        lname = patient.lname

    else:
        author_type = "diet"
        dietitian = get_current_dietitian()
        author_id = dietitian.dietitian_id
        fname = dietitian.fname
        lname = dietitian.lname

    new_comment = Comment(post_id=post_id,
                          author_type=author_type,
                          author_id=author_id,
                          time_stamp=time_stamp,
                          comment_body=comment_body)

    db.session.add(new_comment)
    db.session.commit()

    isoformat_time_stamp = time_stamp.isoformat()

    comment = {"user": {"fname": fname,
                        "lname": lname},
               "comment": {"time_stamp": isoformat_time_stamp,
                           "comment_body": comment_body,
                           "edited": "",
                           "comment_id": new_comment.comment_id}}

    return jsonify(comment)


@app.route("/comment/<int:comment_id>/edit.json", methods=["POST"])
def edit_post_comment(comment_id):
    """Update a comment on a post."""

    comment = Comment.query.get(comment_id)
    comment_body = request.form.get("comment")

    comment.comment_body = comment_body
    comment.edited = True

    db.session.add(comment)
    db.session.commit()

    patient = comment.post.patient

    if comment.author_type == "pat":
        fname = patient.fname
        lname = patient.lname

    else:
        dietitian = patient.dietitian
        fname = dietitian.fname
        lname = dietitian.lname

    isoformat_time_stamp = comment.time_stamp.isoformat()

    comment = {"user": {"fname": fname,
                        "lname": lname},
               "comment": {"time_stamp": isoformat_time_stamp,
                           "comment_body": comment_body,
                           "edited": " (edited)",
                           "comment_id": comment.comment_id}}

    return jsonify(comment)


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

    sorted_goals = sort_date_desc(patient.goals)
    current_goal = sorted_goals[0] if sorted_goals else None

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

    patient_id = session.get("patient_id")
    time_stamp = datetime.now()
    meal_time = request.form.get("meal-time")
    meal_setting = request.form.get("meal-setting")
    TEB = request.form.get("TEB")
    hunger = request.form.get("hunger") or None
    fullness = request.form.get("fullness") or None
    satisfaction = request.form.get("satisfaction") or None
    meal_notes = request.form.get("meal-notes")

    new_post = Post(patient_id=patient_id,
                    time_stamp=time_stamp,
                    meal_time=meal_time,
                    img_path=img_path,
                    meal_setting=meal_setting,
                    TEB=TEB,
                    hunger=hunger,
                    fullness=fullness,
                    satisfaction=satisfaction,
                    meal_notes=meal_notes)

    db.session.add(new_post)
    db.session.commit()

    flash(Markup(f"Post added successfully. <a href='/patient/{patient_id}/posts'>Click here to see it.</a>"))
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

    if img_path:
        post.img_path = img_path

    hunger = request.form.get("hunger")
    fullness = request.form.get("fullness")
    satisfaction = request.form.get("satisfaction")

    post.meal_time = request.form.get("meal-time")
    post.meal_setting = request.form.get("meal-setting")
    post.TEB = request.form.get("TEB")
    post.edited = True
    post.meal_notes = request.form.get("meal-notes")
    post.hunger = hunger if hunger else None
    post.fullness = fullness if fullness else None
    post.satisfaction = satisfaction if satisfaction else None
    
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


@app.route("/patient/<int:patient_id>/ratings-chart")
@patient_or_dietitian_auth
def get_ratings_chart_template(patient_id):
    """Shows page containing rating chart div."""

    diet_and_pats = get_dietitian_and_patients_list()
    patient = Patient.query.get(patient_id)

    return render_template("dietitian-ratings-chart.html",
                            dietitian=diet_and_pats["dietitian"],
                            patients=diet_and_pats["sorted_patients"],
                            patient=patient)


@app.route("/patient/<int:patient_id>/weekly-ratings.json")
def get_patients_weekly_ratings(patient_id):
    """Get a patient's hunger/fullness/satisfaction ratings from last 7 days."""

    patient = Patient.query.get(patient_id)
    now = datetime.now()
    one_week_ago = now - timedelta(days=7)

    hunger_ratings_list = get_list_of_ratings(patient, Post.hunger, one_week_ago, now)
    fullness_ratings_list = get_list_of_ratings(patient, Post.fullness, one_week_ago, now)
    satisfaction_ratings_list = get_list_of_ratings(patient, Post.satisfaction, one_week_ago, now)

    # Get dates to populate dropdown menu.
    sundays_with_data = get_sundays_with_data(patient)

    return jsonify({"data": {"hunger": hunger_ratings_list,
                             "fullness": fullness_ratings_list,
                             "satisfaction": satisfaction_ratings_list,
                             "one_week_ago": one_week_ago.isoformat()},
                    "dropdown": {"dropdown_dates": sundays_with_data}})


@app.route("/patient/<int:patient_id>/past-ratings.json")
def get_patients_past_ratings(patient_id):
    """Get hunger/fullness/satisfaction ratings from a previous week."""

    patient = Patient.query.get(patient_id)

    search_start_date_isoformat = request.args.get("chart-date")
    search_start_date = datetime.strptime(search_start_date_isoformat, "%Y-%m-%d")

    # Get the date one week from the start date.
    search_end_date = search_start_date + timedelta(days=7)

    hunger_ratings_list = get_list_of_ratings(patient, Post.hunger, search_start_date, search_end_date)
    fullness_ratings_list = get_list_of_ratings(patient, Post.fullness, search_start_date, search_end_date)
    satisfaction_ratings_list = get_list_of_ratings(patient, Post.satisfaction, search_start_date, search_end_date)

    return jsonify({"data": {"hunger": hunger_ratings_list,
                             "fullness": fullness_ratings_list,
                             "satisfaction": satisfaction_ratings_list,
                             "search_start_date": search_start_date_isoformat}})


@app.route("/patient/<int:patient_id>/get-post.json")
def get_post_from_chart(patient_id):
    """Get a post as JSON from clicking on a point on the ratings chart."""

    rating_label = request.args.get("ratingLabel")
    meal_time_isoformat = request.args.get("postDatetime")
    rating_value = request.args.get("ratingValue")

    # Assign the type of rating to search for in the query.
    if rating_label == "Hunger Rating":
        rating_to_search = Post.hunger

    elif rating_label == "Fullness Rating":
        rating_to_search = Post.fullness

    else:
        rating_to_search = Post.satisfaction

    # Convert meal_time from isoformat to a datetime object.
    post_meal_time = datetime.strptime(meal_time_isoformat, "%Y-%m-%dT%H:%M:%S")

    post = Post.query.filter(Post.meal_time==post_meal_time,
                             Post.patient_id==patient_id,
                             rating_to_search==rating_value).first()

    edited = " (edited)" if post.edited else ""

    post_dict = {"patient": {"patient_id": patient_id,
                             "fname": post.patient.fname,
                             "lname": post.patient.lname},
                 "post": {"post_id": post.post_id,
                          "time_stamp": post.time_stamp.isoformat(),
                          "edited": edited,
                          "img_path": post.img_path,
                          "meal_time": post.meal_time.isoformat(),
                          "meal_setting": post.meal_setting,
                          "TEB": post.TEB,
                          "hunger": post.hunger,
                          "fullness": post.fullness,
                          "satisfaction": post.satisfaction,
                          "meal_notes": post.meal_notes},
                 "comments": {}}

    comments = post.comments
    if comments:
        sorted_comments = sorted(comments, key=lambda x: x.time_stamp)
        patient = Patient.query.get(patient_id)
        
        for comment in sorted_comments:
            author_fname = patient.dietitian.fname if comment.author_type == "diet" else patient.fname
            author_lname = patient.dietitian.lname if comment.author_type == "diet" else patient.lname 
            edited = " (edited)" if comment.edited else ""

            user_type = get_user_type_from_session()

            if ((user_type == "dietitian" and comment.author_type == "diet") or 
            (user_type == "patient" and comment.author_type == "pat")):
                is_author = True
            else:
                is_author = False

            print(is_author)

            post_dict["comments"][comment.comment_id] = {"comment_id": comment.comment_id,
                                                         "author_fname": author_fname,
                                                         "author_lname": author_lname,
                                                         "comment_body": comment.comment_body,
                                                         "time_stamp": comment.time_stamp.isoformat(),
                                                         "edited": edited,
                                                         "is_author": is_author}

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
