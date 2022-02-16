from datetime import date, timedelta
import requests
import modules.ozon.info as ozon_info
import modules.async_requests as async_requests
import modules.ozon.analytics as ozon_analytics
import modules.info as info


def _fetch_positions_by_sku_list(headers, sku_list, start_date):
    url_list = [f'https://mpstats.io/api/oz/get/item/{sku}/by_category' for sku in sku_list]
    params = {'d1': str(start_date), 'd2': str(date.today())}
    positions_dict = async_requests.by_urls('GET', url_list, sku_list,
                                            params=params,
                                            headers=headers,
                                            content_type='json')
    return positions_dict


def _fetch_positions_by_supplier(headers, supplier, start_date):
    products_list = ozon_analytics.fetch_products(supplier=supplier)
    sku_list = [product['sku'] for product in products_list]
    return _fetch_positions_by_sku_list(headers, sku_list, start_date)


def _fetch_positions_by_suppliers_list(headers, suppliers_list, start_date):
    products_dict = ozon_analytics.fetch_products(suppliers_list=suppliers_list)
    return {supplier: _fetch_positions_by_sku_list(headers,
                                                   [product['sku'] for product in products_dict[supplier]],
                                                   start_date)
            for supplier in suppliers_list}


def _fetch_info_by_supplier(headers, supplier):
    url = 'https://mpstats.io/api/oz/get/seller'
    body = {"startRow": 0, "endRow": 5000}
    items = list()
    for identifier in ozon_info.seller_identifiers(supplier):
        params = {'path': identifier}
        response = requests.post(url, headers=headers, json=body, params=params)
        items += response.json()['data']
    return items


def _fetch_info_by_suppliers_list(headers, suppliers_list):
    print("Получение информации о поставщиках...")
    return {supplier: _fetch_info_by_supplier(headers, supplier) for supplier in suppliers_list}


def _fetch_info_by_sku_list(headers, sku_list):
    suppliers_info_dict = _fetch_info_by_suppliers_list(headers, ozon_info.all_suppliers())
    info_dict = {supplier: [] for supplier in suppliers_info_dict.keys()}
    for supplier, items in suppliers_info_dict.items():
        for item in items:
            if item['id'] in sku_list: info_dict[supplier].append(item)
    return info_dict


def _positions_by_sku_list(sku_list, start_date):
    positions_dict = fetch_positions(sku_list=sku_list, start_date=start_date)
    fetched_info_dict = fetch_info(sku_list=sku_list)
    info_dict = {supplier: {item['id']: item for item in fetched_info}
                 for supplier, fetched_info in fetched_info_dict.items()}
    products_dict = ozon_analytics.fetch_products(suppliers_list=ozon_info.all_suppliers())
    table = list()
    for supplier in ozon_info.all_suppliers():
        supplier_table = list()
        for product in products_dict[supplier]:
            if product['sku'] not in sku_list: continue
            else:
                sku = product['sku']
                category = info_dict[supplier][sku]['category']
                positions_list = positions_dict[sku]['categories'][category]
                for i in range(len(positions_list)):
                    if positions_list[i] == 'NaN': positions_list[i] = '-'
                supplier_table.append([ozon_info.supplier_name(supplier), sku,
                                       product['offer_id'],
                                       category, info_dict[supplier][sku]['brand']] + positions_list)
        table += sorted(supplier_table, key=lambda item: item[2])
    return table


def _positions_by_suppliers_list(suppliers_list, start_date):
    positions_dict = fetch_positions(suppliers_list=suppliers_list, start_date=start_date)
    fetched_info_dict = fetch_info(suppliers_list=suppliers_list)
    info_dict = {supplier: {item['id']: item for item in fetched_info}
                 for supplier, fetched_info in fetched_info_dict.items()}
    products_dict = ozon_analytics.fetch_products(suppliers_list=suppliers_list)
    table = list()
    for supplier in suppliers_list:
        supplier_table = list()
        for product in products_dict[supplier]:
            sku = product['sku']
            category = info_dict[supplier][sku]['category']
            positions_list = positions_dict[supplier][sku]['categories'][category]
            for i in range(len(positions_list)):
                if positions_list[i] == 'NaN': positions_list[i] = '-'
            supplier_table.append([ozon_info.supplier_name(supplier), sku,
                                   product['offer_id'],
                                   category, info_dict[supplier][sku]['brand']] + positions_list)
        table += sorted(supplier_table, key=lambda item: item[2])
    return table


def _positions_by_supplier(supplier, start_date):
    positions_dict = fetch_positions(supplier=supplier, start_date=start_date)
    info_dict = {item['id']: item for item in fetch_info(supplier=supplier)}
    products_list = ozon_analytics.fetch_products(supplier=supplier)
    table = list()
    for product in products_list:
        sku = product['sku']
        category = info_dict[sku]['category']
        positions_list = positions_dict[sku]['categories'][category]
        for i in range(len(positions_list)):
            if positions_list[i] == 'NaN': positions_list[i] = '-'
        table.append([ozon_info.supplier_name(supplier), sku,
                      product['offer_id'],
                      category, info_dict[sku]['brand']] + positions_list)
    return sorted(table, key=lambda item: item[2])


def fetch_info(supplier=None, suppliers_list=None, sku=None, sku_list=None):
    headers = {'X-Mpstats-TOKEN': info.mpstats_token(),
               'Content-Type': 'application/json'}
    if supplier is None \
        and suppliers_list is None \
        and sku_list is None \
        and sku is None: raise AttributeError("No input data to fetch info.")
    elif supplier is not None: return _fetch_info_by_supplier(headers, supplier)
    elif suppliers_list is not None: return _fetch_info_by_suppliers_list(headers, suppliers_list)
    elif sku is not None: return _fetch_info_by_sku_list(headers, [sku])
    elif sku_list is not None: return _fetch_info_by_sku_list(headers, sku_list)


def fetch_positions(supplier=None, suppliers_list=None, sku_list=None, sku=None,
                    start_date=str(date.today()-timedelta(days=7))):
    headers = {'X-Mpstats-TOKEN': info.mpstats_token(),
               'Content-Type': 'application/json'}
    if supplier is None \
        and suppliers_list is None \
        and sku_list is None \
        and sku is None: raise AttributeError("No input data to fetch positions.")
    elif supplier is not None: return _fetch_positions_by_supplier(headers, supplier, start_date)
    elif suppliers_list is not None: return _fetch_positions_by_suppliers_list(headers, suppliers_list, start_date)
    elif sku is not None: return _fetch_positions_by_sku_list(headers, [sku], start_date)
    elif sku_list is not None: return _fetch_positions_by_sku_list(headers, sku_list, start_date)


def positions(input_data, start_date):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд'] + \
             info.days_list(start_date, to_yesterday=True)
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _positions_by_suppliers_list(input_data, start_date)
        elif type(input_data[0]) == int: table = _positions_by_sku_list(input_data, start_date)
    elif type(input_data) == str: table = _positions_by_supplier(input_data, start_date)
    elif type(input_data) == int: table = _positions_by_sku_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table

