from datetime import date, timedelta, datetime
import requests, json

import modules.async_requests as async_requests
import modules.wildberries.info as wb_info
import modules.info as info


def _fetch_cards_by_supplier(url, body, supplier):
    headers = {'Authorization': wb_info.api_key('token', supplier)}
    response = requests.post(url, json=body, headers=headers)
    return response.json()['result']['cards']


def _fetch_cards_by_suppliers_list(url, body, suppliers_list):
    headers_list = [{'Authorization': wb_info.api_key('token', supplier)}
                    for supplier in suppliers_list]
    cards_dict = async_requests.fetch('POST', suppliers_list, url=url,
                                      headers_list=headers_list, body=body, content_type='json')
    cards_dict = {supplier: cards['result']['cards'] for supplier, cards in cards_dict.items()}
    return cards_dict


def _fetch_orders_by_supplier(url, headers, supplier, start_date):
    while True:
        params = {'key': wb_info.api_key('x64', supplier),
                  'dateFrom': start_date}
        response = requests.get(url, params=params, headers=headers)
        if 200 <= response.status_code < 300: return response.json()
        else: continue


def _fetch_orders_by_suppliers_list(url, headers, suppliers_list, start_date):
    params_list = [{'key': wb_info.api_key('x64', supplier),
                    'dateFrom': str(start_date)}
                   for supplier in suppliers_list]
    return async_requests.fetch('GET', suppliers_list, url=url, params_list=params_list,
                                headers=headers, content_type='json')


def _fetch_stocks_by_supplier(url, supplier, start_date):
    params = {'key': wb_info.api_key('x64', supplier), 'dateFrom': start_date}
    response = requests.get(url, params=params)
    return response.json()


def _fetch_stocks_by_suppliers_list(url, suppliers_list, start_date):
    params_list = [{'key': wb_info.api_key('x64', supplier),
                    'dateFrom': start_date}
                   for supplier in suppliers_list]
    return async_requests.fetch('GET', suppliers_list, url=url,
                                params_list=params_list, content_type='json')


def _feedbacks_by_data(supplier, card, feedbacks_list):
    brand = ''  # бренд
    for addin in card['addin']:
        if addin['type'] == 'Бренд':
            brand = addin['params'][0]['value']
            break

    bad_mark = 'Нет'  # наличие плохого отзыва
    rating_score = 0
    bad_feedback = ''  # текст плохого отзыва
    if feedbacks_list is None:
        avg_rating = 0  # средний рейтинг последних отзывов
    else:
        for feedback in feedbacks_list:
            rating_score += feedback['productValuation']
            if bad_mark == 'Нет' and feedback['productValuation'] < 4:
                bad_mark = 'Да'
                bad_feedback = feedback['text']
        avg_rating = round(rating_score / len(feedbacks_list), 1)  # средний рейтинг последних отзывов
    return [[wb_info.supplier_name(supplier), nomenclature['nmId'],
             f"{card['supplierVendorCode']}{nomenclature['vendorCode']}",
             f"{card['parent']}/{card['object']}", brand,
             bad_mark, avg_rating, bad_feedback] for nomenclature in card['nomenclatures']]


def _feedbacks_by_supplier(supplier, count):
    cards = fetch_cards(supplier=supplier)
    imt_list = [card['imtId'] for card in cards]
    feedbacks_dict = fetch_feedbacks(imt_list, count)
    table = list()
    for card in cards:
        data_list = _feedbacks_by_data(supplier, card, feedbacks_dict[card['imtId']])
        table += data_list
    table.sort(key=lambda item: item[2])
    return table


def _feedbacks_by_suppliers_list(suppliers_list, count):
    table = list()
    for supplier in suppliers_list:
        table += _feedbacks_by_supplier(supplier, count)
    return table


