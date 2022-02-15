from datetime import date, timedelta
import requests
import modules.wildberries.info as wb_info
import modules.async_requests as async_requests
import modules.wildberries.analytics as wb_analytics


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


def _fetch_positions_by_nm_list(headers, nm_list, start_date):
    url_list = [f'https://mpstats.io/api/wb/get/item/{nm}/by_category' for nm in nm_list]
    params = {'d1': str(start_date), 'd2': str(date.today())}
    positions_dict = async_requests.by_urls('GET', url_list, nm_list,
                                            params=params,
                                            headers=headers,
                                            content_type='json')
    return positions_dict


def _fetch_info_by_supplier(headers, supplier):
    url = 'https://mpstats.io/api/wb/get/seller'
    body = {"startRow": 0, "endRow": 5000}
    items = list()
    for identifier in wb_info.seller_identifiers(supplier):
        params = {'path': identifier}
        response = requests.post(url, headers=headers, json=body, params=params)
        items += response.json()['data']
    return items


def _fetch_info_by_suppliers_list(headers, suppliers_list):
    print("Получение информации о категориях...")
    return {supplier: _fetch_info_by_supplier(headers, supplier) for supplier in suppliers_list}


def _fetch_info_by_nm_list(headers, nm_list):
    suppliers_info_dict = _fetch_info_by_suppliers_list(headers, wb_info.all_suppliers())
    info_dict = {supplier: [] for supplier in suppliers_info_dict.keys()}
    for supplier, items in suppliers_info_dict.items():
        for item in items:
            if item['id'] in nm_list: info_dict[supplier].append(item)
    return info_dict


def _positions_by_supplier(supplier, start_date):
    info_dict = {item['id']: item for item in fetch_info(supplier=supplier)}
    cards_list = wb_analytics.fetch_cards(supplier=supplier)
    positions_dict = fetch_positions(supplier=supplier, start_date=start_date)
    table = list()
    for card in cards_list:
        for nomenclature in card['nomenclatures']:
            nm = nomenclature['nmId']
            category = info_dict[nm]['category']
            positions_list = positions_dict[nm]['categories'][category]
            for i in range(len(positions_list)):
                if positions_list[i] == 'NaN': positions_list[i] = '-'
            table.append([wb_info.supplier_name(supplier), nm,
                          card['supplierVendorCode'] + nomenclature['vendorCode'],
                          category, info_dict[nm]['brand']] + positions_list)
    return sorted(table, key=lambda item: item[2])


def _positions_by_suppliers_list(suppliers_list, start_date):
    fetched_info_dict = fetch_info(suppliers_list=suppliers_list)
    info_dict = dict()
    for supplier, fetched_info in fetched_info_dict.items():
        info_dict[supplier] = {item['id']: item for item in fetched_info}
    cards_dict = wb_analytics.fetch_cards(suppliers_list=suppliers_list)
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
                supplier_table.append([wb_info.supplier_name(supplier), nm,
                                       card['supplierVendorCode'] + nomenclature['vendorCode'],
                                       category, info_dict[nm]['brand']] + positions_list)
        result_table += sorted(supplier_table, key=lambda item: item[2])
    return result_table


def _positions_by_nm_list(nm_list, start_date):
    fetched_info_dict = fetch_info(nm_list=nm_list)
    info_dict = dict()
    for supplier, fetched_info in fetched_info_dict.items():
        info_dict[supplier] = {item['id']: item for item in fetched_info}
    cards_dict = wb_analytics.fetch_cards(suppliers_list=list(info_dict.keys()))
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
                        supplier_table.append([wb_info.supplier_name(supplier), nm,
                                               card['supplierVendorCode'] + nomenclature['vendorCode'],
                                               category, info_dict[supplier][nm]['brand']] + positions_list)
                    except TypeError:
                        supplier_table.append([wb_info.supplier_name(supplier), nm,
                                               card['supplierVendorCode'] + nomenclature['vendorCode'],
                                               category, info_dict[supplier][nm]['brand']] +
                                              ['-']*len(positions_dict[nm]['days']))
        result_table += sorted(supplier_table, key=lambda item: item[2])
    return result_table


