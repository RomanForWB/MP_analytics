from datetime import date, timedelta, datetime
from warnings import warn as warning
import requests
import modules.files as files
import modules.async_requests as async_requests
import modules.wildberries as wildberries
from main import supplier_names

seller_identifiers = {"maryina": ["ИП Марьина А А", "ИП Марьина Анна Александровна"],
                      "tumanyan": ["ИП Туманян Арен Арменович"],
                      "neweramedia": ["ООО НЬЮЭРАМЕДИА"],
                      "ahmetov": ["ИП Ахметов В Р", "ИП Ахметов Владимир Рафаэльевич"],
                      "fursov": ["ИП Фурсов И Н"]}
if len(supplier_names) != len(seller_identifiers): warning("Please, fill the sellers identifiers in mpstats module.")

def fetch_categories_and_positions(sku_list,
                                   start_date=date.today()-timedelta(days=30),
                                   end_date=date.today()):
    url_list = [f'https://mpstats.io/api/wb/get/item/{sku}/by_category' for sku in sku_list]
    params = {'d1': str(start_date), 'd2': str(end_date)}
    headers = {'X-Mpstats-TOKEN': files.get_mpstats_token(),
               'Content-Type': 'application/json'}
    items_dict = async_requests.by_urls('GET', url_list, sku_list,
                                        params=params,
                                        headers=headers,
                                        content_type='json')
    return items_dict

def fetch_orders_and_balance(sku_list,
                             start_date=date.today()-timedelta(days=30),
                             end_date=date.today()):
    url_list = [f'https://mpstats.io/api/wb/get/item/{sku}/orders_by_size' for sku in sku_list]
    params = {'d1': str(start_date), 'd2': str(end_date)}
    headers = {'X-Mpstats-TOKEN': files.get_mpstats_token(),
               'Content-Type': 'application/json'}
    items_dict = async_requests.by_urls('GET', url_list, sku_list,
                                        params=params,
                                        headers=headers,
                                        content_type='json')
    return items_dict


def stocks(items_dict, categories_dict):
    # === устранение ненужных размеров ===
    actual_items_dict = dict()
    for sku, value in items_dict.items():
        for day, sizes in value.items():
            for size, balance in sizes.items():
                if size == size.upper():
                    actual_items_dict.setdefault(sku, dict()).setdefault(day, dict())[size] = items_dict[sku][day][size]
    items_dict = actual_items_dict

    days = list()
    for sku, value in items_dict.items():
        for day in value.keys():
            if day not in days: days.append(day)
    days = sorted(days)
    table = list()
    table.append(['SKU', 'Предмет', 'Бренд', 'Размер'] + days)
    for sku, value in items_dict.items():
        try:
            brand = categories_dict[sku].rsplit('/', 1)[1]
            category = categories_dict[sku].rsplit('/', 1)[0]
            left_part = [sku, category, brand]
        except AttributeError:
            left_part = [sku, '-', '-']
        try: sizes = sorted(list(list(value.values())[0].keys()))
        except IndexError:
            table.append(left_part + ['-']*(len(days)+1))
            continue
        for size in sizes:
            right_part = [size]
            for day in days:
                try:
                    stock = value[day][size]['balance']
                    if stock == 'NaN': stock = 0
                    right_part.append(stock)
                except KeyError: right_part.append('-')
            table.append(left_part+right_part)
    return table


# =============== NEW VERSION ===============


def _fetch_positions_by_nm_list(headers, nm_list, start_date):
    url_list = [f'https://mpstats.io/api/wb/get/item/{nm}/by_category' for nm in nm_list]
    params = {'d1': str(start_date), 'd2': str(date.today())}
    positions_dict = async_requests.by_urls('GET', url_list, nm_list,
                                        params=params,
                                        headers=headers,
                                        content_type='json')
    return positions_dict


def _fetch_positions_by_supplier(headers, supplier, start_date):
    nm_list = [item['id'] for item in _fetch_info_by_supplier(headers, supplier)]
    return _fetch_positions_by_nm_list(headers, nm_list, start_date)


def _fetch_positions_by_suppliers_list(headers, suppliers_list, start_date):
    suppliers_info_dict = _fetch_info_by_suppliers_list(headers, suppliers_list)
    suppliers_positions_dict = dict()
    for supplier, items in suppliers_info_dict.items():
        nm_list = [item['id'] for item in items]
        suppliers_positions_dict[supplier] = _fetch_positions_by_nm_list(headers, nm_list, start_date)
    return suppliers_positions_dict


