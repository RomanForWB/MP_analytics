import requests
from datetime import date, datetime, timedelta
from copy import deepcopy
import modules.info as info
import modules.ozon.info as ozon_info
import modules.async_requests as async_requests

_product_ids = dict()
_products = dict()
_categories = dict()
_analytics = dict()

def _fetch_product_ids_by_supplier(supplier):
    result = _product_ids.get(supplier)
    url = 'https://api-seller.ozon.ru/v1/product/list'
    headers = {'Client-Id': ozon_info.client_id(supplier),
               'Api-Key': ozon_info.api_key(supplier)}
    body = {"filter": {
        "visibility": "VISIBLE"},
        "page": 1,
        "page_size": 5000}
    if result is None:
        while True:
            try:
                response = requests.post(url=url, json=body, headers=headers)
                result = [item['product_id'] for item in response.json()['result']['items']]
                _product_ids[supplier] = result
                break
            except (requests.exceptions.RequestException, requests.exceptions.BaseHTTPError): pass
    return deepcopy(result)


def _fetch_product_ids_by_suppliers_list(suppliers_list):
    result = _product_ids.get(tuple(suppliers_list))
    if result is None:
        url = 'https://api-seller.ozon.ru/v1/product/list'
        headers_list = [{'Client-Id': ozon_info.client_id(supplier),
                         'Api-Key': ozon_info.api_key(supplier)} for supplier in suppliers_list]
        body = {"filter": {
                "visibility": "VISIBLE"},
                "page": 1,
                "page_size": 5000}
        results_dict = async_requests.fetch('POST', suppliers_list, url=url, headers_list=headers_list,
                                            body=body, content_type='json', lib='httpx')
        result = {supplier: [item['product_id'] for item in result['result']['items']]
                  for supplier, result in results_dict.items()}
        _product_ids[tuple(suppliers_list)] = result
    return deepcopy(result)


def _fetch_products_by_supplier(supplier):
    result = _products.get(supplier)
    if result is None:
        product_ids = _fetch_product_ids_by_supplier(supplier)
        url = 'https://api-seller.ozon.ru/v2/product/info/list'
        headers = {'Client-Id': ozon_info.client_id(supplier),
                   'Api-Key': ozon_info.api_key(supplier)}
        body = {'product_id': product_ids}
        while True:
            try:
                response = requests.post(url=url, json=body, headers=headers)
                result = [product for product in response.json()['result']['items']]
                break
            except (requests.exceptions.RequestException, requests.exceptions.BaseHTTPError): pass
        for i in range(len(result)):
            for source in result[i]['sources']:
                if source['source'] == 'fbo':
                    result[i]['sku'] = source['sku']
                    break
        _products[supplier] = result
    return deepcopy(result)


def _fetch_products_by_suppliers_list(suppliers_list):
    return {supplier: _fetch_products_by_supplier(supplier)
            for supplier in suppliers_list}


def _fetch_categories_by_ids(categories_ids):
    result = _categories.get(tuple(categories_ids))
    if result is None:
        url = 'https://api-seller.ozon.ru/v2/category/tree'
        headers = {'Client-Id': ozon_info.client_id(ozon_info.all_suppliers()[0]),
                   'Api-Key': ozon_info.api_key(ozon_info.all_suppliers()[0])}
        bodies_list = [{'category_id': category_id} for category_id in categories_ids]
        results_dict = async_requests.fetch('POST', categories_ids, url=url, bodies_list=bodies_list,
                                      headers=headers, content_type='json', lib='httpx')
        result = {id: category['result'][0]['title'] for id, category in results_dict.items()}
        _categories[tuple(categories_ids)] = result
    return deepcopy(result)


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


