from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import requests, json, sys

import modules.async_requests as async_requests
import modules.files as files
from main import supplier_names


def get_category_and_brand(sku_list):
    url_list = [f'https://www.wildberries.ru/catalog/{sku}/detail.aspx' for sku in sku_list]
    categories_dict = async_requests.by_urls('GET', url_list, sku_list,
                                             content_type='text')
    counter = 0
    print("Парсинг категорий из карточек Wildberries...")
    print(f"Всего карточек: {len(categories_dict)}")
    for sku, value in categories_dict.items():
        soup = BeautifulSoup(value, 'html.parser')
        category_soup = soup.findAll('a', class_="breadcrumbs__link")
        if len(category_soup) < 2:
            categories_dict[sku] = {'category': None, 'brand': None}
        else:
            categories_dict[sku] = dict()
            header_category = category_soup[1].text.strip()
            for data in category_soup[2:-1]:
                header_category += '/' + data.text.strip()
            categories_dict[sku]['category'] = header_category
            categories_dict[sku]['brand'] = category_soup[-1].text.strip()
        counter += 1
        print(f'\rОбработано: {counter}', end='')
    print()
    return categories_dict


def fetch_incomes(key, start_date=date.today() - timedelta(days=7)):
    url = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/incomes'
    params = {'key': key, 'dateFrom': str(start_date)}
    response = requests.get(url, params=params)
    return response.json()


# ================ NEW VERSION =======================


def _fetch_cards_by_supplier(url, params, supplier):
    headers = {'Authorization': files.get_wb_key('token', supplier)}
    response = requests.post(url, json=params, headers=headers)
    result = response.json()
    return result['result']['cards']


def _fetch_cards_by_suppliers_list(url, params, suppliers_list):
    headers_list = [{'Authorization': files.get_wb_key('token', supplier)}
                    for supplier in suppliers_list]
    cards_dict = async_requests.by_headers('POST', url, headers_list, suppliers_list, params=params, content_type='json')
    cards_dict = {one: cards['result']['cards'] for one, cards in cards_dict.items()}
    return cards_dict


def _fetch_orders_by_supplier(url, headers, supplier, start_date):
    params = {'key': files.get_wb_key('x64', supplier),
              'dateFrom': start_date}
    response = requests.get(url, params=params, headers=headers)
    return response.json()


def _fetch_orders_by_suppliers_list(url, headers, suppliers_list, start_date):
    params_list = [{'key': files.get_wb_key('x64', supplier),
                    'dateFrom': start_date}
                   for supplier in suppliers_list]
    orders_dict = async_requests.by_params('GET', url, params_list, suppliers_list, headers=headers, content_type='json')
    return orders_dict


def _fetch_stocks_by_supplier(url, supplier, start_date):
    params = {'key': files.get_wb_key('x64', supplier), 'dateFrom': start_date}
    response = requests.get(url, params=params)
    return response.json()


def _fetch_stocks_by_suppliers_list(url, suppliers_list, start_date):
    params_list = [{'key': files.get_wb_key('x64', supplier),
                    'dateFrom': start_date}
                   for supplier in suppliers_list]
    stocks_dict = async_requests.by_params('GET', url, params_list, suppliers_list, content_type='json')
    return stocks_dict


def _feedbacks_by_data(supplier, card, feedbacks_list):
    brand = ''  # бренд
    for type in card['addin']:
        if type['type'] == 'Бренд':
            brand = type['params'][0]['value']
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

    return [supplier_names[supplier], card['nomenclatures'][0]['nmId'],
            card['supplierVendorCode'], f"{card['parent']}/{card['object']}", brand,
            bad_mark, avg_rating, bad_feedback]


def _feedbacks_by_supplier(supplier, count):
    cards = fetch_cards(supplier=supplier)
    imt_list = [card['imtId'] for card in cards]
    feedbacks_dict = fetch_feedbacks(imt_list, count)
    table = list()
    for card in cards:
        data_list = _feedbacks_by_data(supplier, card, feedbacks_dict[card['imtId']])
        table.append(data_list)
    table.sort(key=lambda item: item[2])
    return table


def _feedbacks_by_suppliers_list(suppliers_list, count):
    table = list()
    for supplier in suppliers_list:
        table += _feedbacks_by_supplier(supplier, count)
    return table


def _feedbacks_by_nm_list(nm_list, count):
    suppliers_list = list(supplier_names.keys())
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
            supplier_table.append(data_list)
        result_table += sorted(supplier_table, key=lambda item: item[2])
    return result_table


def _orders_by_supplier(supplier, start_date, days):
    orders_list = fetch_orders(supplier, start_date)
    nm_dict = dict()
    nm_info_dict = dict()
    for order in orders_list:
        nm = order['nmId']
        if nm not in nm_info_dict.keys():
            nm_info_dict[nm] = {'Артикул поставщика': order['supplierArticle'],
                                'Предмет': f"{order['category']}/{order['subject']}",
                                'Бренд': order['brand']}
        day = datetime.strptime(order['date'], '%Y-%m-%dT%H:%M:%S').date().strftime('%d.%m')
        nm_dict.setdefault(nm, {day: {'orders': 0, 'prices': []} for day in days})
        try: nm_dict[nm][day]['orders'] += 1
        except KeyError:
            print(order)
            continue
        final_price = order['totalPrice'] * (100 - order['discountPercent']) / 100
        nm_dict[nm][day]['prices'] += final_price * order['quantity']
    table = list()
    for nm, days_info in nm_dict.items():
        article = nm_info_dict[nm]['Артикул поставщика']
        subject = nm_info_dict[nm]['Предмет']
        brand = nm_info_dict[nm]['Бренд']
        days_orders_list = [days_info[day]['orders'] for day in days]
        orders_count = sum(days_orders_list)
        orders_price = sum([sum(days_info[day]['prices']) for day in days])
        avg_price = round(orders_price / orders_count, 2)
        table.append([supplier_names[supplier], article, subject, brand] +
                     days_orders_list + [orders_count, avg_price, orders_price])
    return table