def _feedbacks_by_nm_list(nm_list, count):
    suppliers_list = wb_info.all_suppliers()
    cards_dict = fetch_cards(suppliers_list=suppliers_list)
    supplier_cards_dict = {supplier: [] for supplier in suppliers_list}
    imt_list = list()
    for nm in nm_list:
        for supplier, cards in cards_dict.items():
            for card in cards:
                for nomenclature in card['nomenclatures']:
                    if nm == nomenclature['nmId']:
                        supplier_cards_dict[supplier].append(card)
                        imt_list.append(card['imtId'])
    feedbacks_dict = fetch_feedbacks(imt_list, count)
    result_table = list()
    for supplier, cards in supplier_cards_dict.items():
        supplier_table = list()
        for card in cards:
            data_list = _feedbacks_by_data(supplier, card, feedbacks_dict[card['imtId']])
            supplier_table += data_list
        result_table += sorted(supplier_table, key=lambda item: item[2])
    return result_table


def _orders_count_by_supplier(supplier, start_date):
    orders_list = fetch_orders(supplier=supplier, start_date=start_date)
    days = info.days_list(start_date)
    nm_dict = dict()
    nm_info_dict = dict()
    for order in orders_list:
        nm = order['nmId']
        if nm not in nm_info_dict.keys():
            nm_info_dict[nm] = {'Артикул поставщика': order['supplierArticle'],
                                'Предмет': f"{order['category']}/{order['subject']}",
                                'Бренд': order['brand']}
            nm_dict[nm] = {day: {'orders': 0, 'prices': []} for day in days}
        try:
            day = datetime.strptime(order['date'], '%Y-%m-%dT%H:%M:%S').date().strftime('%d.%m')
            nm_dict[nm][day]['orders'] += 1
            final_price = order['totalPrice'] * (100 - order['discountPercent']) / 100
            nm_dict[nm][day]['prices'] += [final_price] * order['quantity']
        except KeyError: pass

    table = list()
    for nm, days_info in nm_dict.items():
        article = nm_info_dict[nm]['Артикул поставщика']
        subject = nm_info_dict[nm]['Предмет']
        brand = nm_info_dict[nm]['Бренд']
        days_orders_list = [days_info[day]['orders'] for day in days]
        days_values_list = [sum(days_info[day]['prices']) for day in days]
        all_orders_count = sum(days_orders_list)
        all_orders_price = sum(days_values_list)
        if all_orders_count == 0: avg_price = 0
        else: avg_price = all_orders_price / all_orders_count
        table.append([wb_info.supplier_name(supplier), nm, article, subject, brand] +
                     days_orders_list + [all_orders_count, avg_price, all_orders_price])

    return sorted(table, key=lambda item: item[2])


def _orders_count_by_suppliers_list(suppliers_list, start_date):
    table = list()
    for supplier in suppliers_list:
        table += _orders_count_by_supplier(supplier, start_date)
    return table


def _orders_count_by_nm_list(nm_list, start_date):
    orders_dict = fetch_orders(suppliers_list=wb_info.all_suppliers(), start_date=start_date)
    days = info.days_list(start_date)
    table = list()
    nm_dict = dict()
    nm_info_dict = dict()
    for supplier, orders_list in orders_dict.items():
        for order in orders_list:
            nm = order['nmId']
            if nm not in nm_list: continue
            if nm not in nm_info_dict.keys():
                nm_info_dict[nm] = {'Артикул поставщика': order['supplierArticle'],
                                    'Предмет': f"{order['category']}/{order['subject']}",
                                    'Бренд': order['brand']}
                nm_dict[nm] = {day: {'orders': 0, 'prices': []} for day in days}
            try:
                day = datetime.strptime(order['date'], '%Y-%m-%dT%H:%M:%S').date().strftime('%d.%m')
                nm_dict[nm][day]['orders'] += 1
                final_price = order['totalPrice'] * (100 - order['discountPercent']) / 100
                nm_dict[nm][day]['prices'] += [final_price] * order['quantity']
            except KeyError:
                pass

        supplier_table = list()
        for nm, days_info in nm_dict.items():
            article = nm_info_dict[nm]['Артикул поставщика']
            subject = nm_info_dict[nm]['Предмет']
            brand = nm_info_dict[nm]['Бренд']
            days_orders_list = [days_info[day]['orders'] for day in days]
            days_values_list = [sum(days_info[day]['prices']) for day in days]
            all_orders_count = sum(days_orders_list)
            all_orders_price = sum(days_values_list)
            if all_orders_count == 0:
                avg_price = 0
            else:
                avg_price = all_orders_price / all_orders_count
            supplier_table.append([wb_info.supplier_name(supplier), nm, article, subject, brand] +
                                  days_orders_list + [all_orders_count, avg_price, all_orders_price])
        table += sorted(supplier_table, key=lambda item: item[2])
    return table


