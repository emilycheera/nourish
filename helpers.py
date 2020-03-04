

def alphabetize_by_lname(lst):
    """Alphabetize a list of objects by their attribute lname."""

    return sorted(lst, key=lambda x: x.lname)


def sort_date_desc(lst):
    """Sort a list of objects with attribute time_stamp by date descending."""

    return sorted(lst, key=lambda x: x.time_stamp, reverse=True)


def sort_date_asc(lst):
    """Sort a list of objects with attribute time_stamp by date ascending."""

    return sorted(lst, key=lambda x: x.time_stamp)
























