from json import load as json_load
from datetime import datetime, timedelta, date




_mpstats_tokens = None
_paths = None
_google_keys = None

def mpstats_token():
    """Get MPStats API token.
    New token can be added in keys/mpstats.json.

    :return: MPStats token
    :rtype: str
    """
    global _mpstats_tokens
    if _mpstats_tokens is None:
        with open("keys/mpstats.json", "r") as json_file:
            _mpstats_tokens = json_load(json_file)
    return _mpstats_tokens['token']


def google_key(identifier):
    """Get google document key.
    Google keys can be expanded in keys/google.json.

    :param identifier: one of: 'wb_analytics'
    :type identifier: str

    :return: google key
    :rtype: str
    """
    global _google_keys
    if _google_keys is None:
        with open("keys/google.json", "r") as json_file:
            _google_keys = json_load(json_file)
    return _google_keys[identifier]


def path(identifier):
    """Get file path by identifier.
    File paths can be expanded in keys/paths.json.

    :param identifier: one of:
        'wb_analytics',
        'notepad++',
        'chrome_driver'
    :type identifier: str

    :return: file path
    :rtype: str
    """
    global _paths
    if _paths is None:
        with open("keys/paths.json", "r") as json_file:
            _paths = json_load(json_file)
    return _paths[identifier]


def days_list(from_date, to_today=True, to_yesterday=False, to_date=None):
    if to_date is not None: to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
    elif to_yesterday: to_date = date.today() - timedelta(days=1)
    elif to_today: to_date = date.today()
    else: raise ValueError("Unable to recognize input data")
    days = list()
    tmp_day = datetime.strptime(from_date, '%Y-%m-%d').date()
    while tmp_day <= to_date:
        days.append(tmp_day.strftime('%d.%m'))
        tmp_day += timedelta(days=1)
    return days


def dates_list(from_date, to_today=True, to_yesterday=False, to_date=None):
    if to_date is not None: to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
    elif to_yesterday: to_date = date.today() - timedelta(days=1)
    elif to_today: to_date = date.today()
    else: raise ValueError("Unable to recognize input data")
    dates = list()
    tmp_date = datetime.strptime(from_date, '%Y-%m-%d').date()
    while tmp_date <= to_date:
        dates.append(tmp_date.strftime('%Y-%m-%d'))
        tmp_date += timedelta(days=1)
    return dates


def current_monday(skip_one=False):
    if skip_one: current_date = datetime.today() - timedelta(days=1)
    else: current_date = datetime.today()
    weekday_number = current_date.isoweekday()
    return (current_date - timedelta(days=(weekday_number - 1))).date()


def current_month_start_date(skip_one=False):
    if skip_one: today = datetime.today() - timedelta(days=1)
    else: today = datetime.today()
    return today.replace(day=1).date()


def next_monday(from_date):
    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    weekday_number = from_date.isoweekday()
    return (from_date + timedelta(days=(8-weekday_number))).date()


def next_month_start_date(from_date):
    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    to_date = from_date.replace(day=28)
    while True:
        to_date += timedelta(days=1)
        if to_date.day == 1: return to_date.date()
