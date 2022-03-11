from json import load as json_load
from copy import deepcopy

_wb_keys = None
_suppliers = {
    "tumanyan":
       {"name": "ИП Туманян А.А.",
        "seller_identifiers": ["ИП Туманян Арен Арменович"]},
    "maryina":
       {"name": "ИП Марьина А.А.",
        "seller_identifiers": ["ИП Марьина А А", "ИП Марьина Анна Александровна"]},
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

_wbxcatalog = {
    'Женщинам': {
        "Брюки": {'id':'pants', 'kind': 2},
        "Верхняя одежда": {'id':'outwear', 'kind': 2},
        "Блузки и рубашки": {'id':'bl_shirts', 'kind': 2},
        "Джемперы, водолазки и кардиганы": {'id':'jumpers_cardigans', 'kind': 2},
        "Джинсы": {'id':'jeans', 'kind': 2},
        "Комбинезоны": {'id':'overalls', 'kind': 2},
        "Костюмы": {'id':'costumes', 'kind': 2},
        "Лонгсливы": {'id':'sweatshirts_hoodies', 'kind': 2},
        "Пиджаки, жилеты и жакеты": {'id':'blazers_wamuses', 'kind': 2},
        "Платья и сарафаны": {'id':'dresses', 'kind': 2},
        "Футболки и топы": {'id':'tops_tshirts', 'kind': 2},
        "Халаты": {'id':'housewear_root', 'kind': 2},
        "Шорты": {'id':'shorts', 'kind': 2},
        "Юбки": {'id':'skirts', 'kind': 2},
        "Белье": {'id':'women_underwear1', 'kind': 2},
        "Большие размеры": {'id':'women_bigsize', 'kind': 2},
        "Будущие мамы": {'id':'moms', 'kind': 2},
        "Для высоких, невысоких": {'id':'short_tall', 'kind': 2},
        "Офис": {'id':'office_bigroot', 'kind': 2},
        "Пляжная мода": {'id':'beach', 'kind': 2},
        "Религиозная": {'id':'religion', 'kind': 2},
        "Свадьба": {'id':'wedding', 'kind': 2},
        "Спецодежда и СИЗы": {'id':'work_clothes', 'kind': 2},
        "Подарки женщинам": {'id':'gift4', 'kind': 2}},
    'Обувь': {
        'Женская': {'id':'women_shoes', 'kind': 2},
        'Мужская': {'id':'men_shoes', 'kind': 1},
        'Ортопедическая обувь': {'id':'shealth', 'xsubject': '33;93;94;95;97;98;99;100;101;102;103;104;105;106;107;109;232;238;283;318;337;343;391;396;749;1025;1658;1664;1716;2400;2411;2771;2772;2793;2956'}
    }}

def wbxcatalog_ids():
    return deepcopy(_wbxcatalog)


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
