from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc

db = SQLAlchemy()


class Dietitian(db.Model):
    """A dietitian user."""

    __tablename__ = "dietitians"

    dietitian_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    street_address = db.Column(db.String(100))
    city = db.Column(db.String(40))
    state = db.Column(db.String(2))
    zipcode = db.Column(db.String(11))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
    password_hash = db.Column(db.String(128), nullable=False)
    street_address = db.Column(db.String(100))
    city = db.Column(db.String(40))
    state = db.Column(db.String(2))
    zipcode = db.Column(db.String(11))
    phone = db.Column(db.String(15))
    birthdate = db.Column(db.DateTime)
    hunger_visible = db.Column(db.Boolean, default=False, nullable=False)
    fullness_visible = db.Column(db.Boolean, default=False, nullable=False)
    satisfaction_visible = db.Column(db.Boolean, default=False, nullable=False)


    # Define relationship to dietitian
    dietitian = db.relationship("Dietitian", backref=db.backref("patients"))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):

        return f"<Patient id={self.patient_id}, email={self.email}>"


class Goal(db.Model):
    """A goal written by a dietitian for a particular patient."""

    __tablename__ = "goals"

    goal_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    patient_id = db.Column(db.Integer, 
                           db.ForeignKey("patients.patient_id"))
    time_stamp = db.Column(db.DateTime, nullable=False)
    edited = db.Column(db.Boolean, default=False, nullable=False)
    goal_body = db.Column(db.Text, nullable=False)

    # Define relationship to patient
    patient = db.relationship("Patient", backref=db.backref("goals"))

    def sort_date_desc(self, goals_list):
        return sorted(goals_list,
                      key=lambda x: x.time_stamp,
                      reverse=True)

    def __repr__(self):

        return f"""<Goal id={self.goal_id}, patient={self.patient_id}, time={self.time_stamp}>"""


class Post(db.Model):
    """A post made by a patient."""

    __tablename__ = "posts"

    post_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    patient_id = db.Column(db.Integer, 
                           db.ForeignKey("patients.patient_id"))
    time_stamp = db.Column(db.DateTime, nullable=False)
    edited = db.Column(db.Boolean, default=False, nullable=False)
    meal_time = db.Column(db.DateTime, nullable=False)
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

        return f"""<Post id={self.post_id}, patient={self.patient_id}, time={self.time_stamp}>"""


class Comment(db.Model):
    """A dietitian's comment on a patient's post."""

    __tablename__ = "comments"

    comment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.post_id"))
    author_id = db.Column(db.Integer, nullable=False)
    author_type = db.Column(db.String(5), db.ForeignKey("user_types.type_code"))
    time_stamp = db.Column(db.DateTime, nullable=False)
    edited = db.Column(db.Boolean, default=False, nullable=False)
    comment_body = db.Column(db.Text, nullable=False)

    # Define relationship to post
    post = db.relationship("Post", backref=db.backref("comments"))

    def __repr__(self):

        return f"""<Comment id={self.comment_id}, post={self.post_id}, time={self.time_stamp}>"""


class UserType(db.Model):
    """Types of users."""

    __tablename__ = "user_types"

    type_code = db.Column(db.String(5), primary_key=True)
    user_type_name = db.Column(db.String(15))


def load_test_data():
    """Populate a database with sample data for testing purposes."""

    db.create_all()

    # Empty out data from previous runs.
    Dietitian.query.delete()
    Patient.query.delete()
    Goal.query.delete()
    Post.query.delete()
    Comment.query.delete()

    # Create sample dietitian.
    dietitian = Dietitian(fname="Jane", lname="Doe", email="jdoe@gmail.com",
                          street_address="123 Main St.", city="San Francisco",
                          state="CA", zipcode="55443")
    
    dietitian.set_password("password")

    # Create sample patients.
    patient1 = Patient(dietitian_id=1, fname="Joe", lname="Smith", 
                       email="jsmith@gmail.com", street_address="55 South St.",
                       city="Oakland", state="CA", zipcode="44332",
                       phone="8834498765", birthdate="1976-07-19", 
                       hunger_visible=True, fullness_visible=True,
                       satisfaction_visible=True)
    patient1.set_password("password")

    patient2 = Patient(dietitian_id=1, fname="Jenny", lname="Johnson", 
                       email="jenny@gmail.com", street_address="443 Hiland Rd.",
                       city="Berkeley", state="CA", zipcode="57463",
                       phone="6654432345", birthdate="1996-12-03")
    patient2.set_password("password")

    # Create sample goals.
    goal1 = Goal(patient_id=1, time_stamp="2020-02-03 10:18:53", 
                 goal_body="Keep up the great work with your 3-3-3 meal plan.")
    goal2 = Goal(patient_id=1, time_stamp="2020-02-10 10:22:30",
                 goal_body="Experiment with intuitive eating this week.")

    # Create a sample post.
    post = Post(patient_id=1, time_stamp="2020-02-20 10:04:53", 
                meal_time="2020-02-20 08:00:00", 
                img_path="/static/images/uploads/4.jpg", 
                meal_setting="Home alone in kitchen", 
                TEB="Not feeling hungry but food looks delicious.",
                hunger=2, fullness=8, satisfaction=5)

    # Create a sample comment for the sample post.
    comment = Comment(post_id=1, author_id=1, author_type="diet", 
                      time_stamp="2020-02-20 18:30:10", 
                      comment_body="Your breakfast does look delicious!")

    # Create usertypes data.
    type1 = UserType(type_code="diet", user_type_name="dietitian")
    type2 = UserType(type_code="pat", user_type_name="patient")
    
    db.session.add_all([dietitian, patient1, patient2, goal1, goal2, post, 
                        comment, type1, type2])
    db.session.commit()


def connect_to_db(app, db_uri="postgresql:///nourish"):
    """Connect Flask app to database."""

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config["SQLALCHEMY_ECHO"] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    from server import app
    connect_to_db(app)



