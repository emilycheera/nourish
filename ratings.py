from datetime import timedelta, date
from model import db, Post, Patient


def query_for_ratings(patient_obj, post_rating, from_date, to_date):
    """Query the database for ratings made by a patient over a date range."""

    dates_ratings_tuples = (db.session.query(Post.meal_time, post_rating)
                             .filter(Post.patient == patient_obj, 
                             post_rating != None, 
                             Post.meal_time.between(from_date, to_date))
                             .order_by(Post.time_stamp.desc())
                             .all())

    dates_ratings_dicts = []

    for meal_time, rating in dates_ratings_tuples:
        dates_ratings_dicts.append({"meal_time": meal_time.isoformat(),
                                    "rating": rating})

    return dates_ratings_dicts


def get_ratings_dict(patient_id, from_date_isoformat, from_date, to_date):
    """Get a dictionary of ratings a patient made over a specific date range."""

    patient = Patient.query.get(patient_id)

    hunger_ratings = query_for_ratings(patient, Post.hunger, from_date, to_date)
    
    fullness_ratings = query_for_ratings(patient, Post.fullness, 
                                         from_date, to_date)
    
    satisfaction_ratings = query_for_ratings(patient, Post.satisfaction,
                                             from_date, to_date)

    return {"data": {"hunger": hunger_ratings,
                     "fullness": fullness_ratings,
                     "satisfaction": satisfaction_ratings,
                     "chart_start_date": from_date_isoformat}}


def get_sundays_with_data(patient_id):
    """Get a list of past Sundays where the following week has ratings data."""

    patient = Patient.query.get(patient_id)

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