def _fetch_info_by_supplier(headers, supplier):
    url = 'https://mpstats.io/api/wb/get/seller'
    body = {"startRow": 0, "endRow": 5000}
    items = list()
    for identifier in seller_identifiers[supplier]:
        params = {'path': identifier}
        response = requests.post(url, headers=headers, json=body, params=params)
        items += response.json()['data']
    return items


def _fetch_info_by_suppliers_list(headers, suppliers_list):
    print("Получение информации о категориях...")
    return {supplier: _fetch_info_by_supplier(headers, supplier) for supplier in suppliers_list}


def _fetch_info_by_nm_list(headers, nm_list):
    suppliers_info_dict = _fetch_info_by_suppliers_list(headers, list(seller_identifiers.keys()))
    info_dict = {supplier: [] for supplier in suppliers_info_dict.keys()}
    for supplier, items in suppliers_info_dict.items():
        for item in items:
            if item['id'] in nm_list: info_dict[supplier].append(item)
    return info_dict


def _positions_by_supplier(supplier, start_date):
    info_dict = {item['id']: item for item in fetch_info(supplier=supplier)}
    cards_list = wildberries.fetch_cards(supplier=supplier)
    positions_dict = fetch_positions(supplier=supplier, start_date=start_date)
    table = list()
    for card in cards_list:
        for nomenclature in card['nomenclatures']:
            nm = nomenclature['nmId']
            category = info_dict[nm]['category']
            positions_list = positions_dict[nm]['categories'][category]
            for i in range(len(positions_list)):
                if positions_list[i] == 'NaN': positions_list[i] = '-'
            table.append([supplier_names[supplier], nm,
                          card['supplierVendorCode']+nomenclature['vendorCode'],
                          category, info_dict[nm]['brand']] + positions_list)
    table.sort(key=lambda item: item[2])
    return table


def _positions_by_suppliers_list(suppliers_list, start_date):
    fetched_info_dict = fetch_info(suppliers_list=suppliers_list)
    info_dict = dict()
    for supplier, info in fetched_info_dict.items():
        info_dict[supplier] = {item['id']: item for item in info}
    cards_dict = wildberries.fetch_cards(suppliers_list=suppliers_list)
    positions_dict = fetch_positions(suppliers_list=suppliers_list, start_date=start_date)
    result_table = list()
    for supplier in suppliers_list:
        supplier_table = list()
        for card in cards_dict[supplier]:
            for nomenclature in card['nomenclatures']:
                nm = nomenclature['nmId']
                category = info_dict[supplier][nm]['category']
                positions_list = positions_dict[supplier][nm]['categories'][category]
                for i in range(len(positions_list)):
                    if positions_list[i] == 'NaN': positions_list[i] = '-'
                supplier_table.append([supplier_names[supplier], nm,
                              card['supplierVendorCode'] + nomenclature['vendorCode'],
                              category, info_dict[nm]['brand']] + positions_list)
        result_table += sorted(supplier_table, key=lambda item: item[2])
    return result_table


def _positions_by_nm_list(nm_list, start_date):
    fetched_info_dict = fetch_info(nm_list=nm_list)
    info_dict = dict()
    for supplier, info in fetched_info_dict.items():
        info_dict[supplier] = {item['id']: item for item in info}
    cards_dict = wildberries.fetch_cards(suppliers_list=list(info_dict.keys()))
    positions_dict = fetch_positions(nm_list=nm_list, start_date=start_date)
    result_table = list()
    for supplier in info_dict.keys():
        supplier_table = list()
        for card in cards_dict[supplier]:
            for nomenclature in card['nomenclatures']:
                if nomenclature['nmId'] not in nm_list: continue
                else:
                    nm = nomenclature['nmId']
                    category = info_dict[supplier][nm]['category']
                    try:
                        positions_list = positions_dict[nm]['categories'][category]
                        for i in range(len(positions_list)):
                            if positions_list[i] == 'NaN': positions_list[i] = '-'
                        supplier_table.append([supplier_names[supplier], nm,
                                               card['supplierVendorCode'] + nomenclature['vendorCode'],
                                               category, info_dict[supplier][nm]['brand']] + positions_list)
                    except TypeError:
                        supplier_table.append([supplier_names[supplier], nm,
                                               card['supplierVendorCode'] + nomenclature['vendorCode'],
                                               category, info_dict[supplier][nm]['brand']] +
                                              ['-']*len(positions_dict[nm]['days']))
        result_table += sorted(supplier_table, key=lambda item: item[2])
    return result_table


