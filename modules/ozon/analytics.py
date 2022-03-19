import re
from datetime import date, timedelta, datetime
import modules.info as info
import modules.ozon.info as ozon_info
import modules.ozon.fetch as fetch

_product_ids = dict()
_products = dict()
_categories = dict()
_analytics = dict()


def _stocks_by_supplier(supplier, old_stocks_columns):
    products_list = fetch.products(supplier=supplier)
    categories_dict = fetch.categories(supplier=supplier)
    warehouses_list = fetch.warehouses(supplier=supplier)
    old_stocks_dict = {(old_stocks_columns[0][i], int(old_stocks_columns[1][i]),
                        old_stocks_columns[2][i], old_stocks_columns[3][i]):
                           {'present': int(old_stocks_columns[4][i]), 'reserved': int(old_stocks_columns[5][i]),
                            'shipped': int(old_stocks_columns[6][i]), 'between': int(old_stocks_columns[7][i]),
                            'loss': int(old_stocks_columns[8][i]), 'update': old_stocks_columns[9][i]}
                       for i in range(len(old_stocks_columns[0]))}
    stocks_dict = dict()
    for product in products_list:
        dict_key = (ozon_info.supplier_name(supplier), product['sku'],
                    product['offer_id'], categories_dict[product['category_id']])
        stocks_dict[dict_key] = {'present': product['stocks']['present'] - product['stocks']['reserved'],
                                 'reserved': product['stocks']['reserved'],
                                 'loss': 0, 'between': 0, 'shipped': 0}
    for stock in warehouses_list:
        dict_key = (ozon_info.supplier_name(supplier), stock['sku'],
                    stock['offer_id'], stock['category'])
        stocks_dict.setdefault(dict_key, {'present': 0, 'reserved': 0})
        stocks_dict[dict_key].update({'loss': stock['stock']['loss'],
                                      'between': stock['stock']['between_warehouses'],
                                      'shipped': stock['stock']['shipped']})
    table = list()
    for key, values in stocks_dict.items():
        if old_stocks_dict.get(key) is not None:
            update = old_stocks_dict[key].pop('update')
            if old_stocks_dict[key] == stocks_dict[key]:
                table.append(list(key)+[values['present'], values['reserved'], values['shipped'],
                                        values['between'], values['loss'], update])
        else: table.append(list(key)+[values['present'], values['reserved'], values['shipped'],
                                      values['between'], values['loss'], str(datetime.now())])
    return sorted(table, key=lambda item: item[2])


def _stocks_by_suppliers_list(suppliers_list, old_stocks_columns):
    products_dict = fetch.products(suppliers_list=suppliers_list)
    warehouses_dict = fetch.warehouses(suppliers_list=suppliers_list)
    categories_dict = fetch.categories(suppliers_list=suppliers_list)
    old_stocks_dict = {(old_stocks_columns[0][i], int(old_stocks_columns[1][i]),
                        old_stocks_columns[2][i], old_stocks_columns[3][i]):
                           {'present': int(old_stocks_columns[4][i]), 'reserved': int(old_stocks_columns[5][i]),
                            'shipped': int(old_stocks_columns[6][i]), 'between': int(old_stocks_columns[7][i]),
                            'loss': int(old_stocks_columns[8][i]), 'update': old_stocks_columns[9][i]}
                       for i in range(len(old_stocks_columns[0]))}
    table = list()
    for supplier in suppliers_list:
        stocks_dict = dict()
        for product in products_dict[supplier]:
            dict_key = (ozon_info.supplier_name(supplier), product['sku'],
                        product['offer_id'], categories_dict[product['category_id']])
            stocks_dict[dict_key] = {'present': product['stocks']['present'] - product['stocks']['reserved'],
                                     'reserved': product['stocks']['reserved'],
                                     'loss': 0, 'between': 0, 'shipped': 0}
        for stock in warehouses_dict[supplier]:
            dict_key = (ozon_info.supplier_name(supplier), stock['sku'],
                        stock['offer_id'], stock['category'])
            stocks_dict.setdefault(dict_key, {'present': 0, 'reserved': 0})
            stocks_dict[dict_key].update({'loss': stock['stock']['loss'],
                                          'between': stock['stock']['between_warehouses'],
                                          'shipped': stock['stock']['shipped']})
        supplier_table = list()
        for key, values in stocks_dict.items():
            if old_stocks_dict.get(key) is not None:
                update = old_stocks_dict[key].pop('update')
                if old_stocks_dict[key] == stocks_dict[key]:
                    supplier_table.append(list(key) + [values['present'], values['reserved'], values['shipped'],
                                              values['between'], values['loss'], update])
            else: supplier_table.append(list(key) + [values['present'], values['reserved'], values['shipped'],
                                          values['between'], values['loss'], str(datetime.now())])
        table += sorted(supplier_table, key=lambda item: item[2])
    return table


