from datetime import timedelta, date, datetime
from flask import session
from model import db, Dietitian, Patient, Post, Goal



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


def reset_password(password, user_object):
    """Reset a user's password in the database."""

    user_object.set_password(password)

    db.session.add(user_object)
    db.session.commit()


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


def get_all_patients_posts(dietitian):
    """Get all of a dietitian's patient's posts, limit to 30."""

    posts = (Post.query.filter(Patient.dietitian_id == dietitian.dietitian_id)
            .join(Patient)
            .join(Dietitian)
            .order_by(Post.time_stamp.desc())
            .limit(30).all())

    return posts


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
        post_dict_comments = add_comments_to_post_dict(patient_id, comments, post_dict)
        return post_dict_comments

    return post_dict


def add_comments_to_post_dict(patient_id, comments, post_dict):
    """Add comments to a dictionary containing a post object."""

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

        post_dict["comments"][comment.comment_id] = {"comment_id": comment.comment_id,
                                                     "author_fname": author_fname,
                                                     "author_lname": author_lname,
                                                     "comment_body": comment.comment_body,
                                                     "time_stamp": comment.time_stamp.isoformat(),
                                                     "edited": edited,
                                                     "is_author": is_author}

        return post_dict      


def sort_date_desc(lst):
    """Sort a list of objects with attribute time_stamp by date descending."""

    return sorted(lst, key=lambda x: x.time_stamp, reverse=True)


def alphabetize_by_lname(lst):
    """Alphabetize a list of objects by their attribute lname."""

    return sorted(lst, key=lambda x: x.lname)


def create_new_goal(patient_id, time_stamp, goal_body):
    """Create a new goal in the database."""

    new_goal = Goal(patient_id=patient_id,
                    time_stamp=time_stamp,
                    goal_body=goal_body)

    db.session.add(new_goal)
    db.session.commit()

    return new_goal


def create_goal_dict(key_name, goal_obj, current_dict=None):
    """Return a dictionary containing goal object(s)."""

    edited = " (edited)" if goal_obj.edited else ""

    single_goal_dict = {"goal_id": goal_obj.goal_id,
                        "time_stamp": goal_obj.time_stamp.isoformat(),
                        "edited": edited,
                        "goal_body": goal_obj.goal_body}

    if current_dict:
        current_dict[key_name] = single_goal_dict
        return current_dict

    else:
        goal_dict = {}
        goal_dict[key_name] = single_goal_dict
        return goal_dict


def create_comment_dict(comment_obj):
    """Return a dictionary containing the comment object."""

    patient = comment_obj.post.patient

    if comment_obj.author_type == "pat":
        fname = patient.fname
        lname = patient.lname

    else:
        dietitian = patient.dietitian
        fname = dietitian.fname
        lname = dietitian.lname

    isoformat_time_stamp = comment_obj.time_stamp.isoformat()
    edited = " (edited)" if comment_obj.edited else ""

    comment = {"user": {"fname": fname,
                        "lname": lname},
               "comment": {"time_stamp": isoformat_time_stamp,
                           "comment_body": comment_obj.comment_body,
                           "edited": edited,
                           "comment_id": comment_obj.comment_id}}

    return comment


def get_list_of_ratings(patient_obj, post_rating, from_date_obj, to_date_obj):
    """Return a list of dates and ratings as dictionaries."""

    dates_ratings_tuples = (db.session.query(Post.meal_time, post_rating)
                             .filter(Post.patient == patient_obj, 
                             post_rating != None, 
                             Post.meal_time.between(from_date_obj, to_date_obj))
                             .all())

    dates_ratings_dicts = []

    for meal_time, rating in dates_ratings_tuples:
        dates_ratings_dicts.append({"meal_time": meal_time.isoformat(),
                                    "rating": rating})

    return dates_ratings_dicts


def get_sundays_with_data(patient):
    """Get a list of past Sundays where the following week has ratings data."""

    dates_with_data = (db.session.query(Post.meal_time)
                         .filter(Post.patient==patient, 
                          ( (Post.hunger != None) | (Post.fullness !=None) | 
                            (Post.satisfaction != None) ))).all()

    sundays_with_data = set()

    for day, in dates_with_data:
        
        # Get the previous Sunday.
        idx = (day.date().weekday() + 1) % 7
        previous_sunday = day.date() - timedelta(idx)
        
        # If the previous Sunday is not in the set, add it.
        if previous_sunday not in sundays_with_data:
            sundays_with_data.add(previous_sunday.isoformat())

    sundays_with_data_list = list(sundays_with_data)
    sorted_data = sorted(sundays_with_data_list)
    
    return sorted_data[::-1]