def _fetch_analytics_by_supplier(supplier, start_date):
    result = _analytics.get((supplier, start_date))
    url = 'https://api-seller.ozon.ru/v1/analytics/data'
    headers = {'Client-Id': ozon_info.client_id(supplier),
               'Api-Key': ozon_info.api_key(supplier)}
    body = {"date_from": str(start_date),
            "date_to": str(date.today()),
            "metrics": ["revenue",
                        "ordered_units",
                        "delivered_units",
                        "returns",
                        "cancellations"],
            "dimension": ["day"],
            "limit": 1000,
            "offset": 0}
    if result is None:
        while True:
            try:
                response = requests.post(url, headers=headers, json=body)
                result = {value['dimensions'][0]['id']:
                            {'orders_value': value['metrics'][0],
                             'orders_count': value['metrics'][1],
                             'delivered_count': value['metrics'][2],
                             'returns_count': value['metrics'][3],
                             'cancellations_count': value['metrics'][4]}
                        for value in response.json()['result']['data']}
                _analytics[(supplier, start_date)] = result
                break
            except (requests.exceptions.RequestException, requests.exceptions.BaseHTTPError): pass
    return deepcopy(result)


def _fetch_analytics_by_suppliers_list(suppliers_list, start_date):
    result = _analytics.get((tuple(suppliers_list), start_date))
    url = 'https://api-seller.ozon.ru/v1/analytics/data'
    headers_list = [{'Client-Id': ozon_info.client_id(supplier),
                    'Api-Key': ozon_info.api_key(supplier)} for supplier in suppliers_list]
    body = {"date_from": str(start_date),
            "date_to": str(date.today()),
            "metrics": ["revenue",
                        "ordered_units",
                        "delivered_units",
                        "returns",
                        "cancellations"],
            "dimension": ["day"],
            "limit": 1000,
            "offset": 0}
    if result is None:
        analytics_dict = async_requests.fetch('POST', suppliers_list, url=url, headers_list=headers_list,
                                          body=body, content_type='json', lib='httpx')
        result = {supplier: {value['dimensions'][0]['id']:
                {'orders_value': value['metrics'][0],
                 'orders_count': value['metrics'][1],
                 'delivered_count': value['metrics'][2],
                 'returns_count': value['metrics'][3],
                 'cancellations_count': value['metrics'][4]}
            for value in result['result']['data']} for supplier, result in analytics_dict.items()}
        _analytics[(tuple(suppliers_list), start_date)] = result
    return deepcopy(result)


def _fetch_transactions_by_supplier(supplier, start_date):
    result = _analytics.get((supplier, start_date))
    url = 'https://api-seller.ozon.ru/v3/finance/transaction/totals'
    headers = {'Client-Id': ozon_info.client_id(supplier),
               'Api-Key': ozon_info.api_key(supplier)}
    dates = info.dates_list(from_date=start_date)
    bodies_list = [{"date": {"from": f"{day}T00:00:00.000Z",
                    "to": f"{day}T00:00:00.000Z"},
                    "posting_number": "",
                    "transaction_type": "all"} for day in dates]
    if result is None:
        result_dict = async_requests.fetch('POST', dates, url=url, bodies_list=bodies_list,
                                           headers=headers, content_type='json', lib='httpx')
        result = {day: {'sales_value': result['result']['accruals_for_sale'] + result['result']['refunds_and_cancellations'],
                        'delivery_value': result['result']['processing_and_delivery'],
                        'comission_value': result['result']['sale_commission'],
                        'service_value': result['result']['services_amount'],
                        'total_value': sum(result['result'].values())}
            for day, result in result_dict.items()}
        _analytics[(supplier, start_date)] = result
    return deepcopy(result)


def _fetch_transactions_by_suppliers_list(suppliers_list, start_date):
    return {supplier: _fetch_transactions_by_supplier(supplier, start_date)
            for supplier in suppliers_list}


def _stocks_by_supplier(supplier):
    products_list = fetch_products(supplier=supplier)
    categories_dict = fetch_categories(supplier=supplier)
    table = [[ozon_info.supplier_name(supplier), product['sku'],
             product['offer_id'], categories_dict[product['category_id']],
             product['stocks']['present'], product['stocks']['coming'],
             product['stocks']['reserved'], product['status']['state_updated_at']]
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
                         product['stocks']['reserved'], product['status']['state_updated_at']]
                         for product in products_list])
    return table