def stocks(input_data, old_stocks_columns):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет',
              'Доступно', 'Зарезервировано', 'В доставке', 'Между складами', 'Потери', 'Время обновления']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _stocks_by_suppliers_list(input_data, old_stocks_columns)
    elif type(input_data) == str: table = _stocks_by_supplier(input_data, old_stocks_columns)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _positions_by_sku_list(sku_list, start_date):
    positions_dict = fetch.mpstats_positions(sku_list=sku_list, start_date=start_date)
    fetched_products_dict = fetch.products(suppliers_list=ozon_info.all_suppliers())
    products_dict = {supplier: {item['sku']: item for item in fetched_info}
                     for supplier, fetched_info in fetched_products_dict.items()}
    table = list()
    for supplier in ozon_info.all_suppliers():
        supplier_table = list()
        for sku, product in positions_dict.items():
            if sku not in sku_list or sku not in products_dict[supplier].keys(): continue
            try:
                for category, positions_list in product['categories'].items():
                    for i in range(len(positions_list)):
                        if positions_list[i] == 'NaN': positions_list[i] = '-'
                    supplier_table.append([ozon_info.supplier_name(supplier), sku,
                                           products_dict[supplier][sku]['offer_id'],
                                           category] + positions_list)
            except AttributeError:
                supplier_table.append([ozon_info.supplier_name(supplier), sku,
                                       products_dict[supplier][sku]['offer_id']] +
                                      ['-'] * (len(product['days'])+1))
        table += sorted(supplier_table, key=lambda item: item[2])
    return table


def _positions_by_suppliers_list(suppliers_list, start_date):
    positions_dict = fetch.mpstats_positions(suppliers_list=suppliers_list, start_date=start_date)
    fetched_products_dict = fetch.products(suppliers_list=suppliers_list)
    products_dict = {supplier: {item['sku']: item for item in fetched_info}
                     for supplier, fetched_info in fetched_products_dict.items()}
    table = list()
    for supplier in suppliers_list:
        supplier_table = list()
        for sku, product in positions_dict[supplier].items():
            try:
                for category, positions_list in product['categories'].items():
                    for i in range(len(positions_list)):
                        if positions_list[i] == 'NaN': positions_list[i] = '-'
                    supplier_table.append([ozon_info.supplier_name(supplier), sku,
                                           products_dict[supplier][sku]['offer_id'],
                                           category] + positions_list)
            except AttributeError: supplier_table.append([ozon_info.supplier_name(supplier), sku,
                                                         products_dict[supplier][sku]['offer_id']] +
                                                         ['-']*(len(product['days'])+1))
        table += sorted(supplier_table, key=lambda item: item[2])
    return table


