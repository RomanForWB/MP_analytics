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
    url = 'https://api-seller.ozon.ru/v1/product/list'
    headers_list = [{'Client-Id': ozon_info.client_id(supplier),
                     'Api-Key': ozon_info.api_key(supplier)} for supplier in suppliers_list]
    body = {"filter": {
            "visibility": "VISIBLE"},
            "page": 1,
            "page_size": 5000}
    results_dict = async_requests.by_headers('POST', url, headers_list, suppliers_list,
                                             body=body, content_type='json', lib='httpx')
    return {supplier: [item['product_id'] for item in result['result']['items']]
            for supplier, result in results_dict.items()}


def _fetch_products_by_supplier(supplier):
    product_ids = _fetch_product_ids_by_supplier(supplier)
    url = 'https://api-seller.ozon.ru/v2/product/info/list'
    headers = {'Client-Id': ozon_info.client_id(supplier),
               'Api-Key': ozon_info.api_key(supplier)}
    body = {'product_id': product_ids}
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
    return {id: category['result'][0]['title'] for id, category in result.items()}


def _fetch_categories_by_supplier(supplier):
    products_list = fetch_products(supplier=supplier)
    category_ids = list(set([product['category_id'] for product in products_list]))
    return _fetch_categories_by_ids(category_ids)


def _fetch_categories_by_suppliers_list(suppliers_list):
    products_dict = fetch_products(suppliers_list=suppliers_list)
    category_ids = list()
    for supplier, products_list in products_dict.items():
        for product in products_list: category_ids.append(product['category_id'])
    return _fetch_categories_by_ids(list(set(category_ids)))


def _stocks_by_supplier(supplier):
    products_list = fetch_products(supplier=supplier)
    categories_dict = fetch_categories(supplier=supplier)
    table = [[ozon_info.supplier_name(supplier), product['sku'],
             product['offer_id'], categories_dict[product['category_id']],
             product['stocks']['present'], product['stocks']['coming'],
             product['stocks']['reserved'], product['status']]
             for product in products_list]
    return sorted(table, key=lambda item: item[2])


def _stocks_by_suppliers_list(suppliers_list):
    products_dict = fetch_products(suppliers_list=suppliers_list)
    categories_dict = fetch_categories(suppliers_list=suppliers_list)
    table = list()
    for supplier, products_list in products_dict.items():
        table += sorted([[ozon_info.supplier_name(supplier), product['sku'],
                         product['offer_id'], categories_dict[product['category_id']],
                         product['stocks']['present'], product['stocks']['coming'],
                         product['stocks']['reserved'], product['status']]
                         for product in products_list])
    return table


def fetch_products(supplier=None, suppliers_list=None):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch products.")
    elif supplier is not None: return _fetch_products_by_supplier(supplier)
    elif suppliers_list is not None: return _fetch_products_by_suppliers_list(suppliers_list)


def fetch_categories(supplier=None, suppliers_list=None):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch categories.")
    elif supplier is not None: return _fetch_categories_by_supplier(supplier)
    elif suppliers_list is not None: return _fetch_categories_by_suppliers_list(suppliers_list)


def stocks(input_data):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет',
              'На складе', 'В пути на склад', 'В пути к клиенту', 'Время обновления']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _stocks_by_suppliers_list(input_data)
        elif type(input_data[0]) == int: table = _stocks_by_nm_list(input_data)
    elif type(input_data) == str: table = _stocks_by_supplier(input_data)
    elif type(input_data) == int: table = _stocks_by_nm_list([input_data])
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table
