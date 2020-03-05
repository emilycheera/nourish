import unittest
from server import app

from model import (db, Dietitian, Patient, Comment, Goal, Post, connect_to_db,
                   load_test_data)
from users import (create_new_dietitian_account, update_dietitian_account,
                   create_new_patient_account, update_patient_account,
                   reset_password, get_current_dietitian, get_current_patient,
                   get_user_type_from_session, get_dietitian_and_patients_list)
from goals import (create_new_goal, edit_patient_goal, delete_goal, create_goal_dict,
                   add_goal_and_get_dict)
from posts import (create_new_post, edit_post, delete_post,
                   get_all_patients_posts, save_customized_patient_post_form,
                   get_rating_label_to_search, get_post_object, create_post_dict)

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

        self.assertIn(b"Dietitian Dashboard", result.data)


    def test_patient_login(self):
        """Make sure login works for a patient."""

        data = {"email": "jsmith@gmail.com", "password": "password"}

        result = self.client.post("/patient-login", data=data,
                                  follow_redirects=True)

        self.assertIn(b"Patient Dashboard", result.data)


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
        edit_patient_goal(1, form_data)
        goal = Goal.query.get(1)

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
        posts = get_all_patients_posts(dietitian)

        self.assertIn("At work", posts[0].meal_setting)
        self.assertIn("Home alone", posts[1].meal_setting)


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


    def test_creating_post_dictionary(self):
        """Test that function returns a dictionary of a post object."""

        post = Post.query.get(1)
        post_dict = create_post_dict(1, post)

        self.assertEqual(post_dict["patient"]["lname"], "Smith")
        




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







    


    







if __name__ == "__main__":
    unittest.main()