def _orders_value_by_supplier(supplier, start_date):
    orders_list = fetch_orders(supplier, start_date)
    days = info.days_list(start_date)
    nm_dict = dict()
    nm_info_dict = dict()
    for order in orders_list:
        nm = order['nmId']
        if nm not in nm_info_dict.keys():
            nm_info_dict[nm] = {'Артикул поставщика': order['supplierArticle'],
                                'Предмет': f"{order['category']}/{order['subject']}",
                                'Бренд': order['brand']}
            nm_dict[nm] = {day: {'orders': 0, 'prices': []} for day in days}
        try:
            day = datetime.strptime(order['date'], '%Y-%m-%dT%H:%M:%S').date().strftime('%d.%m')
            nm_dict[nm][day]['orders'] += 1
            final_price = order['totalPrice'] * (100 - order['discountPercent']) / 100
            nm_dict[nm][day]['prices'] += [final_price] * order['quantity']
        except KeyError: pass

    table = list()
    for nm, days_info in nm_dict.items():
        article = nm_info_dict[nm]['Артикул поставщика']
        subject = nm_info_dict[nm]['Предмет']
        brand = nm_info_dict[nm]['Бренд']
        days_orders_list = [days_info[day]['orders'] for day in days]
        days_values_list = [sum(days_info[day]['prices']) for day in days]
        all_orders_count = sum(days_orders_list)
        all_orders_price = sum(days_values_list)
        if all_orders_count == 0: avg_price = 0
        else: avg_price = all_orders_price / all_orders_count
        table.append([wb_info.supplier_name(supplier), nm, article, subject, brand] +
                     days_values_list + [all_orders_count, avg_price, all_orders_price])
    return sorted(table, key=lambda item: item[2])


def _orders_value_by_suppliers_list(suppliers_list, start_date):
    table = list()
    for supplier in suppliers_list:
        table += _orders_value_by_supplier(supplier, start_date)
    return table


def _orders_value_by_nm_list(nm_list, start_date):
    orders_dict = fetch_orders(suppliers_list=wb_info.all_suppliers(), start_date=start_date)
    days = info.days_list(start_date)
    table = list()
    nm_dict = dict()
    nm_info_dict = dict()
    for supplier, orders_list in orders_dict.items():
        for order in orders_list:
            nm = order['nmId']
            if nm not in nm_list: continue
            if nm not in nm_info_dict.keys():
                nm_info_dict[nm] = {'Артикул поставщика': order['supplierArticle'],
                                    'Предмет': f"{order['category']}/{order['subject']}",
                                    'Бренд': order['brand']}
                nm_dict[nm] = {day: {'orders': 0, 'prices': []} for day in days}
            try:
                day = datetime.strptime(order['date'], '%Y-%m-%dT%H:%M:%S').date().strftime('%d.%m')
                nm_dict[nm][day]['orders'] += 1
                final_price = order['totalPrice'] * (100 - order['discountPercent']) / 100
                nm_dict[nm][day]['prices'] += [final_price] * order['quantity']
            except KeyError:
                pass

        supplier_table = list()
        for nm, days_info in nm_dict.items():
            article = nm_info_dict[nm]['Артикул поставщика']
            subject = nm_info_dict[nm]['Предмет']
            brand = nm_info_dict[nm]['Бренд']
            days_orders_list = [days_info[day]['orders'] for day in days]
            days_values_list = [sum(days_info[day]['prices']) for day in days]
            all_orders_count = sum(days_orders_list)
            all_orders_price = sum(days_values_list)
            if all_orders_count == 0:
                avg_price = 0
            else:
                avg_price = all_orders_price / all_orders_count
            supplier_table.append([wb_info.supplier_name(supplier), nm, article, subject, brand] +
                                  days_values_list + [all_orders_count, avg_price, all_orders_price])
        table += sorted(supplier_table, key=lambda item: item[2])
    return table