def _positions_by_supplier(supplier, start_date):
    positions_dict = fetch.mpstats_positions(supplier=supplier, start_date=start_date)
    products_list = {item['sku']: item for item in fetch.products(supplier=supplier)}
    table = list()
    for sku, product in positions_dict.items():
        try:
            for category, positions_list in product['categories'].items():
                for i in range(len(positions_list)):
                    if positions_list[i] == 'NaN': positions_list[i] = '-'
                table.append([ozon_info.supplier_name(supplier), sku,
                                       products_list[sku]['offer_id'],
                                       category] + positions_list)
        except AttributeError:
            table.append([ozon_info.supplier_name(supplier), sku,
                                   products_list[sku]['offer_id']] +
                                  ['-'] * (len(product['days'])+1))
    return sorted(table, key=lambda item: item[2])


def positions(input_data, start_date=str(date.today()-timedelta(days=7))):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет'] + \
             info.days_list(start_date, to_yesterday=True)
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _positions_by_suppliers_list(input_data, start_date)
        elif type(input_data[0]) == int: table = _positions_by_sku_list(input_data, start_date)
    elif type(input_data) == str: table = _positions_by_supplier(input_data, start_date)
    elif type(input_data) == int: table = _positions_by_sku_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _categories_by_sku_list(sku_list, start_date):
    days = info.days_list(start_date, to_yesterday=True)
    positions_dict = fetch.mpstats_positions(sku_list=sku_list, start_date=start_date)
    products_dict = fetch.products(suppliers_list=ozon_info.all_suppliers())
    table = list()
    for supplier, products in products_dict.items():
        supplier_table = list()
        for product in products:
            sku = product['sku']
            categories_by_days = list()
            try:
                for i in range(len(days)):
                    categories_raw = [values[i] for values in positions_dict[sku]['categories'].values()]
                    categories_count = len(categories_raw) - categories_raw.count('NaN')
                    categories_by_days.append(categories_count)
                table.append([ozon_info.supplier_name(supplier), sku, product['offer_id'],
                              list(positions_dict[sku]['categories'].keys())[0]] + categories_by_days)
            except AttributeError:
                table.append([ozon_info.supplier_name(supplier), sku, product['offer_id']] +
                             ['-'] * (len(days) + 1))
            except KeyError: pass
        table += sorted(supplier_table, key=lambda item: item[2])
    return table


def _categories_by_supplier(supplier, start_date):
    days = info.days_list(start_date, to_yesterday=True)
    positions_dict = fetch.mpstats_positions(supplier=supplier, start_date=start_date)
    products_list = fetch.products(supplier=supplier)
    table = list()
    for product in products_list:
        sku = product['sku']
        categories_by_days = list()
        try:
            for i in range(len(days)):
                categories_raw = [values[i] for values in positions_dict[sku]['categories'].values()]
                categories_count = len(categories_raw) - categories_raw.count('NaN')
                categories_by_days.append(categories_count)
            table.append([ozon_info.supplier_name(supplier), sku, product['offer_id'],
                          list(positions_dict[sku]['categories'].keys())[0]] + categories_by_days)
        except (AttributeError, KeyError):
            table.append([ozon_info.supplier_name(supplier), sku, product['offer_id']] +
                         ['-'] * (len(days) + 1))
    return sorted(table, key=lambda item: item[2])


def _categories_by_suppliers_list(suppliers_list, start_date):
    days = info.days_list(start_date, to_yesterday=True)
    positions_dict = fetch.mpstats_positions(suppliers_list=suppliers_list, start_date=start_date)
    products_dict = fetch.products(suppliers_list=suppliers_list)
    table = list()
    for supplier, products in products_dict.items():
        supplier_table = list()
        for product in products:
            sku = product['sku']
            categories_by_days = list()
            try:
                for i in range(len(days)):
                    categories_raw = [values[i] for values in positions_dict[sku]['categories'].values()]
                    categories_count = len(categories_raw) - categories_raw.count('NaN')
                    categories_by_days.append(categories_count)
                table.append([ozon_info.supplier_name(supplier), sku, product['offer_id'],
                              list(positions_dict[sku]['categories'].keys())[0]] + categories_by_days)
            except (AttributeError, KeyError):
                table.append([ozon_info.supplier_name(supplier), sku, product['offer_id']] +
                             ['-'] * (len(days) + 1))
        table += sorted(supplier_table, key=lambda item: item[2])
    return table


