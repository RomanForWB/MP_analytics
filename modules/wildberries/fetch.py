from datetime import date, timedelta, datetime
from copy import deepcopy
import modules.async_requests as async_requests
import modules.session_requests as session_requests
import modules.single_requests as single_requests
import modules.google_work as google_work
import modules.wildberries.info as wb_info
import modules.info as info
import json, re

_cards = dict()
_day_orders = dict()
_orders = dict()
_stocks = dict()
_report = dict()
_detail_report = dict()
_top_nms = None
_buyouts = None
_cost = None
_cookie_token = None

_mpstats_info = dict()
_mpstats_categories_info = dict()
_mpstats_positions = dict()


def _detail_report_by_supplier(supplier, weeks, last_date=None):
    result = _detail_report.get(supplier)
    url = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/reportDetailByPeriod'
    headers = {'Content-Type': 'application/json'}
    if result is None:
        if last_date is not None: pass
        else:
            last_date = date.today()
            while True:
                last_date -= timedelta(days=1)
                params = {'key': wb_info.api_key('x64', supplier),
                          'dateFrom': str(last_date),
                          'dateTo': str(last_date)}
                first_result = single_requests.fetch('GET', content_type='json', url=url,
                                                     params=params, headers=headers)
                if first_result is not None: break

        params_list = [{'key': wb_info.api_key('x64', supplier),
                                  'dateFrom': str(last_date - timedelta(days=(7*i)+6)),
                                  'dateTo': str(last_date - timedelta(days=7*i))} for i in range(weeks)]
        result_dict = session_requests.fetch('get', [i for i in range(weeks)], params_list=params_list,
                                             url=url, headers=headers, content_type='text', timeout=10)
        result = list()
        for key, value in result_dict.items():
            if value == 'null': pass
            else: result += json.loads(value)
        _detail_report[supplier] = result
    return deepcopy(result)


def _detail_report_by_suppliers_list(suppliers_list, weeks):
    url = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/reportDetailByPeriod'
    headers = {'Content-Type': 'application/json'}
    last_date = date.today()
    while True:
        last_date -= timedelta(days=1)
        params = {'key': wb_info.api_key('x64', suppliers_list[0]),
                  'dateFrom': str(last_date),
                  'dateTo': str(last_date)}
        first_result = single_requests.fetch('GET', content_type='json', url=url,
                                             params=params, headers=headers)
        if first_result is not None: break
    return {supplier: _detail_report_by_supplier(supplier, weeks, last_date=last_date)
            for supplier in suppliers_list}


def detail_report(supplier=None, suppliers_list=None, weeks=4):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch cards.")
    elif supplier is not None: return _detail_report_by_supplier(supplier, weeks)
    elif suppliers_list is not None: return _detail_report_by_suppliers_list(suppliers_list, weeks)


def _cards_by_supplier(url, body, supplier):
    result = _cards.get(supplier)
    headers = {'Authorization': wb_info.api_key('token', supplier)}
    if result is None:
        result = single_requests.fetch('POST', content_type='json', url=url,
                                       body=body, headers=headers)['result']['cards']
        _cards[supplier] = result
    return deepcopy(result)


def _cards_by_suppliers_list(url, body, suppliers_list):
    result = _cards.get(tuple(suppliers_list))
    if result is None:
        headers_list = [{'Authorization': wb_info.api_key('token', supplier)}
                        for supplier in suppliers_list]
        cards_dict = async_requests.fetch('POST', suppliers_list, url=url,
                                          headers_list=headers_list, body=body, content_type='json',
                                          timeout=60)
        result = {supplier: cards_result['result']['cards'] for supplier, cards_result in cards_dict.items()}
        _cards[tuple(suppliers_list)] = result
    return deepcopy(result)


def cards(supplier=None, suppliers_list=None):
    url = "https://suppliers-api.wildberries.ru/card/list"
    body = {"id": 1,
            "jsonrpc": "2.0",
            "params": {
                "withError": False,
                "query": {
                    "limit": 1000
                }
            }
            }
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch cards.")
    elif supplier is not None: return _cards_by_supplier(url, body, supplier)
    elif suppliers_list is not None: return _cards_by_suppliers_list(url, body, suppliers_list)


def _orders_by_supplier(url, headers, supplier, start_date):
    result = _orders.get((supplier, start_date))
    if result is None:
        params = {'key': wb_info.api_key('x64', supplier),
                  'dateFrom': str(start_date)}
        result = single_requests.fetch('GET', content_type='json', url=url,
                                       params=params, headers=headers, timeout=20)
        _orders[(supplier, start_date)] = result
    return deepcopy(result)