def _orders_category_by_supplier(supplier, start_date):
    orders_list = fetch_orders(supplier=supplier, start_date=start_date)
    days = info.days_list(start_date)
    categories_dict = dict()
    for order in orders_list:
        category = order['subject']
        if category not in categories_dict.keys():
            categories_dict[category] = {day: 0 for day in days}
        try:
            day = datetime.strptime(order['date'], '%Y-%m-%dT%H:%M:%S').date().strftime('%d.%m')
            final_price = order['totalPrice'] * (100 - order['discountPercent']) / 100
            categories_dict[category][day] += final_price
        except KeyError: pass

    table = list()
    total = dict()
    for category, days_info in categories_dict.items():
        table.append([category] + [days_info[day] for day in days])
        for day in days: total[day] += days_info[day]

    table.sort(key=lambda item: sum(item[1:]), reverse=True)
    table.insert(0, ["Итого"] + [total[day] for day in days])
    return table


def _orders_category_by_suppliers_list(suppliers_list, start_date):
    orders_dict = fetch_orders(suppliers_list=suppliers_list, start_date=start_date)
    days = info.days_list(start_date)
    categories_dict = dict()
    for supplier, orders_list in orders_dict.items():
        for order in orders_list:
            category = order['subject']
            if category not in categories_dict.keys():
                categories_dict[category] = {day: 0 for day in days}
            try:
                day = datetime.strptime(order['date'], '%Y-%m-%dT%H:%M:%S').date().strftime('%d.%m')
                final_price = order['totalPrice'] * (100 - order['discountPercent']) / 100
                categories_dict[category][day] += final_price
            except KeyError: pass

    table = list()
    total = {day: 0 for day in days}
    for category, days_info in categories_dict.items():
        table.append([category] + [days_info[day] for day in days])
        for day in days: total[day] += days_info[day]

    table.sort(key=lambda item: sum(item[1:]), reverse=True)
    table.insert(0, ["Итого"] + [total[day] for day in days])
    return table


def _orders_category_by_nm_list(nm_list, start_date):
    orders_dict = fetch_orders(suppliers_list=wb_info.all_suppliers(), start_date=start_date)
    days = info.days_list(start_date)
    categories_dict = dict()
    for supplier, orders_list in orders_dict.items():
        for order in orders_list:
            if order['nmId'] not in nm_list: continue
            category = order['subject']
            if category not in categories_dict.keys():
                categories_dict[category] = {day: 0 for day in days}
            try:
                day = datetime.strptime(order['date'], '%Y-%m-%dT%H:%M:%S').date().strftime('%d.%m')
                final_price = order['totalPrice'] * (100 - order['discountPercent']) / 100
                categories_dict[category][day] += final_price
            except KeyError: pass

    table = list()
    total = {day: 0 for day in days}
    for category, days_info in categories_dict.items():
        table.append([category] + [days_info[day] for day in days])
        for day in days: total[day] += days_info[day]

    table.sort(key=lambda item: sum(item[1:]), reverse=True)
    table.insert(0, ["Итого"] + [total[day] for day in days])
    return table