def categories(input_data, start_date=str(date.today()-timedelta(days=7))):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет'] + \
             info.days_list(start_date, to_yesterday=True)
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _categories_by_suppliers_list(input_data, start_date)
        elif type(input_data[0]) == int: table = _categories_by_sku_list(input_data, start_date)
    elif type(input_data) == str: table = _categories_by_supplier(input_data, start_date)
    elif type(input_data) == int: table = _categories_by_sku_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _report_by_supplier(supplier, start_date):
    analytics_dict = fetch.report(supplier=supplier, start_date=start_date)
    transactions_dict = fetch.transactions(supplier=supplier, start_date=start_date)
    return [[day, analytics['orders_value'], analytics['orders_count'], transactions_dict[day]['sales_value'],
             analytics['delivered_count'] - analytics['returns_count'] - analytics['cancellations_count'],
             -transactions_dict[day]['delivery_value'],
             # transactions_dict[day]['comission_value'], transactions_dict[day]['service_value'],
             transactions_dict[day]['total_value']] for day, analytics in analytics_dict.items()]


def _report_by_suppliers_list(suppliers_list, start_date):
    analytics_dict = fetch.report(suppliers_list=suppliers_list, start_date=start_date)
    transactions_dict = fetch.transactions(suppliers_list=suppliers_list, start_date=start_date)
    dates = info.dates_list(from_date=start_date, to_yesterday=True)
    table = [[day, sum([analytics_dict[supplier][day]['orders_value'] for supplier in suppliers_list]),
                  sum([analytics_dict[supplier][day]['orders_count'] for supplier in suppliers_list]),
                  sum([transactions_dict[supplier][day]['sales_value'] for supplier in suppliers_list]),
                  sum([analytics_dict[supplier][day]['delivered_count'] - \
                       analytics_dict[supplier][day]['returns_count'] - \
                       analytics_dict[supplier][day]['cancellations_count'] for supplier in suppliers_list]),
                  sum([-transactions_dict[supplier][day]['delivery_value'] for supplier in suppliers_list]),
                  # sum([transactions_dict[supplier][day]['comission_value'] for supplier in suppliers_list]),
                  # sum([transactions_dict[supplier][day]['service_value'] for supplier in suppliers_list]),
                  sum([transactions_dict[supplier][day]['total_value'] for supplier in suppliers_list])]
                  for day in dates]
    return table


def report(input_data, start_date):
    header = ['Дата', 'Заказано руб.', 'Заказано шт.', 'Выкупили руб.', 'Выкупили шт.', 'Логистика руб.', 'К перечислению']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _report_by_suppliers_list(input_data, start_date)
        # elif type(input_data[0]) == int: table = _report_by_sku_list(input_data, start_date)
    elif type(input_data) == str: table = _report_by_supplier(input_data, start_date)
    # elif type(input_data) == int: table = _report_by_sku_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _orders_count_by_supplier(supplier, start_date):
    products_list = fetch.products(supplier=supplier)
    products_dict = {item['sku']: item for item in products_list}
    categories_dict = fetch.categories(supplier=supplier)
    orders_dict = fetch.orders(supplier=supplier, start_date=start_date)
    days = info.days_list(from_date=start_date)
    table = list()
    for sku, days_values in orders_dict.items():
        days_values = {datetime.strptime(key, '%Y-%m-%d').strftime('%d.%m'): values
                       for key, values in days_values.items()}
        row = [ozon_info.supplier_name(supplier), sku,
                   products_dict[sku]['offer_id'],
                   categories_dict[products_dict[sku]['category_id']]]
        for day in days: row.append(days_values[day]['orders_count'])
        row.append(sum([day_value['orders_count'] for day_value in days_values.values()]))
        try: row.append(sum([day_value['orders_value'] for day_value in days_values.values()]) /
                       sum([day_value['orders_count'] for day_value in days_values.values()]))
        except ZeroDivisionError: row.append('')
        row.append(sum([day_value['orders_value'] for day_value in days_values.values()]))
        table.append(row)
    return sorted(table, key=lambda item: item[2])


