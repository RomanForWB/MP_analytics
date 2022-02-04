from bs4 import BeautifulSoup
from datetime import date, timedelta
import requests, json

import modules.async_requests as async_requests

WILDBERRIES_SUPPLIER_KEY_MARYINA = 'MmY1ZTU0ZTUtN2E2NC00YmI5LTgwNTgtODU4MWVlZTRlNzVh'

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
        response = requests.get(url, params=params)
        items_dict[company] = response.json()
    return items_dict

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

# ================== тестовые запуски ==================
if __name__ == '__main__':
    # sku_list = [44117798,16557761,35663011,35663012,16557765,16557766,12129508,16557769,16557770]
    # items_dict = get_category_and_brand(sku_list)
    # for sku, value in items_dict.items():
    #     print(sku + value)

    items_list = fetch_stocks(WILDBERRIES_SUPPLIER_KEY_MARYINA, '2022-01-01')
    stocks_table = stocks(items_list)
    for row in stocks_table:
        print(row)
