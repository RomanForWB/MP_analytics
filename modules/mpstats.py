from datetime import date, timedelta

import modules.async_fetch as async_fetch
import modules.wildberries as wildberries

MPSTATS_TOKEN = '61f13463acf5c2.3680545125abcc4e82cf45ecd7c2cfa60c39ef32'

def get_categories_and_positions(sku_list,
                                 start_date=date.today()-timedelta(days=30),
                                 end_date=date.today()):
    url_list = [f'https://mpstats.io/api/wb/get/item/{sku}/by_category' for sku in sku_list]
    params = {'d1': str(start_date), 'd2': str(end_date)}
    headers = {'X-Mpstats-TOKEN': MPSTATS_TOKEN,
               'Content-Type': 'application/json'}
    items_list = async_fetch.by_urls('GET', url_list,
                                     params=params,
                                     headers=headers,
                                     additional_ids=sku_list,
                                     content_type='json')
    return items_list

def categories(items_list):
    days = None
    table = list()
    for item in items_list:
        sku = item['id']
        if days is None: # при первом проходе
            days = item['days']
            table.append(['SKU']+days)
        categories_result = list()
        try:
            for day in range(len(days)):
                categories_by_day = [value[day] for value in item['categories'].values()]
                categories_count = len(categories_by_day)-categories_by_day.count('NaN')
                categories_result.append(categories_count)
            table.append([int(sku)] + categories_result)
        except AttributeError:
            table.append([int(sku)] + ['-']*len(days))
    return table

def positions(sku_list, items_list):
    days = None
    table = list()
    main_categories_list = wildberries.get_main_category(sku_list)
    for item in items_list:
        sku = item['id']
        if days is None: # при первом проходе
            days = item['days']
            table.append(['SKU']+['Основная категория']+days)
        if len(item['categories']) == 0: table.append([int(sku)] + ['-'] + ['-']*len(days))

        else:
            for i in range(len(main_categories_list)):
                try:
                    if sku == main_categories_list[i][0] and main_categories_list[i][1] is None:
                        table.append([int(sku)] + ['-'] + ['-'] * len(days))
                        break
                    elif sku == main_categories_list[i][0]:
                        for category, values in item['categories'].items():
                            main_category_length = 0
                            if main_categories_list[i][1] in category and values[-1] != 'NaN':
                                if len(category) > main_category_length:
                                    main_category = category
                                    main_values = values
                                    main_category_length = len(category)
                        for i in range(len(main_values)):
                            if type(main_values[i]) != int: main_values[i] = '-'
                        table.append([int(sku)] + [main_category] + main_values)
                        break
                except IndexError: pass
    return table


# ================== тестовые запуски ==================
if __name__ == '__main__':
    sku_list = [44117798,16557761,35663011,35663012,16557765,16557766,12129508,16557769,16557770]
    items_list = get_categories_and_positions(sku_list)
    print(items_list)
    # category_table = categories(items_list)
    # print(category_table)