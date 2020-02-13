from model import connect_to_db, db, Dietitian, Patient, Goal, Post, Comment
from server import app


def load_dietitians(dietitian_filename):
    """Load dietitians from u.patient into database."""

    for row in open(dietitian_filename):
        row = row.rstrip()
        fname, lname, email, password, street_address, city, state, zipcode = row.split("|")

        dietitian = Dietitian(fname=fname,
                              lname=lname,
                              email=email,
                              street_address=street_address,
                              city=city,
                              state=state,
                              zipcode=zipcode)

        dietitian.set_password(password)

        db.session.add(dietitian)

    db.session.commit()


def load_patients(patient_filename):
    """Load patients from u.patient into database."""

    for row in open(patient_filename):
        row = row.rstrip()
        dietitian_id, fname, lname, email, password, street_address, city, state, zipcode, phone, birthdate = row.split("|")

        patient = Patient(dietitian_id=dietitian_id,
                          fname=fname,
                          lname=lname,
                          email=email,
                          street_address=street_address,
                          city=city,
                          state=state,
                          zipcode=zipcode,
                          phone=phone,
                          birthdate=birthdate)

        patient.set_password(password)

        db.session.add(patient)

    db.session.commit()


def load_goals(goal_filename):
    """Load goals from u.goal into database."""

    for row in open(goal_filename):
        row = row.rstrip()
        patient_id, time_stamp, goal_body = row.split("|")

        goal = Goal(patient_id=patient_id,
                    time_stamp=time_stamp,
                    goal_body=goal_body)

        db.session.add(goal)

    db.session.commit()


def load_posts(post_filename):
    """Load posts from u.post into database."""

    for row in open(post_filename):
        row = row.rstrip()
        patient_id, post_time, meal_time, img_path, meal_setting, TEB = row.split("|")

        post = Post(patient_id=patient_id,
                    post_time=post_time,
                    meal_time=meal_time,
                    img_path=img_path,
                    meal_setting=meal_setting,
                    TEB=TEB)

        db.session.add(post)

    db.session.commit()


def load_comments(comment_filename):
    """Load comments from u.comment into database."""

    for row in open(comment_filename):
        row = row.rstrip()
        post_id, time_stamp, comment_body = row.split("|")

        comment = Comment(post_id=post_id,
                          time_stamp=time_stamp,
                          comment_body=comment_body)

        db.session.add(comment)

    db.session.commit()



if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    dietitian_filename = "seed_data/u.dietitian"
    patient_filename = "seed_data/u.patient"
    goal_filename = "seed_data/u.goal"
    post_filename = "seed_data/u.post"
    comment_filename = "seed_data/u.comment"

    load_dietitians(dietitian_filename)
    load_patients(patient_filename)
    load_goals(goal_filename)
    load_posts(post_filename)
    load_comments(comment_filename)


