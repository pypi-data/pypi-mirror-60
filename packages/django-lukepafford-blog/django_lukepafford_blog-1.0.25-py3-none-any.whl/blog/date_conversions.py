from datetime import datetime


def extract_date_from_title(title):
    """
    Returns a datetime object by parsing the string
    in the format yyyy-mm-dd-name-of-the-post
    """
    pieces = title.split("-")[0:3]
    date_str = "-".join(pieces)
    return datetime.strptime(date_str, "%Y-%m-%d")
