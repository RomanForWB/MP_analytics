from datetime import date, timedelta

import modules.async_fetch as async_fetch
import modules.wildberries as wildberries

MPSTATS_TOKEN = '61f13463acf5c2.3680545125abcc4e82cf45ecd7c2cfa60c39ef32'

def fetch_categories_and_positions(sku_list,
                                   start_date=date.today()-timedelta(days=30),
                                   end_date=date.today()):
    url_list = [f'https://mpstats.io/api/wb/get/item/{sku}/by_category' for sku in sku_list]
    params = {'d1': str(start_date), 'd2': str(end_date)}
    headers = {'X-Mpstats-TOKEN': MPSTATS_TOKEN,
               'Content-Type': 'application/json'}
    items_dict = async_fetch.by_urls('GET', url_list, sku_list,
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
    items_dict = async_fetch.by_urls('GET', url_list, sku_list,
                                     params=params,
                                     headers=headers,
                                     content_type='json')
    return items_dict

def categories(items_dict):
    days = None
    table = list()
    for sku, value in items_dict.items():
        if days is None: # при первом проходе
            days = value['days']
            table.append(['SKU']+days)
        categories = list()
        try:
            for i in range(len(days)):
                categories_by_day = [positions[i] for positions in value['categories'].values()]
                categories_count = len(categories_by_day) - categories_by_day.count('NaN')
                categories.append(categories_count)
            table.append([int(sku)] + categories)
        except AttributeError:
            table.append([int(sku)] + ['-']*len(days))
    return table


def positions(items_dict):
    days = None
    table = list()
    header_categories_dict = wildberries.get_category(list(items_dict.keys()))  # категории с сайта WB
    for sku, value in items_dict.items():
        if days is None: # при первом проходе
            days = value['days']
            table.append(['SKU']+['Основная категория']+days)

        if len(value['categories']) == 0: table.append([int(sku)] + ['-']*(len(days)+1))
        elif header_categories_dict[sku] is None: table.append([int(sku)] + ['-']*(len(days)+1))
        else:
            for category, positions in value['categories'].items():
                main_category_length = 0
                if header_categories_dict[sku] in category and positions[-1] != 'NaN':
                    if len(category) > main_category_length:
                        main_category = category
                        main_positions = positions
                        main_category_length = len(category)
            for i in range(len(main_positions)):
                if type(main_positions[i]) != int: main_positions[i] = '-'
            table.append([int(sku)] + [main_category] + main_positions)
    return table

def balance(items_dict):
    table = list()
    table.append(['SKU', 'Основная категория', 'Бренд', 'Предмет', 'Размер', 'Остаток на складе'])

# ================== тестовые запуски ==================
if __name__ == '__main__':
    sku_list = [44117798,16557761,35663011,35663012,16557765,16557766,12129508,16557769,16557770]
    items_dict = fetch_categories_and_positions(sku_list)
    for sku, value in items_dict.items():
        print(sku)
        print(value)
    items_dict = fetch_orders_and_balance(sku_list, start_date=date.today(), end_date=date.today())
    for sku, value in items_dict.items():
        print(sku)
        print(value)