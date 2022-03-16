from datetime import date, timedelta, datetime
from copy import deepcopy
import modules.info as info
import modules.ozon.info as ozon_info
import modules.async_requests as async_requests
import modules.single_requests as single_requests

_product_ids = dict()
_products = dict()
_categories = dict()
_analytics = dict()
_warehouses = dict()

_mpstats_positions = dict()
_mpstats_info = dict()


def _product_ids_by_supplier(supplier):
    result = _product_ids.get(supplier)
    if result is None:
        url = 'https://api-seller.ozon.ru/v1/product/list'
        headers = {'Client-Id': ozon_info.client_id(supplier),
                   'Api-Key': ozon_info.api_key(supplier)}
        body = {"filter": {"visibility": "ALL"}, "page": 1, "page_size": 5000}
        result = [item['product_id'] for item in
                  single_requests.fetch('POST', content_type='json', url=url, body=body, headers=headers)['result']['items']]
        _product_ids[supplier] = result
    return deepcopy(result)


def _product_ids_by_suppliers_list(suppliers_list):
    result = _product_ids.get(tuple(suppliers_list))
    if result is None:
        url = 'https://api-seller.ozon.ru/v1/product/list'
        headers_list = [{'Client-Id': ozon_info.client_id(supplier),
                         'Api-Key': ozon_info.api_key(supplier)} for supplier in suppliers_list]
        body = {"filter": {"visibility": "ALL"}, "page": 1, "page_size": 5000}
        results_dict = async_requests.fetch('POST', suppliers_list, url=url, headers_list=headers_list,
                                            body=body, content_type='json', lib='httpx')
        result = {supplier: [item['product_id'] for item in result['result']['items']]
                  for supplier, result in results_dict.items()}
        _product_ids[tuple(suppliers_list)] = result
    return deepcopy(result)


def _products_by_supplier(supplier):
    result = _products.get(supplier)
    if result is None:
        product_ids = _product_ids_by_supplier(supplier)
        url = 'https://api-seller.ozon.ru/v2/product/info/list'
        headers = {'Client-Id': ozon_info.client_id(supplier),
                   'Api-Key': ozon_info.api_key(supplier)}
        body = {'product_id': product_ids}
        product_list = single_requests.fetch('POST', content_type='json', url=url,
                                       body=body, headers=headers)['result']['items']
        result = list()
        for i in range(len(product_list)):
            for source in product_list[i]['sources']:
                product = deepcopy(product_list[i])
                product.pop('sources')
                product['source'] = source['source']
                product['sku'] = source['sku']
                result.append(product)
        _products[supplier] = result
    return deepcopy(result)


def _products_by_suppliers_list(suppliers_list):
    return {supplier: _products_by_supplier(supplier)
            for supplier in suppliers_list}


def products(supplier=None, suppliers_list=None):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch products.")
    elif supplier is not None: return _products_by_supplier(supplier)
    elif suppliers_list is not None: return _products_by_suppliers_list(suppliers_list)


def _categories_by_ids(categories_ids):
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


def _categories_by_supplier(supplier):
    products_list = products(supplier=supplier)
    category_ids = list(set([product['category_id'] for product in products_list]))
    return _categories_by_ids(category_ids)


def _categories_by_suppliers_list(suppliers_list):
    products_dict = products(suppliers_list=suppliers_list)
    category_ids = list()
    for supplier, products_list in products_dict.items():
        for product in products_list: category_ids.append(product['category_id'])
    return _categories_by_ids(list(set(category_ids)))


def categories(supplier=None, suppliers_list=None):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch categories.")
    elif supplier is not None: return _categories_by_supplier(supplier)
    elif suppliers_list is not None: return _categories_by_suppliers_list(suppliers_list)


def _warehouses_by_supplier(supplier):
    result = _analytics.get(supplier)
    if result is None:
        url = f'https://api-seller.ozon.ru/v1/analytics/stock_on_warehouses'
        headers = {'Client-Id': ozon_info.client_id(supplier),
                   'Api-Key': ozon_info.api_key(supplier),
                   'Content-Type': 'application/json'}
        body = {'limit': 1000}
        result = single_requests.fetch('POST', url=url, headers=headers, body=body, content_type='json')['total_items']
        _warehouses[supplier] = result
    return deepcopy(result)


