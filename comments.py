from datetime import datetime
from model import db, Comment
from users import (get_user_type_from_session, get_current_dietitian, 
                   get_current_patient)


def add_post_comment(post_id, form_data):
    """Add a comment to a post in the database."""

    time_stamp = datetime.now()
    comment_body = form_data.get("comment")

    user_type = get_user_type_from_session()

    if user_type == "patient":
        author_type = "pat"
        patient = get_current_patient()
        author_id = patient.patient_id

    else:
        author_type = "diet"
        dietitian = get_current_dietitian()
        author_id = dietitian.dietitian_id

    new_comment = Comment(post_id=post_id,
                          author_type=author_type,
                          author_id=author_id,
                          time_stamp=time_stamp,
                          comment_body=comment_body)

    db.session.add(new_comment)
    db.session.commit()

    return(new_comment)


def edit_post_comment(comment_id, form_data):
    """Update a comment in the database."""

    comment = Comment.query.get(comment_id)
    comment_body = form_data.get("comment")

    comment.comment_body = comment_body
    comment.edited = True

    db.session.add(comment)
    db.session.commit()

    return comment


def delete_comment(comment_id):
    """Delete a comment in the database."""

    comment = Comment.query.get(comment_id)

    db.session.delete(comment)
    db.session.commit()

    return "Success"


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