def _orders_by_suppliers_list(url, headers, suppliers_list, start_date):
    result = _orders.get((tuple(suppliers_list), start_date))
    if result is None:
        params_list = [{'key': wb_info.api_key('x64', supplier),
                        'dateFrom': str(start_date)} for supplier in suppliers_list]
        result = session_requests.fetch('GET', suppliers_list, content_type='json',
                                      url=url, headers=headers, params_list=params_list, timeout=20)
        _orders[(tuple(suppliers_list), start_date)] = result
    return deepcopy(result)


def orders(supplier=None, suppliers_list=None, start_date=str(date.today()-timedelta(days=6))):
    url = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/orders'
    headers = {'Content-Type': 'application/json'}
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch orders.")
    elif supplier is not None: return _orders_by_supplier(url, headers, supplier, start_date)
    elif suppliers_list is not None: return _orders_by_suppliers_list(url, headers, suppliers_list, start_date)


def _fetch_day_orders_by_supplier(url, headers, supplier, day):
    result = _day_orders.get((supplier, day))
    if result is None:
        print(f'Получение информации о заказах {wb_info.supplier_name(supplier)}..')
        params = {'key': wb_info.api_key('x64', supplier),
                  'dateFrom': str(day), 'flag': 1}
        result = single_requests.fetch('GET', content_type='json', url=url, params=params, headers=headers, timeout=20)
        _day_orders[(supplier, day)] = result
    return deepcopy(result)


def _fetch_day_orders_by_suppliers_list(url, headers, suppliers_list, day):
    return {supplier: _fetch_day_orders_by_supplier(url, headers, supplier, day)
            for supplier in suppliers_list}


def fetch_day_orders(supplier=None, suppliers_list=None, day=str(date.today()-timedelta(days=1))):
    url = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/orders'
    headers = {'Content-Type': 'application/json'}
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch orders.")
    elif supplier is not None: return _fetch_day_orders_by_supplier(url, headers, supplier, day)
    elif suppliers_list is not None: return _fetch_day_orders_by_suppliers_list(url, headers, suppliers_list, day)


def _stocks_by_supplier(url, supplier, start_date):
    result = _stocks.get((supplier, start_date))
    if result is None:
        params = {'key': wb_info.api_key('x64', supplier), 'dateFrom': str(start_date)}
        result = single_requests.fetch('GET', content_type='json', url=url, params=params, timeout=20)
        _stocks[(supplier, start_date)] = result
    return deepcopy(result)


def _stocks_by_suppliers_list(url, suppliers_list, start_date):
    result = _stocks.get((tuple(suppliers_list), start_date))
    if result is None:
        params_list = [{'key': wb_info.api_key('x64', supplier),
                        'dateFrom': str(start_date)}
                       for supplier in suppliers_list]
        result = async_requests.fetch('GET', suppliers_list, url=url,
                                      params_list=params_list, content_type='json')
        _stocks[(tuple(suppliers_list), start_date)] = result
    return deepcopy(result)


def stocks(supplier=None, suppliers_list=None, start_date=str(date.today()-timedelta(days=6))):
    url = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/stocks'
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch stocks.")
    elif supplier is not None: return _stocks_by_supplier(url, supplier, start_date)
    elif suppliers_list is not None: return _stocks_by_suppliers_list(url, suppliers_list, start_date)


def _report_by_supplier(url, supplier):
    result = _report.get(supplier)
    if result is None:
        params = {'isCommussion': 2}
        headers = {'Cookie': f"WBToken={cookie_token(supplier)}; x-supplier-id={wb_info.api_key('cookie_id', supplier)}"}
        result = single_requests.fetch('GET', content_type='json', url=url,
                                       params=params, headers=headers, timeout=20)['data']
        _report[supplier] = result
    return deepcopy(result)


def _report_by_suppliers_list(url, suppliers_list):
    result = _report.get(tuple(suppliers_list))
    if result is None:
        params = {'isCommussion': 2}
        headers_list = [{'Cookie': f"WBToken={cookie_token(supplier)}; x-supplier-id={wb_info.api_key('cookie_id', supplier)}"}
                        for supplier in suppliers_list]
        report_dict = async_requests.fetch('GET', suppliers_list, content_type='json',
                                           url=url, params=params, headers_list=headers_list)
        result = {supplier: report_list['data'] for supplier, report_list in report_dict.items()}
        _report[tuple(suppliers_list)] = result
    return deepcopy(result)


