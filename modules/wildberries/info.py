from json import load as json_load

_wb_keys = None
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
                   "seller_identifiers": ["ИП Фурсов И Н"]},
              "lepeshkin":
                  {"name": "ИП Лепешкин Д.И.",
                   "seller_identifiers": ["ИП Лепешкин Д И"]},
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


def api_key(type, supplier):
    """Get wildberries key or token.
    New suppliers and tokens can be added in keys/wb.json.

    :param type: one of: 'token', 'x32', 'x64'
    :type type: str

    :param supplier: one of the suppliers
    :type supplier: str

    :return: wildberries key or token string
    :rtype: str
    """
    global _wb_keys
    if _wb_keys is None:
        with open("keys/wb.json", "r") as json_file:
            _wb_keys = json_load(json_file)
    return _wb_keys[type][supplier]
