import unittest
from server import app

from comments import (edit_post_comment, delete_comment,
                      create_comment_dict)
from model import (db, Dietitian, Patient, Comment, Goal, Post, connect_to_db,
                   load_test_data)
from users import (create_new_dietitian_account, update_dietitian_account,
                   create_new_patient_account, update_patient_account,
                   reset_password)
from goals import (create_new_goal, edit_patient_goal, delete_goal,
                   create_goal_dict, add_goal_and_get_dict)
from posts import (create_new_post, edit_post, delete_post,
                   get_all_patients_posts, save_customized_patient_post_form,
                   get_rating_label_to_search, get_post_object)
from ratings import query_for_ratings, get_ratings_dict, get_sundays_with_data

class BasicTests(unittest.TestCase):
    """Test routes that don't require access to the database or session."""

    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


    def test_homepage(self):
        """Test initial rendering of homepage."""
        
        result = self.client.get("/")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"What type of user are you?", result.data)


    def test_dietitian_registration_form(self):
        """Test initial rendering of dietitian registration form."""
        
        result = self.client.get("/register")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Dietitian Registration", result.data)



class DietitianSessionTests(unittest.TestCase):
    """Test routes that require a logged-in dietitian."""

    def setUp(self):
        """Setup for database function testing."""

        # Get the Flask test client.
        self.client = app.test_client()
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "key"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        with self.client as c:
            with c.session_transaction() as sess:
                sess["dietitian_id"] = 2


    def test_logout(self):
        """Make sure logout works."""

        result = self.client.get("/logout", follow_redirects=True)
        self.assertIn(b"Logout successful", result.data)



