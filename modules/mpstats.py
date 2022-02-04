from datetime import date, timedelta

import modules.async_requests as async_requests
import modules.wildberries as wildberries

MPSTATS_TOKEN = '61f13463acf5c2.3680545125abcc4e82cf45ecd7c2cfa60c39ef32'

def fetch_categories_and_positions(sku_list,
                                   start_date=date.today()-timedelta(days=30),
                                   end_date=date.today()):
    url_list = [f'https://mpstats.io/api/wb/get/item/{sku}/by_category' for sku in sku_list]
    params = {'d1': str(start_date), 'd2': str(end_date)}
    headers = {'X-Mpstats-TOKEN': MPSTATS_TOKEN,
               'Content-Type': 'application/json'}
    items_dict = async_requests.by_urls('GET', url_list, sku_list,
                                        params=params,
                                        headers=headers,
                                        content_type='json')
    return items_dict

def fetch_orders_and_balance(sku_list,
                             start_date=date.today()-timedelta(days=30),
                             end_date=date.today()):
    url_list = [f'https://mpstats.io/api/wb/get/item/{sku}/orders_by_size' for sku in sku_list]
    params = {'d1': str(start_date), 'd2': str(end_date)}
    headers = {'X-Mpstats-TOKEN': MPSTATS_TOKEN,
               'Content-Type': 'application/json'}
    items_dict = async_requests.by_urls('GET', url_list, sku_list,
                                        params=params,
                                        headers=headers,
                                        content_type='json')
    return items_dict

def categories(items_dict, categories_dict):
    days = None
    table = list()
    for sku, value in items_dict.items():
        if days is None: # при первом проходе
            days = value['days']
            table.append(['SKU', 'Основная категория', 'Бренд']+days)
        categories = list()
        try:
            for i in range(len(days)):
                categories_by_day = [positions[i] for positions in value['categories'].values()]
                categories_count = len(categories_by_day) - categories_by_day.count('NaN')
                categories.append(categories_count)
            table.append([int(sku), categories_dict[sku]['category'], categories_dict[sku]['brand']] + categories)
        except AttributeError:
            table.append([int(sku)] + ['-']*(len(days)+2))
    return table

def positions(items_dict, categories_dict):
    days = None
    table = list()
    for sku, value in items_dict.items():
        if days is None: # при первом проходе
            days = value['days']
            table.append(['SKU', 'Основная категория', 'Бренд'] + days)  # шапка

        if len(value['categories']) == 0: table.append([int(sku)] + ['-']*(len(days)+2))
        elif categories_dict[sku]['category'] is None: table.append([int(sku)] + ['-']*(len(days)+2))
        else:
            for category, positions in value['categories'].items():
                main_category_length = 0
                if categories_dict[sku]['category'] in category and positions[-1] != 'NaN':
                    if len(category) > main_category_length:
                        main_category = category
                        main_positions = positions
                        main_category_length = len(category)
            for i in range(len(main_positions)):
                if type(main_positions[i]) != int: main_positions[i] = '-'
            table.append([int(sku), main_category, categories_dict[sku]['brand']] + main_positions)
    return table

def stocks(items_dict, categories_dict):
    # === устранение ненужных размеров ===
    actual_items_dict = dict()
    for sku, value in items_dict.items():
        for day, sizes in value.items():
            for size, balance in sizes.items():
                if size == size.upper():
                    actual_items_dict.setdefault(sku, dict()).setdefault(day, dict())[size] = items_dict[sku][day][size]
    items_dict = actual_items_dict

    days = list()
    for sku, value in items_dict.items():
        for day in value.keys():
            if day not in days: days.append(day)
    days = sorted(days)
    table = list()
    table.append(['SKU', 'Предмет', 'Бренд', 'Размер'] + days)
    for sku, value in items_dict.items():
        try:
            brand = categories_dict[sku].rsplit('/', 1)[1]
            category = categories_dict[sku].rsplit('/', 1)[0]
            left_part = [sku, category, brand]
        except AttributeError:
            left_part = [sku, '-', '-']
        try: sizes = sorted(list(list(value.values())[0].keys()))
        except IndexError:
            table.append(left_part + ['-']*(len(days)+1))
            continue
        for size in sizes:
            right_part = [size]
            for day in days:
                try:
                    stock = value[day][size]['balance']
                    if stock == 'NaN': stock = 0
                    right_part.append(stock)
                except KeyError: right_part.append('-')
            table.append(left_part+right_part)
    return table

# ================== тестовые запуски ==================
if __name__ == '__main__':
    sku_list = [44117798,16557761,35663011,35663012,16557765,16557766,12129508,16557769,16557770]
    items_dict = fetch_orders_and_balance(sku_list)
    categories_dict = wildberries.get_category_and_brand(sku_list)
    balance_table = stocks(items_dict, categories_dict)
    for row in balance_table:
        print(row)