def _stocks_by_supplier(supplier, start_date):
    stocks_list = fetch_stocks(supplier=supplier, start_date=start_date)
    table = list()
    items_dict = dict()
    for stock in stocks_list:
        dict_key = (wb_info.supplier_name(supplier),
                    stock['nmId'],
                    stock['supplierArticle'],
                    f"{stock['category']}/{stock['subject']}",
                    stock['brand'],
                    stock['techSize'])
        items_dict.setdefault(dict_key, [0, 0, 0, 0, 0, ''])
        items_dict[dict_key][0] += stock['quantityFull']
        items_dict[dict_key][1] += stock['quantityNotInOrders']
        items_dict[dict_key][2] += stock['quantity']
        items_dict[dict_key][3] += stock['inWayToClient']
        items_dict[dict_key][4] += stock['inWayFromClient']
        if items_dict[dict_key][5] < stock['lastChangeDate']: items_dict[dict_key][5] = stock['lastChangeDate']
    for key, value in items_dict.items():
        table.append(list(key) + value)
    return sorted(table, key=lambda item: item[2])


def _stocks_by_suppliers_list(suppliers_list, start_date):
    stocks_dict = fetch_stocks(suppliers_list=suppliers_list, start_date=start_date)
    table = list()
    for supplier, stocks_list in stocks_dict.items():
        supplier_table = list()
        items_dict = dict()
        for stock in stocks_list:
            dict_key = (wb_info.supplier_name(supplier),
                        stock['nmId'],
                        stock['supplierArticle'],
                        f"{stock['category']}/{stock['subject']}",
                        stock['brand'],
                        stock['techSize'])
            items_dict.setdefault(dict_key, [0, 0, 0, 0, 0, ''])
            items_dict[dict_key][0] += stock['quantityFull']
            items_dict[dict_key][1] += stock['quantityNotInOrders']
            items_dict[dict_key][2] += stock['quantity']
            items_dict[dict_key][3] += stock['inWayToClient']
            items_dict[dict_key][4] += stock['inWayFromClient']
            if items_dict[dict_key][5] < stock['lastChangeDate']: items_dict[dict_key][5] = stock['lastChangeDate']
        for key, value in items_dict.items():
            supplier_table.append(list(key) + value)
        table += sorted(supplier_table, key=lambda item: item[2])
    return table


def _stocks_by_nm_list(nm_list, start_date):
    stocks_dict = fetch_stocks(suppliers_list=wb_info.all_suppliers(), start_date=start_date)
    table = list()
    for supplier, stocks_list in stocks_dict.items():
        supplier_table = list()
        items_dict = dict()
        for stock in stocks_list:
            if stock['nmId'] not in nm_list: continue
            dict_key = (wb_info.supplier_name(supplier),
                        stock['nmId'],
                        stock['supplierArticle'],
                        f"{stock['category']}/{stock['subject']}",
                        stock['brand'],
                        stock['techSize'])
            items_dict.setdefault(dict_key, [0, 0, 0, 0, 0, ''])
            items_dict[dict_key][0] += stock['quantityFull']
            items_dict[dict_key][1] += stock['quantityNotInOrders']
            items_dict[dict_key][2] += stock['quantity']
            items_dict[dict_key][3] += stock['inWayToClient']
            items_dict[dict_key][4] += stock['inWayFromClient']
            if items_dict[dict_key][5] < stock['lastChangeDate']: items_dict[dict_key][5] = stock['lastChangeDate']
        for key, value in items_dict.items():
            supplier_table.append(list(key) + value)
        table += sorted(supplier_table, key=lambda item: item[2])
    return table


def fetch_cards(supplier=None, suppliers_list=None):
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
    elif supplier is not None: return _fetch_cards_by_supplier(url, body, supplier)
    elif suppliers_list is not None: return _fetch_cards_by_suppliers_list(url, body, suppliers_list)


def fetch_feedbacks(imt_list, count=1000):
    url = 'https://public-feedbacks.wildberries.ru/api/v1/summary/full'
    bodies_list = [{"imtId": imt,
                    "skip": 0,
                    "take": count} for imt in imt_list]
    feedbacks_dict = async_requests.fetch('POST', imt_list, url=url,
                                          bodies_list=bodies_list, content_type='json')
    feedbacks_dict = {imt: feedbacks_info['feedbacks']
                      for imt, feedbacks_info in feedbacks_dict.items()}
    return feedbacks_dict