def _categories_by_nm_list(nm_list, start_date, days):
    positions_dict = fetch_positions(nm_list=nm_list, start_date=start_date)
    cards_dict = wildberries.fetch_cards(suppliers_list=list(seller_identifiers.keys()))
    result_table = list()
    for supplier, cards in cards_dict.items():
        supplier_table = list()
        for card in cards:
            for nomenclature in card['nomenclatures']:
                if nomenclature['nmId'] not in nm_list: continue
                else:
                    nm = nomenclature['nmId']
                    categories = list()
                    try:
                        for i in range(len(days)):
                            categories_by_day = [positions[i] for positions in positions_dict[nm]['categories'].values()]
                            categories_count = len(categories_by_day) - categories_by_day.count('NaN')
                            categories.append(categories_count)
                            for type in card['addin']:
                                if type['type'] == 'Бренд': brand = type['params'][0]['value']
                        supplier_table.append([supplier_names[supplier], nm,
                                                card['supplierVendorCode'] + nomenclature['vendorCode'],
                                                f"{card['parent']}/{card['object']}", brand] + categories)
                    except AttributeError:
                        supplier_table.append([supplier_names[supplier], nm,
                                               card['supplierVendorCode'] + nomenclature['vendorCode'],
                                               f"{card['parent']}/{card['object']}", brand] + ['-']*len(days))
        result_table += supplier_table
    return result_table


def fetch_positions(supplier=None, suppliers_list=None, nm_list=None, nm=None,
                    start_date=str(date.today()-timedelta(days=7))):
    headers = {'X-Mpstats-TOKEN': files.get_mpstats_token(),
               'Content-Type': 'application/json'}
    if supplier is None \
        and suppliers_list is None \
        and nm_list is None \
        and nm is None: raise AttributeError("No input data to fetch positions.")
    elif supplier is not None: return _fetch_positions_by_supplier(headers, supplier, start_date)
    elif suppliers_list is not None: return _fetch_positions_by_suppliers_list(headers, suppliers_list, start_date)
    elif nm is not None: return _fetch_positions_by_nm_list(headers, [nm], start_date)
    elif nm_list is not None: return _fetch_positions_by_nm_list(headers, nm_list, start_date)


def fetch_info(supplier=None, suppliers_list=None, nm_list=None, nm=None):
    headers = {'X-Mpstats-TOKEN': files.get_mpstats_token(),
               'Content-Type': 'application/json'}
    if supplier is None \
        and suppliers_list is None \
        and nm_list is None \
        and nm is None: raise AttributeError("No input data to fetch info.")
    elif supplier is not None: return _fetch_info_by_supplier(headers, supplier)
    elif suppliers_list is not None: return _fetch_info_by_suppliers_list(headers, suppliers_list)
    elif nm is not None: return _fetch_info_by_nm_list(headers, [nm])
    elif nm_list is not None: return _fetch_info_by_nm_list(headers, nm_list)


def positions(input_data, start_date):
    days = list()
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    today_date = date.today() - timedelta(days=1)
    intermediate_day = start_date
    while intermediate_day <= today_date:
        days.append(intermediate_day.strftime('%d.%m'))
        intermediate_day += timedelta(days=1)

    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд'] + days
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _positions_by_suppliers_list(input_data, start_date)
        elif type(input_data[0]) == int: table = _positions_by_nm_list(input_data, start_date)
    elif type(input_data) == str: table = _positions_by_supplier(input_data, start_date)
    elif type(input_data) == int: table = _positions_by_nm_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def categories(input_data, start_date):
    days = list()
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    today_date = date.today() - timedelta(days=1)
    intermediate_day = start_date
    while intermediate_day <= today_date:
        days.append(intermediate_day.strftime('%d.%m'))
        intermediate_day += timedelta(days=1)

    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд'] + days
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _categories_by_suppliers_list(input_data, start_date, days)
        elif type(input_data[0]) == int: table = _categories_by_nm_list(input_data, start_date, days)
    elif type(input_data) == str: table = _categories_by_supplier(input_data, start_date, days)
    elif type(input_data) == int: table = _categories_by_nm_list([input_data], start_date, days)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


# ================== тестовые запуски ==================
if __name__ == '__main__':
    sku_list = [44117798,16557761,35663011,35663012,16557765,16557766,12129508,16557769,16557770]
    items_dict = fetch_orders_and_balance(sku_list)
    categories_dict = wildberries.get_category_and_brand(sku_list)
    balance_table = stocks(items_dict, categories_dict)
    for row in balance_table:
        print(row)