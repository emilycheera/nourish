from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Dietitian(db.Model):
    """A dietitian user."""

    __tablename__ = "dietitians"

    dietitian_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.String(100))
    city = db.Column(db.String(40))
    state = db.Column(db.String(2))
    zipcode = db.Column(db.String(11))

    def __repr__(self):

        return f"<Dietitian id={self.dietitian_id}, email={self.email}>"


class Patient(db.Model):
    """A patient user."""

    __tablename__ = "patients"

    patient_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    dietitian_id = db.Column(db.Integer, 
                             db.ForeignKey("dietitians.dietitian_id"))
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.String(100))
    city = db.Column(db.String(40))
    state = db.Column(db.String(2))
    zipcode = db.Column(db.String(11))
    phone = db.Column(db.String(15))
    birthdate = db.Column(db.Datetime)

    # Define relationship to dietitian
    dietitian = db.relationship("Dietitian", backref=db.backref("patients"))

    def __repr__(self):

        return f"<Patient id={self.patient_id}, email={self.email}>"


class Goal(db.Model):
    """A goal written by a dietitian for a particular patient."""

    __tablename__ = "goals"

    goal_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    patient_id = db.Column(db.Integer, 
                           db.ForeignKey("patients.patient_id"))
    time_stamp = db.Column(db.Datetime, nullable=False)
    goal_body = db.Column(db.Text, nullable=False)

    # Define relationship to patient
    patient = db.relationship("Patient", backref=db.backref("goals"))

    def __repr__(self):

        return f"""<Goal id={self.goal_id},
                    patient={self.patient_id},
                    time={self.time_stamp}>"""


class Post(db.Model):
    """A post made by a patient."""

    __tablename__ = "posts"

    post_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    patient_id = db.Column(db.Integer, 
                           db.ForeignKey("patients.patient_id"))
    post_time = db.Column(db.Datetime, nullable=False)
    meal_time = db.Column(db.Datetime, nullable=False)
    img_path = db.Column(db.String)
    meal_setting = db.Column(db.String(200))
    TEB = db.Column(db.Text)
    hunger = db.Column(db.Integer)
    fullness = db.Column(db.Integer)
    satisfaction = db.Column(db.Integer)
    meal_notes = db.Column(db.Text)

    # Define relationship to patient
    patient = db.relationship("Patient", backref=db.backref("posts"))

    def __repr__(self):

        return f"""<Post id={self.post_id},
                    patient={self.patient_id},
                    time={self.time_stamp}>"""

class Comment(db.Model)
    """A dietitian's comment on a patient's post."""

    __tablename__ = "comments"

    comment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.post_id"))
    time_stamp = db.Column(db.Datetime, nullable=False)
    comment_body = db.Column(db.Text, nullable=False)

    # Define relationship to post
    post = db.relationship("Post", backref=db.backref("comments"))

    def __repr__(self):

        return f"""<Comment id={self.comment_id},
                    post={self.post_id},
                    time={self.time_stamp}>"""



# Helper functions
def connect_to_db(app):
    """Connect Flask app to database."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nourish'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    from server import app
    connect_to_db(app)