class DatabaseTests(unittest.TestCase):
    """Test functions that require access to the database."""

    def setUp(self):
        """Setup for database function testing."""

        # Get the Flask test client.
        self.client = app.test_client()
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        # Connect to the test database.
        connect_to_db(app, db_uri="postgresql:///testnourish") 

        # Create the tables and add the sample data.
        db.create_all()
        load_test_data()
        

    def tearDown(self):
        """Do this after each test."""

        db.session.close()
        db.drop_all()


    def test_dietitian_login(self):
        """Make sure login works for a dietitian."""

        data = {"email": "jdoe@gmail.com", "password": "password"}
        result = self.client.post("/dietitian-login", data=data,
                                  follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Dietitian Dashboard", result.data)

        data = {"email": "jdoe@gmail.com", "password": "pass"}
        result = self.client.post("/dietitian-login", data=data,
                                  follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Incorrect password", result.data)

        data = {"email": "jdoe33@gmail.com", "password": "password"}
        result = self.client.post("/dietitian-login", data=data,
                                  follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"No account with", result.data)


    def test_patient_login(self):
        """Make sure login works for a patient."""

        data = {"email": "jsmith@gmail.com", "password": "password"}
        result = self.client.post("/patient-login", data=data,
                                  follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Patient Dashboard", result.data)

        data = {"email": "jsmith@gmail.com", "password": "pass"}
        result = self.client.post("/patient-login", data=data,
                                  follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Incorrect password", result.data)

        data = {"email": "jsmith33@gmail.com", "password": "password"}
        result = self.client.post("/patient-login", data=data,
                                  follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"No account with", result.data)


    def test_dietitian_registration(self):
        """Test that registration route works correctly with POST method."""

        data = {"fname": "Jill", "lname": "Jones", 
                "email": "jill23@gmail.com", "password": "password", 
                "street-address": "33 Blue St", "city": "San Francisco", 
                "state": "CA", "zipcode": "43223"}
        result = self.client.post("/register", data=data,
                                  follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Successfully registered", result.data)

        data = {"fname": "Jill", "lname": "Doe", 
                "email": "jdoe@gmail.com", "password": "password", 
                "street-address": "33 Blue St", "city": "San Francisco", 
                "state": "CA", "zipcode": "43223"}
        result = self.client.post("/register", data=data,
                                  follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"email address already exists", result.data)


    def test_getting_patients_recent_ratings(self):
        """Test that route returns correct JSON."""

        result = self.client.get("/patient/1/recent-ratings.json")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"fullness", result.data)


    def test_getting_patients_past_ratings(self):
        """Test that route returns correct JSON."""

        result = self.client.get("/patient/1/past-ratings.json?chart-date=2020-02-20")
        
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"fullness", result.data)


    def test_getting_post_from_chart(self):
        """Test that route returns correct JSON."""

        result = self.client.get("/patient/1/get-post.json?ratingLabel=Hunger%20Rating&postDatetime=2020-02-20T08:00:00&ratingValue=2")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"hunger", result.data)


    def test_creating_new_dietitian(self):
        """Test process of registering a dietitian."""

        form_data = {"fname": "Jill", "lname": "Jones", 
                    "email": "jill23@gmail.com", "password": "password", 
                    "street-address": "33 Blue St", "city": "San Francisco", 
                    "state": "CA", "zipcode": "43223"}

        dietitian_id = create_new_dietitian_account(form_data)

        self.assertEqual(2, dietitian_id)


    def test_updating_dietitian_account(self):
        """Test process of updating a dietitian."""
        
        form_data = {"fname": "Jill", "lname": "Jones", 
                    "email": "jill23@gmail.com", "street-address": "33 Blue St", 
                    "city": "San Francisco", "state": "CA", "zipcode": "43223"}

        update_dietitian_account(1, form_data)

        dietitian = Dietitian.query.get(1)
        self.assertEqual("Jill", dietitian.fname)


    def test_reset_password(self):
        """Test process of resetting a password."""

        dietitian = Dietitian.query.get(1)
        reset_password("newpass", dietitian)

        self.assertEqual(True, dietitian.check_password("newpass"))


    def test_creating_new_patient(self):
        """Test process of registering a patient."""

        form_data = {"fname": "Jill", "lname": "Jones", 
                    "email": "jill23@gmail.com", "password": "password", 
                    "street-address": "33 Blue St", "city": "San Francisco", 
                    "state": "CA", "zipcode": "43223", "phone": "8884445555",
                    "birthdate":"1984-05-05"}

        patient_id = create_new_patient_account(form_data)

        self.assertEqual(3, patient_id)


    def test_updating_patient_account(self):
        """Test process of updating a patient."""
        
        form_data = {"fname": "Jill", "lname": "Jones", 
                    "email": "jill23@gmail.com", "password": "password", 
                    "street-address": "33 Blue St", "city": "San Francisco", 
                    "state": "CA", "zipcode": "43223", "phone": "8884445555",
                    "birthdate":"1984-05-05"}

        update_patient_account(1, form_data)

        patient = Patient.query.get(1)
        self.assertEqual("Jill", patient.fname)


    def test_creating_new_goal(self):
        """Test process of adding a new goal."""

        form_data = {"goal-body": "New goal body."}
        goal = create_new_goal(1, form_data)
        
        self.assertEqual("New goal body.", goal.goal_body)


    def test_editing_goal(self):
        """Test process of editing a goal."""

        form_data = {"goal-body": "Goal body edit."}
        goal = edit_patient_goal(1, form_data)

        self.assertEqual("Goal body edit.", goal.goal_body)


    def test_deleting_goal(self):
        """Test process of deleting a goal."""

        delete_goal(1)
        self.assertIsNone(Goal.query.get(1))


    def test_creating_goal_dict(self):
        """Test if function returns dictionary of the goal object."""

        goal = Goal.query.get(1)
        goal_dict = create_goal_dict("goal", goal)

        self.assertIsInstance(goal_dict, dict)
        self.assertEqual(goal_dict["goal"]["goal_body"], goal.goal_body)


    def test_adding_goal_and_getting_dict(self):
        """Test if function returns dictionary with two goals."""

        form_data = {"goal-body": "New goal body."}
        goal_dict = add_goal_and_get_dict(1, form_data)

        self.assertIsInstance(goal_dict, dict)
        self.assertIn("Experiment with", goal_dict["goal"]["goal_body"])
        self.assertIn("New goal", goal_dict["current_goal"]["goal_body"])


    def test_creating_new_post(self):
        """Test process of creating a post."""

        form_data = {"meal-time": "2020-02-25 08:00:00", 
                     "meal-setting": "At home!", "TEB": "Some thoughts..",
                     "hunger": 2, "fullness": 8, "satisfaction": 5,
                     "meal-notes": "Some notes."}
        
        create_new_post(1, "/static/images/uploads/2.jpg", form_data)

        post = Post.query.get(3)

        self.assertIsInstance(post, Post)
        self.assertEqual(post.meal_setting, "At home!")


    def test_editing_post(self):
        """Test process of editing a post."""

        form_data = {"meal-time": "2020-02-25 08:00:00", 
                     "meal-setting": "At home!", "TEB": "Some thoughts..",
                     "hunger": 2, "fullness": 3, "meal-notes": "Some notes."}

        edit_post(1, "/static/images/uploads/2.jpg", form_data)

        post = Post.query.get(1)
        
        self.assertEqual(post.meal_setting, "At home!")
        self.assertEqual(post.satisfaction, None)
        self.assertNotEqual(post.fullness, 8)


    def test_deleting_post(self):
        """Test process of deleting a post."""

        delete_post(1)
        post = Post.query.get(1)
        self.assertEqual(post, None)


    def test_getting_all_patient_posts(self):
        """Test that query returns a list of a patient's posts."""

        dietitian = Dietitian.query.get(1)
        posts = get_all_patients_posts(dietitian, 1)

        self.assertIn("At work", posts.items[0].meal_setting)
        self.assertIn("Home alone", posts.items[1].meal_setting)


    def test_saving_customized_patient_post_form(self):
        """Test that function saves correct information in the database."""

        form_data = {"hunger-visible": None}
        save_customized_patient_post_form(1, form_data)
        
        patient = Patient.query.get(1)
        self.assertEqual(False, patient.hunger_visible)


    def test_getting_rating_label_to_search(self):
        """Test that function returns corrent label."""

        rating = get_rating_label_to_search("Hunger Rating")
        self.assertEqual(rating, Post.hunger)


    def test_getting_post_object(self):
        """Test that a post object is returned."""

        point_data = {"ratingLabel": "Hunger Rating",
                      "postDatetime": "2020-02-20T08:00:00",
                      "ratingValue": 2}
        post = get_post_object(point_data, 1)

        self.assertEqual(post.meal_setting, "Home alone in kitchen")


    def test_editing_post_comment(self):
        """Test process of editing a comment on a post."""

        form_data = {"comment": "Here's my new comment!"}
        new_comment = edit_post_comment(1, form_data)

        self.assertIn("my new comment", new_comment.comment_body)


    def test_deleting_comment(self):
        """Test process of deleting a comment on a post."""

        delete_comment(1)
        comment = Comment.query.get(1)

        self.assertEqual(comment, None)


    def test_creating_comment_dict(self):
        """Test process of creating a dictionary of a comment object."""

        comment = Comment.query.get(1)
        comment_dict = create_comment_dict(comment)

        self.assertIsInstance(comment_dict, dict)
        self.assertEqual(comment_dict["user"]["fname"], "Jane")


    def test_querying_for_ratings(self):
        """Test that query for ratings returns correct list of data."""

        patient = Patient.query.get(1)
        dates_ratings = query_for_ratings(patient, Post.hunger, 
                             "2020-02-19 08:00:00", "2020-02-21 08:00:00")

        self.assertIsInstance(dates_ratings, list)
        self.assertEqual(dates_ratings[0]["rating"], 2)


    def test_getting_ratings_dict(self):
        """Test that function returns dictionary of posts."""

        ratings_dict = get_ratings_dict(1, "2020-02-19T08:00:00", 
                       "2020-02-19 08:00:00", "2020-02-21 08:00:00")

        self.assertIsInstance(ratings_dict, dict)
        self.assertEqual(ratings_dict["data"]["fullness"][0]["rating"], 8)


    def test_getting_sundays_with_data(self):
        """Test that function returns correct list of dates."""

        data = get_sundays_with_data(1)

        self.assertIn(data[0], "2020-02-16")


class DietitianDatabaseTests(unittest.TestCase):
    """Test functions that require a logged-in dietitian and the database."""

    def setUp(self):
        """Setup for database function testing."""

        # Get the Flask test client.
        self.client = app.test_client()
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "key"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        with self.client as c:
            with c.session_transaction() as sess:
                sess["dietitian_id"] = 1

        # Connect to the test database.
        connect_to_db(app, db_uri="postgresql:///testnourish") 

        # Create the tables and add the sample data.
        db.create_all()
        load_test_data()
        

    def tearDown(self):
        """Do this after each test."""

        db.session.close()
        db.drop_all()


    def test_homepage_redirect_patient(self):
        """Test redirect when patient is logged in and visits index route."""

        result = self.client.get("/", follow_redirects=True)

        self.assertIn(b"Dietitian Dashboard", result.data)


    def test_showing_dietitian_homepage(self):
        """Test rendering of the dietitian homepage."""

        result = self.client.get("/dietitian/1")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Dietitian Dashboard", result.data)

        result = self.client.get("/dietitian/2", follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_showing_dietitian_account(self):
        """Test rendering of the dietitian account page."""

        result = self.client.get("/dietitian/1/account")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Account Details", result.data)

        result = self.client.get("/dietitian/2/account", follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_showing_edit_dietitian_account(self):
        """Test rendering of the dietitian edit account page."""

        result = self.client.get("/dietitian/1/account/edit")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Edit your information", result.data)

        result = self.client.get("/dietitian/2/account/edit",
                                 follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_dietitian_edit_account(self):
        """Test that edit dietitian account route works with POST method."""

        data = {"fname": "Jill", "lname": "Jones", 
                "email": "jill23@gmail.com", "street-address": "33 Blue St", 
                "city": "San Francisco", "state": "CA", "zipcode": "43223"}

        result = self.client.post("/dietitian/1/account/edit", data=data,
                                  follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"successfully updated", result.data)


    def test_showing_dietitian_reset_password(self):
        """Test rendering of showing dietitian reset password page."""

        result = self.client.get("/dietitian/1/account/reset-password")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Type in a new password", result.data)

        result = self.client.get("/dietitian/4/account/reset-password",
                                 follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_dietitian_reset_password(self):
        """Test that reset dietitian password route works with POST method."""

        data = {"password": "newpass"}
        result = self.client.post("/dietitian/1/account/reset-password", 
                                  data=data, follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"successfully reset", result.data)


    def test_showing_patient_registration(self):
        """Test rendering of the patient registration page."""

        result = self.client.get("/patient/new-patient")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Register a New Patient", result.data)


    def test_adding_new_patient(self):
        """Test that registering a new patient route works correctly."""

        data = {"dietitian_id": 1, "fname": "Jill", "lname": "Jones", 
                "email": "jill237@gmail.com", "password": "password", 
                "street-address": "33 Blue St", "city": "San Francisco", 
                "state": "CA", "zipcode": "43223", "phone": "8884445555",
                "birthdate":"1984-05-05"}
        result = self.client.post("/patient/new-patient", data=data,
                                  follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"registered new patient", result.data)

        data = {"dietitian_id": 1, "fname": "Jill", "lname": "Jones", 
                "email": "jsmith@gmail.com", "password": "password", 
                "street-address": "33 Blue St", "city": "San Francisco", 
                "state": "CA", "zipcode": "43223", "phone": "8884445555",
                "birthdate":"1984-05-05"}
        result = self.client.post("/patient/new-patient", data=data,
                                  follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"email address already exists", result.data)


    def test_showing_single_patient_overview(self):
        """Test rendering of a single patient overview page."""

        result = self.client.get("/patient/1/account")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Birthdate", result.data)

        result = self.client.get("/patient/4/account",
                                 follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_showing_edit_single_patient_account(self):
        """Test rendering of a single patient account edit page."""

        result = self.client.get("/patient/1/account/edit")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Edit the information below.", result.data)

        result = self.client.get("/patient/4/account/edit",
                                 follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_patient_edit_account(self):
        """Test that edit patient account route works with POST method."""

        data = {"fname": "Jill", "lname": "Jones", "email": "jill23@gmail.com",
                "street-address": "33 Blue St", "city": "San Francisco", 
                "state": "CA", "zipcode": "43223", "phone": "8884445555",
                "birthdate":"1984-05-05"}

        result = self.client.post("/patient/1/account/edit", data=data,
                                  follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"successfully updated", result.data)


    def test_not_authorized_to_reset_patient_password(self):
        """Test that a dietitian can't reset a patient's password."""

        result = self.client.get("/patient/1/account/reset-password",
                                 follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_showing_customize_post_form(self):
        """Test rendering of the customize posts page."""

        result = self.client.get("/patient/1/account/customize-posts")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Place a check", result.data)

        result = self.client.get("/patient/4/account/customize-posts",
                                 follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_customize_post_form(self):
        """Test that customizing patient form route works for POST method."""

        data = {"hunger-visible": None}
        result = self.client.post("/patient/1/account/customize-posts", 
                                  data=data, follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"customization saved", result.data)


    def test_showing_patient_goals(self):
        """Test rendering of the show a patient's goals page."""

        result = self.client.get("/patient/1/goals")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Add a new goal", result.data)

        result = self.client.get("/patient/4/goals", follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_adding_patient_goals(self):
        """Test that adding new patient goal route works with POST method."""

        data = {"goal-body": "New goal body."}
        result = self.client.post("/patient/1/add-goal.json", data=data)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"New goal", result.data)


    def test_editing_patient_goals(self):
        """Test that editing a patient goal route works with POST method."""

        data = {"goal-body": "Edited goal body."}
        result = self.client.post("/goal/1/edit.json", data=data)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Edited goal", result.data)


    def test_deleting_patient_goals(self):
        """Test that deleting a patient goal route works with POST method."""

        data = {"goal": 1}
        result = self.client.post("/delete-goal", data=data)
        goal = Goal.query.get(1)

        self.assertEqual(result.status_code, 200)
        self.assertIsNone(goal)


    def test_showing_single_patient_posts(self):
        """Test rendering of the show a single patient's posts page."""

        result = self.client.get("/patient/1/posts")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Setting:", result.data)

        result = self.client.get("/patient/4/posts", follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_adding_comment(self):
        """Test that adding new comment route works with POST method."""

        data = {"comment": "New comment body."}
        result = self.client.post("/post/1/add-comment.json", data=data)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"New comment", result.data)


    def test_editing_comment(self):
        """Test that editing a comment route works with POST method."""

        data = {"comment": "Edited comment body."}
        result = self.client.post("/comment/1/edit.json", data=data)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Edited comment", result.data)


    def test_deleting_comment_route(self):
        """Test that deleting a comment route works with POST method."""

        data = {"comment": 1}
        result = self.client.post("/delete-comment", data=data)
        comment = Comment.query.get(1)

        self.assertEqual(result.status_code, 200)
        self.assertIsNone(comment)


    def test_redirect_for_patient_home_route(self):
        """Test that URL redirects to patient's account page."""

        result = self.client.get("/patient/1", follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Account Details", result.data)

        result = self.client.get("/patient/4", follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_showing_patient_ratings_chart(self):
        """Test rendering of patient's rating chart."""

        result = self.client.get("/patient/1/ratings-chart")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"view the ratings chart", result.data)

        result = self.client.get("/patient/4/ratings-chart",
                                 follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)



class PatientDatabaseTests(unittest.TestCase):
    """Test functions that require a logged-in patient and the database."""

    def setUp(self):
        """Setup for database function testing."""

        # Get the Flask test client.
        self.client = app.test_client()
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "key"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        with self.client as c:
            with c.session_transaction() as sess:
                sess["patient_id"] = 1

        # Connect to the test database.
        connect_to_db(app, db_uri="postgresql:///testnourish") 

        # Create the tables and add the sample data.
        db.create_all()
        load_test_data()
        

    def tearDown(self):
        """Do this after each test."""

        db.session.close()
        db.drop_all()


    def test_homepage_redirect_patient(self):
        """Test redirect when patient is logged in and visits index route."""

        result = self.client.get("/", follow_redirects=True)

        self.assertIn(b"Patient Dashboard", result.data)
    

    def test_showing_patient_homepage(self):
        """Test rendering of the patient homepage."""

        result = self.client.get("/patient/1")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Patient Dashboard", result.data)

        result = self.client.get("/patient/2", follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_showing_patient_account(self):
        """Test rendering of a single patient overview page."""

        result = self.client.get("/patient/1/account")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Birthdate", result.data)

        result = self.client.get("/patient/4/account",
                                 follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_showing_edit_patient_account(self):
        """Test rendering of a single patient account edit page."""

        result = self.client.get("/patient/1/account/edit")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Edit the information below.", result.data)

        result = self.client.get("/patient/4/account/edit",
                                 follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_patient_edit_account_as_patient(self):
        """Test that edit patient account route works with POST method."""

        data = {"fname": "Jill", "lname": "Jones", "email": "jill23@gmail.com", 
                "street-address": "33 Blue St", "city": "San Francisco", 
                "state": "CA", "zipcode": "43223", "phone": "8884445555", 
                "birthdate":"1984-05-05"}

        result = self.client.post("/patient/1/account/edit", data=data,
                                  follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"successfully updated", result.data)


    def test_showing_patient_reset_password(self):
        """Test rendering of showing patient reset password page."""

        result = self.client.get("/patient/1/account/reset-password")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Type in a new password", result.data)

        result = self.client.get("/patient/4/account/reset-password",
                                 follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_patient_reset_password(self):
        """Test that reset patient password route works with POST method."""

        data = {"password": "newpass"}
        result = self.client.post("/patient/1/account/reset-password", 
                                  data=data, follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"successfully reset", result.data)


    def test_adding_patient_posts(self):
        """Test that adding new patient post route works with POST method."""

        data = {"meal-time": "2020-02-25 08:00:00", 
                "meal-setting": "At home!", "TEB": "Some thoughts..",
                "hunger": 2, "fullness": 8, "satisfaction": 5,
                "meal-notes": "Some notes."}
        
        result = self.client.post("/post/new-post", data=data,
                                  follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Post added successfully", result.data)


    def test_editing_patient_posts(self):
        """Test that editing a patient post route works with POST method."""

        data = {"meal-time": "2020-02-25 08:00:00", 
                "meal-setting": "At home!", "TEB": "Some thoughts..",
                "hunger": 2, "fullness": 3, "meal-notes": "Some notes."}
        
        result = self.client.post("/post/edit/1", data=data,
                                  follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Post updated successfully", result.data)


    def test_deleting_patient_posts(self):
        """Test that deleting a patient post route works with POST method."""

        data = {"post": 1}
        result = self.client.post("/delete-post", data=data)
        post = Post.query.get(1)

        self.assertEqual(result.status_code, 200)
        self.assertIsNone(post)

    def test_adding_comment(self):
        """Test that adding new comment route works with POST method."""

        data = {"comment": "New comment body."}
        result = self.client.post("/post/1/add-comment.json", data=data)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"New comment", result.data)


    def test_showing_patient_goals_as_patient(self):
        """Test rendering of the show a patient's goals page."""

        result = self.client.get("/patient/1/goals")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Goals", result.data)

        result = self.client.get("/patient/4/goals", follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_showing_patient_posts(self):
        """Test rendering of the show a patient's posts page."""

        result = self.client.get("/patient/1/posts")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Setting:", result.data)

        result = self.client.get("/patient/4/posts", follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_showing_patient_ratings_chart_as_patient(self):
        """Test rendering of patient's rating chart."""

        result = self.client.get("/patient/1/ratings-chart")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"button in the sidebar", result.data)

        result = self.client.get("/patient/4/ratings-chart",
                                 follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)


    def test_patient_new_patient_unauthorized(self):
        """Test that a patient is unauthorized to vist new patient route."""

        result = self.client.get("/patient/new-patient")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"not authorized", result.data)



if __name__ == "__main__":
    unittest.main()