def _categories_by_supplier(supplier, start_date):
    days = wb_info.days_list(start_date, to_yesterday=True)
    cards_list = wb_analytics.fetch_cards(supplier=supplier)
    positions_dict = fetch_positions(supplier=supplier, start_date=start_date)
    table = list()
    for card in cards_list:
        brand = ''
        for addin in card['addin']:
            if addin['type'] == 'Бренд': brand = addin['params'][0]['value']
        for nomenclature in card['nomenclatures']:
            nm = nomenclature['nmId']
            categories_by_days = list()
            try:
                for i in range(len(days)):
                    categories_raw = [values[i] for values in positions_dict[nm]['categories'].values()]
                    categories_count = len(categories_raw) - categories_raw.count('NaN')
                    categories_by_days.append(categories_count)
                table.append([wb_info.supplier_name(supplier), nm,
                              card['supplierVendorCode'] + nomenclature['vendorCode'],
                                       f"{card['parent']}/{card['object']}", brand] + categories_by_days)
            except AttributeError:
                table.append([wb_info.supplier_name(supplier), nm,
                              card['supplierVendorCode'] + nomenclature['vendorCode'],
                                       f"{card['parent']}/{card['object']}", brand] + ['-'] * len(days))
    return sorted(table, key=lambda item: item[2])


def _categories_by_suppliers_list(suppliers_list, start_date):
    positions_dict = fetch_positions(suppliers_list=suppliers_list, start_date=start_date)
    days = wb_info.days_list(start_date, to_yesterday=True)
    cards_dict = wb_analytics.fetch_cards(suppliers_list=suppliers_list)
    result_table = list()
    for supplier, cards in cards_dict.items():
        supplier_table = list()
        for card in cards:
            brand = ''
            for addin in card['addin']:
                if addin['type'] == 'Бренд': brand = addin['params'][0]['value']
            for nomenclature in card['nomenclatures']:
                nm = nomenclature['nmId']
                categories_by_days = list()
                try:
                    for i in range(len(days)):
                        categories_raw = [values[i] for values in positions_dict[nm]['categories'].values()]
                        categories_count = len(categories_raw) - categories_raw.count('NaN')
                        categories_by_days.append(categories_count)
                    supplier_table.append([wb_info.supplier_name(supplier), nm,
                                           card['supplierVendorCode'] + nomenclature['vendorCode'],
                                           f"{card['parent']}/{card['object']}", brand] + categories_by_days)
                except AttributeError:
                    supplier_table.append([wb_info.supplier_name(supplier), nm,
                                           card['supplierVendorCode'] + nomenclature['vendorCode'],
                                           f"{card['parent']}/{card['object']}", brand] + ['-']*len(days))
        result_table += sorted(supplier_table, key=lambda item: item[2])
    return result_table


def _categories_by_nm_list(nm_list, start_date):
    positions_dict = fetch_positions(nm_list=nm_list, start_date=start_date)
    days = wb_info.days_list(start_date, to_yesterday=True)
    cards_dict = wb_analytics.fetch_cards(suppliers_list=wb_info.all_suppliers())
    result_table = list()
    for supplier, cards in cards_dict.items():
        supplier_table = list()
        for card in cards:
            brand = ''
            for addin in card['addin']:
                if addin['type'] == 'Бренд': brand = addin['params'][0]['value']
            for nomenclature in card['nomenclatures']:
                if nomenclature['nmId'] not in nm_list: continue
                else:
                    nm = nomenclature['nmId']
                    categories_by_days = list()
                    try:
                        for i in range(len(days)):
                            categories_raw = [values[i] for values in positions_dict[nm]['categories'].values()]
                            categories_count = len(categories_raw) - categories_raw.count('NaN')
                            categories_by_days.append(categories_count)
                        supplier_table.append([wb_info.supplier_name(supplier), nm,
                                               card['supplierVendorCode'] + nomenclature['vendorCode'],
                                               f"{card['parent']}/{card['object']}", brand] + categories_by_days)
                    except AttributeError:
                        supplier_table.append([wb_info.supplier_name(supplier), nm,
                                               card['supplierVendorCode'] + nomenclature['vendorCode'],
                                               f"{card['parent']}/{card['object']}", brand] + ['-']*len(days))
        result_table += sorted(supplier_table, key=lambda item: item[2])
    return result_table


def fetch_positions(supplier=None, suppliers_list=None, nm_list=None, nm=None,
                    start_date=str(date.today()-timedelta(days=7))):
    headers = {'X-Mpstats-TOKEN': wb_info.mpstats_token(),
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
    headers = {'X-Mpstats-TOKEN': wb_info.mpstats_token(),
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
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд'] + \
             wb_info.days_list(start_date, to_yesterday=True)
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
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд'] + \
             wb_info.days_list(start_date, to_yesterday=True)
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _categories_by_suppliers_list(input_data, start_date)
        elif type(input_data[0]) == int: table = _categories_by_nm_list(input_data, start_date)
    elif type(input_data) == str: table = _categories_by_supplier(input_data, start_date)
    elif type(input_data) == int: table = _categories_by_nm_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


# ================== тестовые запуски ==================
if __name__ == '__main__': pass
