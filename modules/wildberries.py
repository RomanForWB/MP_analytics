from bs4 import BeautifulSoup
from datetime import date, timedelta
import requests, json, sys

import modules.async_requests as async_requests
import modules.files as files

def get_category_and_brand(sku_list):
    url_list = [f'https://www.wildberries.ru/catalog/{sku}/detail.aspx' for sku in sku_list]
    categories_dict = async_requests.by_urls('GET', url_list, sku_list,
                                             content_type='text')
    counter = 0
    print("\nПарсинг категорий из карточек Wildberries...")
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
    return categories_dict

def fetch_incomes(key, start_date=date.today()-timedelta(days=30)):
    url = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/incomes'
    params = {'key': key, 'dateFrom': str(start_date)}
    response = requests.get(url, params=params)
    return response.json()

def fetch_stocks(key, start_date=date.today()-timedelta(days=30)):
    url = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/stocks'
    params = {'key': key, 'dateFrom': str(start_date)}
    response = requests.get(url, params=params)
    return response.json()

def fetch_all_stocks(keys_dict, start_date=date.today()-timedelta(days=30)):
    url = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/stocks'
    items_dict = dict()
    for company, key in keys_dict.items():
        params = {'key': key, 'dateFrom': str(start_date)}
        while (True):
            response = requests.get(url, params=params)
            if response.status_code >= 200 and response.status_code < 300:
                items_dict[company] = response.json()
                break
    return items_dict

def fetch_cards(token):
    headers = {'Authorization': token}
    body = {"id": 1,
            "jsonrpc": "2.0",
            "params": {
            'withError': False,
            'query': {
                "limit": 1000
            }
        }
    }
    r = requests.post("https://suppliers-api.wildberries.ru/card/list", json=body, headers=headers)
    result = json.loads(r.text)
    return result['result']['cards']

def stocks(company, items_list):
    table = list()
    items_dict = dict()
    for item in items_list:
        dict_key = (item['supplierArticle'],
                    item['nmId'],
                    company,
                    f"{item['category']}/{item['subject']}",
                    item['brand'],
                    item['techSize'])
        items_dict.setdefault(dict_key, [0,0,0,0,0,''])
        items_dict[dict_key][0] += item['quantityFull']
        items_dict[dict_key][1] += item['quantityNotInOrders']
        items_dict[dict_key][2] += item['quantity']
        items_dict[dict_key][3] += item['inWayToClient']
        items_dict[dict_key][4] += item['inWayFromClient']
        if items_dict[dict_key][5] < item['lastChangeDate']: items_dict[dict_key][5] = item['lastChangeDate']
    for key, value in items_dict.items():
        table.append(list(key)+value)
    table.sort()
    return table

def all_stocks(items_dict):
    table = list()
    header = ['Артикул поставщика', 'SKU', 'Компания', 'Предмет', 'Бренд', 'Размер',
              'На складе', 'На складе (не в заказах)',
              'Доступно для продажи', 'В пути к клиенту', 'В пути от клиента', 'Время обновления']
    for company, items in items_dict.items():
        table += stocks(company, items)
    table.insert(0, header)
    return table

def fetch_feedbacks(card_ids):
    url = 'https://public-feedbacks.wildberries.ru/api/v1/summary/full'
    params_list = [{"imtId": card_id,
                    "skip": 0,
                    "take": 1000} for card_id in card_ids]
    feedbacks_dict = async_requests.by_params('POST', url, params_list, card_ids, content_type='json')
    feedbacks_dict = {card_id: feedbacks['feedbacks'] for card_id, feedbacks in feedbacks_dict.items()}
    return feedbacks_dict

def feedbacks(supplier):
    token = files.get_wb_key('token', supplier)
    cards = fetch_cards(token)
    card_ids = [card['imtId'] for card in cards]
    feedbacks = fetch_feedbacks(card_ids)
    table = list()
    last_counter = 3  # количество рассматриваемых отзывов
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд',
              'Плохой отзыв', 'Средний рейтинг', 'Последний негативный отзыв']
    for card in cards:
        card_id = card['imtId']
        nomenclature = card['nomenclatures'][0]['nmId']
        for type in card['addin']:
            if type['type'] == 'Бренд':
                brand = type['params'][0]['value']
                break
        bad_mark = 'Нет'
        rating_score = 0
        bad_feedback = ''
        if feedbacks[card_id] is None: avg_rating = 0
        elif len(feedbacks[card_id]) <= last_counter:
            for feedback in feedbacks[card_id]:
                rating_score += feedback['productValuation']
                if bad_mark == 'Нет' and feedback['productValuation'] < 4:
                    bad_mark = 'Да'
                    bad_feedback = feedback['text']
            avg_rating = round(rating_score / len(feedbacks[card_id]), 1)
        else:
            for feedback in feedbacks[card_id][:last_counter]:
                rating_score += feedback['productValuation']
                if bad_mark == 'Нет' and feedback['productValuation'] < 4:
                    bad_mark = 'Да'
                    bad_feedback = feedback['text']
            avg_rating = round(rating_score/last_counter, 1)
        table.append([supplier,
                      nomenclature,
                      card['supplierVendorCode'],
                      f"{card['parent']}/{card['object']}",
                      brand,
                      bad_mark,
                      avg_rating,
                      bad_feedback])
    table.sort(key=lambda item: item[2])
    table.insert(0, header)
    return table


# ================== тестовые запуски ==================
if __name__ == '__main__':
    result = feedbacks('ИП Марьина А.А.')
    print(result)
    print(len(result))