def _orders_by_suppliers_list(suppliers_list, start_date, days):
    table = list()
    for supplier in suppliers_list:
        table += _orders_by_supplier(supplier, start_date, days)
    return table


def _stocks_by_supplier(supplier, start_date):
    stocks_list = fetch_stocks(supplier=supplier, start_date=start_date)
    table = list()
    items_dict = dict()
    for item in stocks_list:
        dict_key = (item['supplierArticle'],
                    item['nmId'],
                    supplier_names[supplier],
                    f"{item['category']}/{item['subject']}",
                    item['brand'],
                    item['techSize'])
        items_dict.setdefault(dict_key, [0, 0, 0, 0, 0, ''])
        items_dict[dict_key][0] += item['quantityFull']
        items_dict[dict_key][1] += item['quantityNotInOrders']
        items_dict[dict_key][2] += item['quantity']
        items_dict[dict_key][3] += item['inWayToClient']
        items_dict[dict_key][4] += item['inWayFromClient']
        if items_dict[dict_key][5] < item['lastChangeDate']: items_dict[dict_key][5] = item['lastChangeDate']
    for key, value in items_dict.items():
        table.append(list(key) + value)
    table.sort()
    return table


def _stocks_by_suppliers_list(suppliers_list, start_date):
    table = list()
    for supplier in suppliers_list:
        table += _stocks_by_supplier(supplier, start_date)
    return table


# def _stocks_by_nm_list
# def _orders_by_nm_list()


def fetch_cards(supplier=None, suppliers_list=None):
    url = "https://suppliers-api.wildberries.ru/card/list"
    params = {"id": 1,
              "jsonrpc": "2.0",
              "params": {
                  "withError": False,
                  "query": {
                      "limit": 1000
                      }
                  }
              }
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch cards.")
    elif supplier is not None: return _fetch_cards_by_supplier(url, params, supplier)
    elif suppliers_list is not None: return _fetch_cards_by_suppliers_list(url, params, suppliers_list)
    else: raise AttributeError("Choose an only option to fetch cards.")


def fetch_feedbacks(imt_list, count=1000):
    url = 'https://public-feedbacks.wildberries.ru/api/v1/summary/full'
    params_list = [{"imtId": imt,
                    "skip": 0,
                    "take": count} for imt in imt_list]
    feedbacks_dict = async_requests.by_params('POST', url, params_list, imt_list, content_type='json')
    feedbacks_dict = {imt: feedbacks_info['feedbacks']
                      for imt, feedbacks_info in feedbacks_dict.items()}
    return feedbacks_dict


def fetch_simple_category_and_brand(nm_list):
    url_list = [f'https://wbx-content-v2.wbstatic.net/ru/{nm}.json' for nm in nm_list]
    nm_dict = async_requests.by_urls('GET', url_list, nm_list, content_type='text')
    simple_categories_dict = dict()
    for nm, info in nm_dict.items():
        info = json.loads(info)
        simple_categories_dict[nm] = {'category': f"{info['subj_root_name']}/{info['subj_name']}",
                                      'brand': info['selling']['brand_name']}
    return simple_categories_dict


def fetch_orders(supplier=None, suppliers_list=None, start_date=str(date.today()-timedelta(days=7))):
    url = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/orders'
    headers = {'Content-Type': 'application/json'}
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch orders.")
    elif supplier is not None: return _fetch_orders_by_supplier(url, headers, supplier, start_date)
    elif suppliers_list is not None: return _fetch_orders_by_suppliers_list(url, headers, suppliers_list, start_date)
    else: raise AttributeError("Choose an only option to fetch orders.")


def fetch_stocks(supplier=None, suppliers_list=None, start_date=date.today()-timedelta(days=7)):
    url = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/stocks'
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch orders.")
    elif supplier is not None: return _fetch_stocks_by_supplier(url, supplier, start_date)
    elif suppliers_list is not None: return _fetch_stocks_by_suppliers_list(url, suppliers_list, start_date)
    else: raise AttributeError("Choose an only option to fetch orders.")


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


def orders(input_data, start_date=str(date.today()-timedelta(days=7))):
    days = list()
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    today_date = date.today()
    intermediate_day = start_date
    while intermediate_day <= today_date:
        days.append(intermediate_day.strftime('%d.%m'))
        intermediate_day += timedelta(days=1)

    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд'] + \
             days + ['Итого заказов', 'Средняя цена', 'Сумма заказов']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _orders_by_suppliers_list(input_data, start_date, days)
        elif type(input_data[0]) == int: table = _orders_by_nm_list(input_data, start_date, days)
    elif type(input_data) == str: table = _orders_by_supplier(input_data, start_date, days)
    elif type(input_data) == int: table = _orders_by_nm_list([input_data], start_date, days)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def stocks(input_data, start_date=str(date.today()-timedelta(days=7))):
    header = ['Артикул поставщика', 'SKU', 'Компания', 'Предмет', 'Бренд', 'Размер',
              'На складе', 'На складе (не в заказах)',
              'Доступно для продажи', 'В пути к клиенту', 'В пути от клиента', 'Время обновления']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _stocks_by_suppliers_list(input_data, start_date)
        elif type(input_data[0]) == int: table = _stocks_by_nm_list(input_data, start_date)
    elif type(input_data) == str: table = _stocks_by_supplier(input_data, start_date)
    elif type(input_data) == int: table = _stocks_by_nm_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table

# ================== тестовые запуски ==================
if __name__ == '__main__': pass
