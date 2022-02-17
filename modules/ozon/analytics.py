from datetime import date, timedelta, datetime
import modules.ozon.info as ozon_info
import modules.async_requests as async_requests
import requests


def _fetch_product_ids_by_supplier(supplier):
    url = 'https://api-seller.ozon.ru/v1/product/list'
    headers = {'Client-Id': ozon_info.client_id(supplier),
               'Api-Key': ozon_info.api_key(supplier)}
    body = {"filter": {
            "visibility": "VISIBLE"},
            "page": 1,
            "page_size": 5000}
    response = requests.post(url=url, json=body, headers=headers)
    return [item['product_id'] for item in response.json()['result']['items']]


def _fetch_product_ids_by_suppliers_list(suppliers_list):
    return {supplier: _fetch_product_ids_by_supplier(supplier)
            for supplier in suppliers_list}


def _fetch_products_by_supplier(supplier):
    product_id_list = _fetch_product_ids_by_supplier(supplier)
    url = 'https://api-seller.ozon.ru/v2/product/info/list'
    headers = {'Client-Id': ozon_info.client_id(supplier),
               'Api-Key': ozon_info.api_key(supplier)}
    body = {'product_id': product_id_list}
    response = requests.post(url=url, json=body, headers=headers)
    products_list = [product for product in response.json()['result']['items']]
    for i in range(len(products_list)):
        for source in products_list[i]['sources']:
            if source['source'] == 'fbo':
                products_list[i]['sku'] = source['sku']
                break
    return products_list


def _fetch_products_by_suppliers_list(suppliers_list):
    return {supplier: _fetch_products_by_supplier(supplier)
            for supplier in suppliers_list}


def _fetch_categories_by_ids(categories_ids):
    url = 'https://api-seller.ozon.ru/v2/category/tree'
    headers = {'Client-Id': ozon_info.client_id(ozon_info.all_suppliers()[0]),
               'Api-Key': ozon_info.api_key(ozon_info.all_suppliers()[0])}
    bodies_list = [{'category_id': category_id} for category_id in categories_ids]
    result = async_requests.by_bodies('POST', url, bodies_list, categories_ids, headers=headers, content_type='json', lib='httpx')
    return result


def _stocks_by_supplier(supplier):
    products_list = fetch_products(supplier=supplier)
    table = list()
    for product in products_list:
        table.append([ozon_info.supplier_name(supplier), product['sku'],
                      product['offer_id'], ])


def fetch_products(supplier=None, suppliers_list=None):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch cards.")
    elif supplier is not None: return _fetch_products_by_supplier(supplier)
    elif suppliers_list is not None: return _fetch_products_by_suppliers_list(suppliers_list)


def stocks(input_data, start_date=str(date.today()-timedelta(days=7))):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет',
              'На складе', 'В пути', 'Время обновления']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _stocks_by_suppliers_list(input_data, start_date)
        elif type(input_data[0]) == int: table = _stocks_by_nm_list(input_data, start_date)
    elif type(input_data) == str: table = _stocks_by_supplier(input_data, start_date)
    elif type(input_data) == int: table = _stocks_by_nm_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table
