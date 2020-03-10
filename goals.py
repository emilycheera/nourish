from copy import copy
from datetime import datetime
from helpers import sort_date_desc
from model import db, Goal, Patient


def get_patients_goals_dict(patient_id, page):
    """Get all goals of a particular patient."""

    all_goals = (Goal.query.filter_by(patient_id=patient_id)
                       .order_by(Goal.time_stamp.desc())
                       .paginate(per_page=10, page=page))

    current_goal = (Goal.query.filter_by(patient_id=patient_id)
                              .order_by(Goal.time_stamp.desc())
                              .first())

    past_goals = copy(all_goals)
    past_goals.items = past_goals.items[1:]

    return {"all_goals": all_goals,
            "past_goals": past_goals, 
            "current_goal": current_goal}


def create_new_goal(patient_id, form_data):
    """Create a new goal in the database."""

    time_stamp = datetime.now()
    goal_body = form_data.get("goal-body")

    new_goal = Goal(patient_id=patient_id,
                    time_stamp=time_stamp,
                    goal_body=goal_body)

    db.session.add(new_goal)
    db.session.commit()

    return new_goal


def edit_patient_goal(goal_id, form_data):
    """Edit a patient goal in the database."""

    goal = Goal.query.get(goal_id)
    goal_body = form_data.get("goal-body")

    goal.goal_body = goal_body
    goal.edited = True

    db.session.add(goal)
    db.session.commit()

    return goal


def delete_goal(goal_id):
    """Delete a goal in the database."""

    goal = Goal.query.get(goal_id)

    db.session.delete(goal)
    db.session.commit()

    return "Success"


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


def add_goal_and_get_dict(patient_id, form_data):
    """Add goal to the database. Return dictionary of new_goal/new_past_goal."""

    # Get list of the patient's goals before new goal is added to check if 
    # there's a previous current goal that needs to be moved to the past 
    # goals section.
    patient = Patient.query.get(patient_id)
    sorted_goals = sort_date_desc(patient.goals)

    new_goal = create_new_goal(patient_id, form_data)

    goals = create_goal_dict("current_goal", new_goal)
    
    # If there's past goals, assign the old current goal as the new past goal
    # and add it to the goals dictionary to be returned as JSON.
    if sorted_goals:
        new_past_goal = sorted_goals[0]
        goals = create_goal_dict("goal", new_past_goal, goals)

    return goals