def _warehouses_by_suppliers_list(suppliers_list):
    result = _analytics.get(tuple(suppliers_list))
    if result is None:
        url = f'https://api-seller.ozon.ru/v1/analytics/stock_on_warehouses'
        headers_list = [{'Client-Id': ozon_info.client_id(supplier),
                   'Api-Key': ozon_info.api_key(supplier),
                   'Content-Type': 'application/json'} for supplier in suppliers_list]
        body = {'limit': 1000}
        result = async_requests.fetch('POST', suppliers_list, url=url, headers_list=headers_list,
                                      body=body, content_type='json', lib='httpx')
        result = {supplier: values['total_items'] for supplier, values in result.items()}
        _warehouses[tuple(suppliers_list)] = result
    return deepcopy(result)


def warehouses(supplier=None, suppliers_list=None):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch warehouses.")
    elif supplier is not None: return _warehouses_by_supplier(supplier)
    elif suppliers_list is not None: return _warehouses_by_suppliers_list(suppliers_list)


def _report_by_supplier(supplier, start_date):
    result = _analytics.get((supplier, start_date))
    if result is None:
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
        result = {value['dimensions'][0]['id']:
                            {'orders_value': value['metrics'][0],
                             'orders_count': value['metrics'][1],
                             'delivered_count': value['metrics'][2],
                             'returns_count': value['metrics'][3],
                             'cancellations_count': value['metrics'][4]}
                        for value in single_requests.fetch('POST', content_type='json', url=url, body=body,
                                                           headers=headers)['result']['data']}
        _analytics[(supplier, start_date)] = result
    return deepcopy(result)


def _report_by_suppliers_list(suppliers_list, start_date):
    result = _analytics.get((tuple(suppliers_list), start_date))
    if result is None:
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


def report(supplier=None, suppliers_list=None, start_date=str(date.today() - timedelta(days=6))):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch analytics.")
    elif supplier is not None: return _report_by_supplier(supplier, start_date)
    elif suppliers_list is not None: return _report_by_suppliers_list(suppliers_list, start_date)


def _orders_by_supplier(supplier, start_date):
    result = _analytics.get((supplier, start_date))
    if result is None:
        result_list = list()
        offset = 0
        while True:
            url = 'https://api-seller.ozon.ru/v1/analytics/data'
            headers = {'Client-Id': ozon_info.client_id(supplier),
                       'Api-Key': ozon_info.api_key(supplier)}
            body = {"date_from": str(start_date),
                    "date_to": str(date.today()),
                    "metrics": ["revenue",
                                "ordered_units"],
                    "dimension": ["day", 'sku'],
                    "limit": 1000,
                    "offset": offset}
            analytic_list = single_requests.fetch('POST', content_type='json', url=url, body=body,
                                                           headers=headers)['result']['data']
            if len(analytic_list) < 1: break
            else:
                result_list += analytic_list
                offset += 1000
        result = dict()
        for item in result_list:
            day = item['dimensions'][0]['id']
            sku = int(item['dimensions'][1]['id'])
            result.setdefault(sku, {day: {'orders_value': 0, 'orders_count': 0} for day in info.dates_list(start_date)})
            result[sku][day] = {'orders_value': item['metrics'][0],
                                'orders_count': item['metrics'][1]}
        _analytics[(supplier, start_date)] = result
    return deepcopy(result)


def _orders_by_suppliers_list(suppliers_list, start_date):
    return {supplier: _orders_by_supplier(supplier, start_date)
            for supplier in suppliers_list}


def orders(supplier=None, suppliers_list=None, start_date=str(date.today() - timedelta(days=7))):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch analytics.")
    elif supplier is not None: return _orders_by_supplier(supplier, start_date)
    elif suppliers_list is not None: return _orders_by_suppliers_list(suppliers_list, start_date)


def _transactions_by_supplier(supplier, start_date):
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


def _transactions_by_suppliers_list(suppliers_list, start_date):
    return {supplier: _transactions_by_supplier(supplier, start_date)
            for supplier in suppliers_list}


