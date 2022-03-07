from datetime import date, timedelta
import modules.info as info
import modules.ozon.info as ozon_info
import modules.ozon.fetch as fetch

_product_ids = dict()
_products = dict()
_categories = dict()
_analytics = dict()


def _stocks_by_supplier(supplier):
    products_list = fetch.products(supplier=supplier)
    categories_dict = fetch.categories(supplier=supplier)
    table = [[ozon_info.supplier_name(supplier), product['sku'],
             product['offer_id'], categories_dict[product['category_id']],
             product['stocks']['present'], product['stocks']['coming'],
             product['stocks']['reserved'], product['status']['state_updated_at']]
             for product in products_list]
    return sorted(table, key=lambda item: item[2])


def _stocks_by_suppliers_list(suppliers_list):
    products_dict = fetch.products(suppliers_list=suppliers_list)
    categories_dict = fetch.categories(suppliers_list=suppliers_list)
    table = list()
    for supplier, products_list in products_dict.items():
        table += sorted([[ozon_info.supplier_name(supplier), product['sku'],
                         product['offer_id'], categories_dict[product['category_id']],
                         product['stocks']['present'], product['stocks']['coming'],
                         product['stocks']['reserved'], product['status']['state_updated_at']]
                         for product in products_list])
    return table


def stocks(input_data):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет',
              'На складе', 'В пути на склад', 'В пути к клиенту', 'Время обновления']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _stocks_by_suppliers_list(input_data)
        elif type(input_data[0]) == int: table = _stocks_by_sku_list(input_data)
    elif type(input_data) == str: table = _stocks_by_supplier(input_data)
    elif type(input_data) == int: table = _stocks_by_sku_list([input_data])
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
    analytics_dict = fetch.analytics(supplier=supplier, start_date=start_date)
    transactions_dict = fetch.transactions(supplier=supplier, start_date=start_date)
    return [[day, analytics['orders_value'], analytics['orders_count'], transactions_dict[day]['sales_value'],
             analytics['delivered_count'] - analytics['returns_count'] - analytics['cancellations_count'],
             -transactions_dict[day]['delivery_value'],
             # transactions_dict[day]['comission_value'], transactions_dict[day]['service_value'],
             transactions_dict[day]['total_value']] for day, analytics in analytics_dict.items()]


def _report_by_suppliers_list(suppliers_list, start_date):
    analytics_dict = fetch.analytics(suppliers_list=suppliers_list, start_date=start_date)
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
