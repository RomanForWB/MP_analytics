from json import load as json_load
from datetime import datetime, timedelta, date

_google_keys = None
_wb_keys = None
_paths = None
_mpstats_tokens = None
_suppliers = {"maryina":
                  {"name": "ИП Марьина А.А.",
                   "seller_identifiers": ["ИП Марьина А А", "ИП Марьина Анна Александровна"]},
              "tumanyan":
                  {"name": "ИП Туманян А.А.",
                   "seller_identifiers": ["ИП Туманян Арен Арменович"]},
              "neweramedia":
                  {"name": "ООО НЬЮЭРАМЕДИА",
                   "seller_identifiers": ["ООО НЬЮЭРАМЕДИА"]},
              "ahmetov":
                  {"name": "ИП Ахметов В.Р.",
                   "seller_identifiers": ["ИП Ахметов В Р", "ИП Ахметов Владимир Рафаэльевич"]},
              "fursov":
                  {"name": "ИП Фурсов И.Н.",
                   "seller_identifiers": ["ИП Фурсов И Н"]}
              }


def all_suppliers():
    return list(_suppliers.keys())


def suppliers_names():
    return [values['name'] for supplier, values in _suppliers.items()]


def supplier_by_name(name):
    for supplier, values in _suppliers.items():
        if values["name"] == name: return supplier


def supplier_name(supplier):
    return _suppliers[supplier]["name"]


def seller_identifiers(supplier):
    return _suppliers[supplier]["seller_identifiers"]


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


def wb_key(type, supplier):
    """Get wildberries key or token.
    New suppliers and tokens can be added in keys/wb.json.

    :param type: one of: 'token', 'x32', 'x64'
    :type type: str

    :param supplier: one of the suppliers in supplier's dictionary in main
    :type supplier: str

    :return: wildberries key or token string
    :rtype: str
    """
    global _wb_keys
    if _wb_keys is None:
        with open("keys/wb.json", "r") as json_file:
            _wb_keys = json_load(json_file)
    return _wb_keys[type][supplier]


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