def fetch_simple_category_and_brand(nm_list):
    urls_list = [f'https://wbx-content-v2.wbstatic.net/ru/{nm}.json' for nm in nm_list]
    nm_dict = async_requests.fetch('GET', nm_list, urls_list=urls_list, content_type='text')
    simple_categories_dict = dict()
    for nm, card_info in nm_dict.items():
        card_info = json.loads(card_info)
        simple_categories_dict[nm] = {'category': f"{card_info['subj_root_name']}/{card_info['subj_name']}",
                                      'brand': card_info['selling']['brand_name']}
    return simple_categories_dict


def fetch_orders(supplier=None, suppliers_list=None, start_date=str(date.today()-timedelta(days=6))):
    url = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/orders'
    headers = {'Content-Type': 'application/json'}
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch orders.")
    elif supplier is not None: return _fetch_orders_by_supplier(url, headers, supplier, start_date)
    elif suppliers_list is not None: return _fetch_orders_by_suppliers_list(url, headers, suppliers_list, start_date)


def fetch_stocks(supplier=None, suppliers_list=None, start_date=date.today()-timedelta(days=6)):
    url = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/stocks'
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch orders.")
    elif supplier is not None: return _fetch_stocks_by_supplier(url, supplier, start_date)
    elif suppliers_list is not None: return _fetch_stocks_by_suppliers_list(url, suppliers_list, start_date)


def feedbacks(input_data, count=3):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд',
              'Плохой отзыв', 'Средний рейтинг', 'Последний негативный отзыв']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _feedbacks_by_suppliers_list(input_data, count)
        elif type(input_data[0]) == int: table = _feedbacks_by_nm_list(input_data, count)
    elif type(input_data) == str: table = _feedbacks_by_supplier(input_data, count)
    elif type(input_data) == int: table = _feedbacks_by_nm_list([input_data], count)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def orders_count(input_data, start_date=str(date.today()-timedelta(days=7))):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд'] + \
             info.days_list(start_date) + \
             ['Итого', 'Средняя цена', 'Сумма заказов']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _orders_count_by_suppliers_list(input_data, start_date)
        elif type(input_data[0]) == int: table = _orders_count_by_nm_list(input_data, start_date)
    elif type(input_data) == str: table = _orders_count_by_supplier(input_data, start_date)
    elif type(input_data) == int: table = _orders_count_by_nm_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def orders_value(input_data, start_date=str(date.today()-timedelta(days=7))):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд'] + \
             info.days_list(start_date) + \
             ['Итого', 'Средняя цена', 'Сумма заказов']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _orders_value_by_suppliers_list(input_data, start_date)
        elif type(input_data[0]) == int: table = _orders_value_by_nm_list(input_data, start_date)
    elif type(input_data) == str: table = _orders_value_by_supplier(input_data, start_date)
    elif type(input_data) == int: table = _orders_value_by_nm_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def orders_category(input_data, start_date=str(date.today()-timedelta(days=7))):
    header = ['По категориям'] + info.days_list(start_date)
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str:
            header = ['Для всех'] + info.days_list(start_date)
            table = _orders_category_by_suppliers_list(input_data, start_date)
        elif type(input_data[0]) == int:
            header = ['Для номенклатур'] + info.days_list(start_date)
            table = _orders_category_by_nm_list(input_data, start_date)
    elif type(input_data) == str:
        header = [wb_info.supplier_name(input_data)] + info.days_list(start_date)
        table = _orders_category_by_supplier(input_data, start_date)
    elif type(input_data) == int:
        header = [input_data] + info.days_list(start_date)
        table = _orders_category_by_nm_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def stocks(input_data, start_date=str(date.today()-timedelta(days=7))):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд',
              'Размер', 'На складе', 'Не в заказе', 'Доступно',
              'В пути к клиенту', 'В пути от клиента', 'Время обновления']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _stocks_by_suppliers_list(input_data, start_date)
        elif type(input_data[0]) == int: table = _stocks_by_nm_list(input_data, start_date)
    elif type(input_data) == str: table = _stocks_by_supplier(input_data, start_date)
    elif type(input_data) == int: table = _stocks_by_nm_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table
