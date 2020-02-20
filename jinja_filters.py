"""Define custom jinja filters used for formatting datetime objects."""

def datetimeformat(value, format="%b %-d, %Y at %-I:%M %p"):
    return value.strftime(format)

def dateformat(value, format="%m-%d-%Y"):
    return value.strftime(format)

def htmldateformat(value, format="%Y-%m-%dT%H:%M"):
    return value.strftime(format)