def fetch_analytics(supplier=None, suppliers_list=None, start_date=str(date.today()-timedelta(days=6))):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch analytics.")
    elif supplier is not None: return _fetch_analytics_by_supplier(supplier, start_date)
    elif suppliers_list is not None: return _fetch_analytics_by_suppliers_list(suppliers_list, start_date)


def fetch_products(supplier=None, suppliers_list=None):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch products.")
    elif supplier is not None: return _fetch_products_by_supplier(supplier)
    elif suppliers_list is not None: return _fetch_products_by_suppliers_list(suppliers_list)


def fetch_transactions(supplier=None, suppliers_list=None, start_date=str(date.today()-timedelta(days=6))):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch products.")
    elif supplier is not None: return _fetch_transactions_by_supplier(supplier, start_date)
    elif suppliers_list is not None: return _fetch_transactions_by_suppliers_list(suppliers_list, start_date)


def fetch_categories(supplier=None, suppliers_list=None):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch categories.")
    elif supplier is not None: return _fetch_categories_by_supplier(supplier)
    elif suppliers_list is not None: return _fetch_categories_by_suppliers_list(suppliers_list)


def _report_by_supplier(supplier, start_date):
    analytics_dict = fetch_analytics(supplier=supplier, start_date=start_date)
    transactions_dict = fetch_transactions(supplier=supplier, start_date=start_date)
    return [[day.replace('-', '.'), analytics['orders_count'], analytics['orders_value'],
             analytics['delivered_count'] - analytics['returns_count'] - analytics['cancellations_count'],
             transactions_dict[day]['sales_value'], transactions_dict[day]['delivery_value'],
             transactions_dict[day]['comission_value'], transactions_dict[day]['service_value'],
             transactions_dict[day]['total_value']] for day, analytics in analytics_dict.items()]


def _report_by_suppliers_list(suppliers_list, start_date):
    analytics_dict = fetch_analytics(suppliers_list=suppliers_list, start_date=start_date)
    transactions_dict = fetch_transactions(suppliers_list=suppliers_list, start_date=start_date)
    dates = info.dates_list(from_date=start_date, to_yesterday=True)
    table = [[day, sum([analytics_dict[supplier][day]['orders_count'] for supplier in suppliers_list]),
                  sum([analytics_dict[supplier][day]['orders_value'] for supplier in suppliers_list]),
                  sum([analytics_dict[supplier][day]['delivered_count'] - \
                       analytics_dict[supplier][day]['returns_count'] - \
                       analytics_dict[supplier][day]['cancellations_count'] for supplier in suppliers_list]),
                  sum([transactions_dict[supplier][day]['sales_value'] for supplier in suppliers_list]),
                  sum([transactions_dict[supplier][day]['delivery_value'] for supplier in suppliers_list]),
                  sum([transactions_dict[supplier][day]['comission_value'] for supplier in suppliers_list]),
                  sum([transactions_dict[supplier][day]['service_value'] for supplier in suppliers_list]),
                  sum([transactions_dict[supplier][day]['total_value'] for supplier in suppliers_list])]
                  for day in dates]
    return table


def report(input_data, start_date):
    header = ['Дата', 'Заказы шт.', 'Заказы руб.', 'Выкуплено шт.', 'Выкуплено руб.',
              'Доставка руб.', 'Комиссия руб.', 'Доп. услуги руб.', 'К перечислению']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _report_by_suppliers_list(input_data, start_date)
        elif type(input_data[0]) == int: table = _report_by_sku_list(input_data, start_date)
    elif type(input_data) == str: table = _report_by_supplier(input_data, start_date)
    elif type(input_data) == int: table = _report_by_sku_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def stocks(input_data):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет',
              'На складе', 'В пути на склад', 'В пути к клиенту', 'Время обновления']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _stocks_by_suppliers_list(input_data)
        elif type(input_data[0]) == int: table = _stocks_by_sku_list(input_data)
    elif type(input_data) == str: table = _stocks_by_supplier(input_data)
    elif type(input_data) == int: table = _stocks_by_sku_list([input_data])
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table