def report(supplier=None, suppliers_list=None):
    url = 'https://seller.wildberries.ru/ns/consolidated/analytics-back/api/v1/consolidated-table'
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch sales.")
    elif supplier is not None: return _report_by_supplier(url, supplier)
    elif suppliers_list is not None: return _report_by_suppliers_list(url, suppliers_list)


def feedbacks(imt_list, count=1000):
    url = 'https://public-feedbacks.wildberries.ru/api/v1/summary/full'
    bodies_list = [{"imtId": imt,
                    "skip": 0,
                    "take": count} for imt in imt_list]
    feedbacks_dict = async_requests.fetch('POST', imt_list, url=url,
                                          bodies_list=bodies_list, content_type='json')
    feedbacks_dict = {imt: feedbacks_info['feedbacks']
                      for imt, feedbacks_info in feedbacks_dict.items()}
    return feedbacks_dict


def top_nms():
    global _top_nms
    result = _top_nms
    if result is None:
        category_ids = wb_info.wbxcatalog_ids()
        wbx_list = list()
        for category, sub_categories in category_ids.items():
            for sub_category, values in sub_categories.items():
                params = {'sort': 'popular', 'page': 1, 'locale': 'ru', 'kind': 2}
                if values.get('kind') is not None: params['kind'] = values['kind']
                if values.get('xsubject') is not None: params['xsubject'] = values['xsubject']
                wbx_list.append([category, sub_category,
                                f"https://wbxcatalog-ru.wildberries.ru/{values['id']}/catalog", params])
        products_dict = async_requests.fetch('GET', ids=[(item[0], item[1]) for item in wbx_list],
                                             urls_list=[item[2] for item in wbx_list],
                                             params_list=[item[3] for item in wbx_list],
                                             content_type='text')
        result = dict()
        for category, sub_categories in category_ids.items():
            result[category] = dict()
            for sub_category in sub_categories.keys():
                result[category][sub_category] = [item['id'] for item in json.loads(products_dict[(category, sub_category)])['data']['products']]
        _top_nms = result
    return deepcopy(result)


def buyouts():
    global _buyouts
    result = _buyouts
    if result is None:
        ws = google_work.open_sheet(info.google_key('wb_day_reports'), 'выкупы')
        buyout_columns = google_work.get_columns(ws, 1, 1, 2, 3, 4)
        buyout_rows = [[buyout_columns[0][i], buyout_columns[1][i], buyout_columns[2][i], buyout_columns[3][i],]
                        for i in range(len(buyout_columns[0]))]
        result = dict()
        for item in buyout_rows:
            try:
                buyout_date = datetime.strptime(item[0], '%d.%m.%Y').strftime('%d.%m')
                nm = int(re.sub(r"[^0-9]", '', item[1]))
                count = int(re.sub(r"[^0-9]", '', item[2]))
                price = int(re.sub(r"[^0-9]", '', item[3]))
                result.setdefault(nm, {'buyouts': []})
                result[nm]['buyouts'].append([buyout_date, count, price])
            except ValueError: pass
        _buyouts = result
    return deepcopy(result)


def cost():
    global _cost
    result = _cost
    if result is None:
        ws = google_work.open_sheet(info.google_key('wb_week_reports'), 'закуп')
        cost_columns = google_work.get_columns(ws, 1, 1, 2, 3)
        result = {'nm': dict(), 'article': dict()}
        for i in range(len(cost_columns[0])):
            try:
                result['nm'][int(cost_columns[1][i])] = int(cost_columns[2][i])
                result['article'][cost_columns[0][i].split('/')[0]+'/'] = int(cost_columns[2][i])
            except ValueError: pass
        _cost = result
    return deepcopy(result)


def cookie_token(supplier):
    global _cookie_token
    result = _cookie_token
    if result is None:
        url = 'https://seller.wildberries.ru/passport/api/v2/auth/login'
        body = {
            "country": "RU",
            "device": "test",
            "token": wb_info.api_key('main_token', supplier)
        }
        single_requests.fetch('POST', content_type='json', url=url, body=body)
        result = single_requests.session.cookies.get_dict()['WBToken']
        _cookie_token = result
    return deepcopy(result)


# ==============================================


def _mpstats_positions_by_supplier(headers, supplier, start_date):
    nm_list = [item['id'] for item in _mpstats_info_by_supplier(headers, supplier)]
    return _mpstats_positions_by_nm_list(headers, nm_list, start_date)