def _orders_count_by_suppliers_list(suppliers_list, start_date):
    products_dict = fetch.products(suppliers_list=suppliers_list)
    categories_dict = fetch.categories(suppliers_list=suppliers_list)
    orders_dict = fetch.orders(suppliers_list=suppliers_list, start_date=start_date)
    days = info.days_list(from_date=start_date)
    table = list()
    for supplier in suppliers_list:
        supplier_table = list()
        supplier_products_dict = {item['sku']: item for item in products_dict[supplier]}
        for sku, days_values in orders_dict[supplier].items():
            try:
                days_values = {datetime.strptime(key, '%Y-%m-%d').strftime('%d.%m'): values
                               for key, values in days_values.items()}
                row = [ozon_info.supplier_name(supplier), sku,
                       supplier_products_dict[sku]['offer_id'],
                       categories_dict[supplier_products_dict[sku]['category_id']]]
                for day in days: row.append(days_values[day]['orders_count'])
                row.append(sum([day_value['orders_count'] for day_value in days_values.values()]))
                try: row.append(sum([day_value['orders_value'] for day_value in days_values.values()]) /
                           sum([day_value['orders_count'] for day_value in days_values.values()]))
                except ZeroDivisionError: row.append('')
                row.append(sum([day_value['orders_value'] for day_value in days_values.values()]))
                supplier_table.append(row)
            except KeyError: pass
        table += sorted(supplier_table, key=lambda item: item[2])
    return table


def orders_count(input_data, start_date):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет'] + \
             info.days_list(from_date=start_date) + ['Итого', 'Средняя цена', 'Сумма заказов']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _orders_count_by_suppliers_list(input_data, start_date)
        # elif type(input_data[0]) == int: table = _report_by_sku_list(input_data, start_date)
    elif type(input_data) == str: table = _orders_count_by_supplier(input_data, start_date)
    # elif type(input_data) == int: table = _report_by_sku_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _orders_value_by_supplier(supplier, start_date):
    products_list = fetch.products(supplier=supplier)
    products_dict = {item['sku']: item for item in products_list}
    categories_dict = fetch.categories(supplier=supplier)
    orders_dict = fetch.orders(supplier=supplier, start_date=start_date)
    days = info.days_list(from_date=start_date)
    table = list()
    for sku, days_values in orders_dict.items():
        days_values = {datetime.strptime(key, '%Y-%m-%d').strftime('%d.%m'): values
                       for key, values in days_values.items()}
        row = [ozon_info.supplier_name(supplier), sku,
                   products_dict[sku]['offer_id'],
                   categories_dict[products_dict[sku]['category_id']]]
        for day in days: row.append(days_values[day]['orders_value'])
        row.append(sum([day_value['orders_count'] for day_value in days_values.values()]))
        try: row.append(sum([day_value['orders_value'] for day_value in days_values.values()]) /
                       sum([day_value['orders_count'] for day_value in days_values.values()]))
        except ZeroDivisionError: row.append('')
        row.append(sum([day_value['orders_value'] for day_value in days_values.values()]))
        table.append(row)
    return sorted(table, key=lambda item: item[2])


