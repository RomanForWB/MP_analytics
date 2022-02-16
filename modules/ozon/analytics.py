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


def fetch_products(supplier=None, suppliers_list=None):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch cards.")
    elif supplier is not None: return _fetch_products_by_supplier(supplier)
    elif suppliers_list is not None: return _fetch_products_by_suppliers_list(suppliers_list)