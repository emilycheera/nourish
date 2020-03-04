from datetime import datetime
from helpers import sort_date_asc
from model import db, Patient, Dietitian, Post
from users import get_user_type_from_session


def create_new_post(patient_id, img_path, form_data):
    """Add a new post to the database."""

    time_stamp = datetime.now()
    meal_time = form_data.get("meal-time")
    meal_setting = form_data.get("meal-setting")
    TEB = form_data.get("TEB")
    hunger = form_data.get("hunger") or None
    fullness = form_data.get("fullness") or None
    satisfaction = form_data.get("satisfaction") or None
    meal_notes = form_data.get("meal-notes")

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

    return "Success"


def edit_post(post_id, img_path, form_data):
    """Save an edited post in the database."""

    post = Post.query.get(post_id)

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

    return "Success"


def delete_post(post_id):
    """Delete a post from the database."""

    post = Post.query.get(post_id)
    comments = post.comments

    for comment in comments:
        db.session.delete(comment)

    db.session.delete(post)
    db.session.commit()

    return "Success"


def get_all_patients_posts(dietitian):
    """Get all of a dietitian's patient's posts, limit to 30."""

    posts = (Post.query.filter(Patient.dietitian_id == dietitian.dietitian_id)
            .join(Patient)
            .join(Dietitian)
            .order_by(Post.time_stamp.desc())
            .limit(30).all())

    return posts


def save_customized_patient_post_form(patient_id, form_data):
    """Save which form fields the dietitian selected for a specific patient."""

    patient = Patient.query.get(patient_id)

    patient.hunger_visible = bool(form_data.get("hunger-visible"))
    patient.fullness_visible = bool(form_data.get("fullness-visible"))
    patient.satisfaction_visible = bool(form_data.get("satisfaction-visible"))

    db.session.add(patient)
    db.session.commit()

    return "Success"


def get_rating_label_to_search(rating_label):
    """Assign the type of rating to search for in the query for a post."""

    if rating_label == "Hunger Rating":
        rating_to_search = Post.hunger

    elif rating_label == "Fullness Rating":
        rating_to_search = Post.fullness

    else:
        rating_to_search = Post.satisfaction

    return rating_to_search


def get_post_object(point_data, patient_id):
    """Get a post from data collected when user clicked on a ratings chart."""

    rating_label = point_data.get("ratingLabel")
    rating_to_search = get_rating_label_to_search(rating_label)

    # Get meal_time from  form and convert from isoformat to a datetime object.
    meal_time_isoformat = point_data.get("postDatetime")
    post_meal_time = datetime.strptime(meal_time_isoformat, "%Y-%m-%dT%H:%M:%S")

    rating_value = point_data.get("ratingValue")

    post = Post.query.filter(Post.meal_time==post_meal_time,
                             Post.patient_id==patient_id,
                             rating_to_search==rating_value).first()

    return post


def create_post_dict(patient_id, post_obj):
    """Return a dictionary with a post object."""

    edited = " (edited)" if post_obj.edited else ""

    post_dict = {"patient": {"patient_id": patient_id,
                             "fname": post_obj.patient.fname,
                             "lname": post_obj.patient.lname},
                 "post": {"post_id": post_obj.post_id,
                          "time_stamp": post_obj.time_stamp.isoformat(),
                          "edited": edited,
                          "img_path": post_obj.img_path,
                          "meal_time": post_obj.meal_time.isoformat(),
                          "meal_setting": post_obj.meal_setting,
                          "TEB": post_obj.TEB,
                          "hunger": post_obj.hunger,
                          "fullness": post_obj.fullness,
                          "satisfaction": post_obj.satisfaction,
                          "meal_notes": post_obj.meal_notes},
                 "comments": {}}

    comments = post_obj.comments
    
    if comments:
        post_dict_comments = add_comments_to_post_dict(patient_id, comments, 
                                                       post_dict)
        return post_dict_comments

    return post_dict


def add_comments_to_post_dict(patient_id, comments, post_dict):
    """Add comments to a dictionary containing a post object."""

    sorted_comments = sort_date_asc(comments)
    patient = Patient.query.get(patient_id)

    for comment in sorted_comments:
        if comment.author_type == "diet":
            author_fname = patient.dietitian.fname
            author_lname = patient.dietitian.lname
        else:
            author_fname = patient.fname
            author_lname = patient.lname

        edited = " (edited)" if comment.edited else ""

        user_type = get_user_type_from_session()

        if ((user_type == "dietitian" and comment.author_type == "diet") 
         or (user_type == "patient" and comment.author_type == "pat")):
            is_author = True
        else:
            is_author = False

        post_dict["comments"][comment.comment_id] = {"comment_id": comment.comment_id,
                                                     "author_fname": author_fname,
                                                     "author_lname": author_lname,
                                                     "comment_body": comment.comment_body,
                                                     "time_stamp": comment.time_stamp.isoformat(),
                                                     "edited": edited,
                                                     "is_author": is_author}

        return post_dict