def _orders_value_by_suppliers_list(suppliers_list, start_date):
    products_dict = fetch.products(suppliers_list=suppliers_list)
    categories_dict = fetch.categories(suppliers_list=suppliers_list)
    orders_dict = fetch.orders(suppliers_list=suppliers_list, start_date=start_date)
    days = info.days_list(from_date=start_date)
    table = list()
    for supplier in suppliers_list:
        supplier_table = list()
        supplier_products_dict = {item['sku']: item for item in products_dict[supplier]}
        for sku, days_values in orders_dict[supplier].items():
            try:
                days_values = {datetime.strptime(key, '%Y-%m-%d').strftime('%d.%m'): values
                               for key, values in days_values.items()}
                row = [ozon_info.supplier_name(supplier), sku,
                       supplier_products_dict[sku]['offer_id'],
                       categories_dict[supplier_products_dict[sku]['category_id']]]
                for day in days: row.append(days_values[day]['orders_value'])
                row.append(sum([day_value['orders_count'] for day_value in days_values.values()]))
                try: row.append(sum([day_value['orders_value'] for day_value in days_values.values()]) /
                           sum([day_value['orders_count'] for day_value in days_values.values()]))
                except ZeroDivisionError: row.append('')
                row.append(sum([day_value['orders_value'] for day_value in days_values.values()]))
                supplier_table.append(row)
            except KeyError: pass
        table += sorted(supplier_table, key=lambda item: item[2])
    return table


def orders_value(input_data, start_date):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет'] + \
             info.days_list(from_date=start_date) + ['Итого', 'Средняя цена', 'Сумма заказов']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _orders_value_by_suppliers_list(input_data, start_date)
        # elif type(input_data[0]) == int: table = _report_by_sku_list(input_data, start_date)
    elif type(input_data) == str: table = _orders_value_by_supplier(input_data, start_date)
    # elif type(input_data) == int: table = _report_by_sku_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _orders_category_by_suppliers_list(suppliers_list, start_date, visible_categories):
    products_dict = fetch.products(suppliers_list=suppliers_list)
    categories_dict = fetch.categories(suppliers_list=suppliers_list)
    orders_dict = fetch.orders(suppliers_list=suppliers_list, start_date=start_date)
    days = info.days_list(from_date=start_date)
    orders_by_category_dict = dict()
    other_days_values = {day: 0 for day in days}
    for supplier in suppliers_list:
        supplier_products_dict = {item['sku']: item for item in products_dict[supplier]}
        for sku, days_values in orders_dict[supplier].items():
            try:
                category_words = re.split(r'\s+', categories_dict[supplier_products_dict[sku]['category_id']])
                category = ' '.join(list(filter(lambda item: 'женск' not in item.lower(), category_words)))
                days_values = {datetime.strptime(key, '%Y-%m-%d').strftime('%d.%m'): values
                               for key, values in days_values.items()}
                for day in days:
                    if visible_categories is not None:
                        if category in visible_categories:
                            orders_by_category_dict.setdefault(category, {day: 0 for day in days})
                            orders_by_category_dict[category][day] += days_values[day]['orders_value']
                        else: other_days_values[day] += days_values[day]['orders_value']
                    else:
                        orders_by_category_dict.setdefault(category, {day: 0 for day in days})
                        orders_by_category_dict[category][day] += days_values[day]['orders_value']
            except KeyError: pass
    table = [[category] + [value for day, value in days_values.items()]
             for category, days_values in orders_by_category_dict.items()]
    table.sort(key=lambda item: sum(item[1:]), reverse=True)
    if sum(other_days_values.values()) > 0:
        table.append(['Остальное'] + [other_days_values[day] for day in days])
    table.append(['Итого'] + [sum([values[day] for values in orders_by_category_dict.values()])
                              for day in days])
    return table


def orders_category(input_data, start_date, categories_list=None):
    header = ['Заказано руб.'] + \
             info.days_list(from_date=start_date)
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _orders_category_by_suppliers_list(input_data, start_date, categories_list)
        # elif type(input_data[0]) == int: table = _report_by_sku_list(input_data, start_date)
    elif type(input_data) == str: table = _orders_category_by_supplier(input_data, start_date, categories_list)
    # elif type(input_data) == int: table = _report_by_sku_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table