def transactions(supplier=None, suppliers_list=None, start_date=str(date.today()-timedelta(days=6))):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch products.")
    elif supplier is not None: return _transactions_by_supplier(supplier, start_date)
    elif suppliers_list is not None: return _transactions_by_suppliers_list(suppliers_list, start_date)


# ==============================================


def _mpstats_positions_by_sku_list(headers, sku_list, start_date):
    result = _mpstats_positions.get(tuple(sku_list))
    if result is None:
        start_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=1)).date()
        urls_list = [f'https://mpstats.io/api/oz/get/item/{sku}/by_category' for sku in sku_list]
        params = {'d1': str(start_date), 'd2': str(date.today())}
        result = async_requests.fetch('GET', sku_list, urls_list=urls_list,
                                      params=params, headers=headers, content_type='json')
        _mpstats_positions[tuple(sku_list)] = result
    return deepcopy(result)


def _mpstats_positions_by_supplier(headers, supplier, start_date):
    products_list = _mpstats_info_by_supplier(headers, supplier)
    sku_list = [product['id'] for product in products_list]
    return _mpstats_positions_by_sku_list(headers, sku_list, start_date)


def _mpstats_positions_by_suppliers_list(headers, suppliers_list, start_date):
    products_dict = _mpstats_info_by_suppliers_list(headers, suppliers_list)
    result = {supplier: _mpstats_positions_by_sku_list(headers,
                                                     [product['id'] for product in products_dict[supplier]],
                                                     start_date)
            for supplier in suppliers_list}
    return result


def mpstats_positions(supplier=None, suppliers_list=None, sku_list=None, sku=None,
                      start_date=str(date.today()-timedelta(days=7))):
    headers = {'X-Mpstats-TOKEN': info.mpstats_token(),
               'Content-Type': 'application/json'}
    if supplier is None \
        and suppliers_list is None \
        and sku_list is None \
        and sku is None: raise AttributeError("No input data to fetch positions.")
    elif supplier is not None: return _mpstats_positions_by_supplier(headers, supplier, start_date)
    elif suppliers_list is not None: return _mpstats_positions_by_suppliers_list(headers, suppliers_list, start_date)
    elif sku is not None: return _mpstats_positions_by_sku_list(headers, [sku], start_date)
    elif sku_list is not None: return _mpstats_positions_by_sku_list(headers, sku_list, start_date)


def _mpstats_info_by_supplier(headers, supplier):
    result = _mpstats_info.get(supplier)
    if result is None:
        url = 'https://mpstats.io/api/oz/get/seller'
        body = {"startRow": 0, "endRow": 5000}
        result = list()
        for identifier in ozon_info.seller_identifiers(supplier):
            params = {'path': identifier}
            result += single_requests.fetch('POST', content_type='json', url=url,
                                            body=body, params=params, headers=headers)['data']
        _mpstats_info[supplier] = result
    return deepcopy(result)


def _mpstats_info_by_suppliers_list(headers, suppliers_list):
    return {supplier: _mpstats_info_by_supplier(headers, supplier) for supplier in suppliers_list}


def _mpstats_info_by_sku_list(headers, sku_list):
    suppliers_info_dict = _mpstats_info_by_suppliers_list(headers, ozon_info.all_suppliers())
    info_dict = {supplier: [] for supplier in suppliers_info_dict.keys()}
    for supplier, items in suppliers_info_dict.items():
        for item in items:
            if item['id'] in sku_list: info_dict[supplier].append(item)
    return info_dict


def mpstats_info(supplier=None, suppliers_list=None, sku=None, sku_list=None):
    headers = {'X-Mpstats-TOKEN': info.mpstats_token(),
               'Content-Type': 'application/json'}
    if supplier is None \
        and suppliers_list is None \
        and sku_list is None \
        and sku is None: raise AttributeError("No input data to fetch info.")
    elif supplier is not None: return _mpstats_info_by_supplier(headers, supplier)
    elif suppliers_list is not None: return _mpstats_info_by_suppliers_list(headers, suppliers_list)
    elif sku is not None: return _mpstats_info_by_sku_list(headers, [sku])
    elif sku_list is not None: return _mpstats_info_by_sku_list(headers, sku_list)

