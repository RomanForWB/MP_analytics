from json import load as json_load

_ozon_keys = None
_suppliers = {"tumanyan":
                  {"name": "ИП Туманян А.А.",
                   "seller_identifiers": ["Mi Kar"]},
              "maryina":
                  {"name": "ИП Марьина А.А.",
                   "seller_identifiers": ['ИП Марьина А.А.']},
              "ahmetov":
                  {"name": "ИП Ахметов В.Р.",
                   "seller_identifiers": ["ИП Ахметов В.Р."]}
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


def api_key(supplier):
    """Get ozon seller API key.
    New suppliers and keys can be added in keys/ozon.json.

    :param supplier: one of the suppliers
    :type supplier: str

    :return: ozon key string
    :rtype: str
    """
    global _ozon_keys
    if _ozon_keys is None:
        with open("keys/ozon.json", "r") as json_file:
            _ozon_keys = json_load(json_file)
    return _ozon_keys[supplier]['api_key']


def client_id(supplier):
    """Get ozon client (seller) id.
    New suppliers can be added in keys/ozon.json.

    :param supplier: one of the suppliers
    :type supplier: str

    :return: ozon client id
    :rtype: int
    """
    global _ozon_keys
    if _ozon_keys is None:
        with open("keys/ozon.json", "r") as json_file:
            _ozon_keys = json_load(json_file)
    return _ozon_keys[supplier]['client_id']