def _mpstats_positions_by_suppliers_list(headers, suppliers_list, start_date):
    suppliers_info_dict = _mpstats_info_by_suppliers_list(headers, suppliers_list)
    suppliers_positions_dict = dict()
    for supplier, items in suppliers_info_dict.items():
        nm_list = [item['id'] for item in items]
        suppliers_positions_dict[supplier] = _mpstats_positions_by_nm_list(headers, nm_list, start_date)
    return suppliers_positions_dict


def _mpstats_positions_by_nm_list(headers, nm_list, start_date):
    result = _mpstats_positions.get(tuple(nm_list))
    if result is None:
        urls_list = [f'https://mpstats.io/api/wb/get/item/{nm}/by_category' for nm in nm_list]
        params = {'d1': str(start_date), 'd2': str(date.today())}
        result = async_requests.fetch('GET', nm_list, urls_list=urls_list, params=params,
                                      headers=headers, content_type='json')
        _mpstats_positions[tuple(nm_list)] = result
    return deepcopy(result)


def mpstats_positions(supplier=None, suppliers_list=None, nm_list=None, nm=None,
                      start_date=str(date.today()-timedelta(days=7))):
    headers = {'X-Mpstats-TOKEN': info.mpstats_token(),
               'Content-Type': 'application/json'}
    if supplier is None \
        and suppliers_list is None \
        and nm_list is None \
        and nm is None: raise AttributeError("No input data to fetch positions.")
    elif supplier is not None: return _mpstats_positions_by_supplier(headers, supplier, start_date)
    elif suppliers_list is not None: return _mpstats_positions_by_suppliers_list(headers, suppliers_list, start_date)
    elif nm is not None: return _mpstats_positions_by_nm_list(headers, [nm], start_date)
    elif nm_list is not None: return _mpstats_positions_by_nm_list(headers, nm_list, start_date)


def _mpstats_info_by_supplier(headers, supplier):
    result = _mpstats_info.get(supplier)
    if result is None:
        url = 'https://mpstats.io/api/wb/get/seller'
        body = {"startRow": 0, "endRow": 5000}
        result = list()
        for identifier in wb_info.seller_identifiers(supplier):
            params = {'path': identifier}
            result += single_requests.fetch('POST', content_type='json', url=url,
                                            body=body, params=params, headers=headers)['data']
        _mpstats_info[supplier] = result
    return deepcopy(result)


def _mpstats_info_by_suppliers_list(headers, suppliers_list):
    return {supplier: _mpstats_info_by_supplier(headers, supplier) for supplier in suppliers_list}


def _mpstats_info_by_nm_list(headers, nm_list):
    suppliers_info_dict = _mpstats_info_by_suppliers_list(headers, wb_info.all_suppliers())
    info_dict = {supplier: [] for supplier in suppliers_info_dict.keys()}
    for supplier, items in suppliers_info_dict.items():
        for item in items:
            if item['id'] in nm_list: info_dict[supplier].append(item)
    return info_dict


def mpstats_info(supplier=None, suppliers_list=None, nm_list=None, nm=None):
    headers = {'X-Mpstats-TOKEN': info.mpstats_token(),
               'Content-Type': 'application/json'}
    if supplier is None \
        and suppliers_list is None \
        and nm_list is None \
        and nm is None: raise AttributeError("No input data to fetch info.")
    elif supplier is not None: return _mpstats_info_by_supplier(headers, supplier)
    elif suppliers_list is not None: return _mpstats_info_by_suppliers_list(headers, suppliers_list)
    elif nm is not None: return _mpstats_info_by_nm_list(headers, [nm])
    elif nm_list is not None: return _mpstats_info_by_nm_list(headers, nm_list)


def mpstats_categories_info(categories_list, start_date=str(date.today()-timedelta(days=7)),
                            end_date=str(date.today()-timedelta(days=1))):
    result = _mpstats_categories_info.get(tuple([tuple(categories_list), start_date, end_date]))
    if result is None:
        headers = {'X-Mpstats-TOKEN': info.mpstats_token(),
                   'Content-Type': 'application/json'}
        url = 'https://mpstats.io/api/wb/get/category/by_date'
        params_list = [{'path': category.strip(), 'groupBy': 'day',
                       'd1': str(start_date), 'd2': str(end_date)}
                       for category in categories_list]
        result_dict = async_requests.fetch("GET", categories_list, content_type='json', url=url,
                                           params_list=params_list, headers=headers)
        result = {category: {item['period']: item for item in day_values}
                  for category, day_values in result_dict.items()}
        _mpstats_categories_info[tuple([tuple(categories_list), start_date, end_date])] = result
    return deepcopy(result)


