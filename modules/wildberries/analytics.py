from datetime import date, timedelta, datetime

import modules.wildberries.info as wb_info
import modules.wildberries.fetch as fetch
import modules.info as info


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
    cards = fetch.cards(supplier=supplier)
    imt_list = [card['imtId'] for card in cards]
    feedbacks_dict = fetch.feedbacks(imt_list, count)
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
    cards_dict = fetch.cards(suppliers_list=suppliers_list)
    supplier_cards_dict = {supplier: [] for supplier in suppliers_list}
    imt_list = list()
    for nm in nm_list:
        for supplier, cards in cards_dict.items():
            for card in cards:
                for nomenclature in card['nomenclatures']:
                    if nm == nomenclature['nmId']:
                        supplier_cards_dict[supplier].append(card)
                        imt_list.append(card['imtId'])
    feedbacks_dict = fetch.feedbacks(imt_list, count)
    result_table = list()
    for supplier, cards in supplier_cards_dict.items():
        supplier_table = list()
        for card in cards:
            data_list = _feedbacks_by_data(supplier, card, feedbacks_dict[card['imtId']])
            supplier_table += data_list
        result_table += sorted(supplier_table, key=lambda item: item[2])
    return result_table


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


def _orders_count_by_supplier(supplier, start_date):
    orders_list = fetch.orders(supplier=supplier, start_date=start_date)
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
    orders_dict = fetch.orders(suppliers_list=suppliers_list, start_date=start_date)
    days = info.days_list(start_date)
    table = list()
    for supplier, orders_list in orders_dict.items():
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

def _orders_count_by_nm_list(nm_list, start_date):
    orders_dict = fetch.orders(suppliers_list=wb_info.all_suppliers(), start_date=start_date)
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


def orders_count(input_data, start_date=str(date.today()-timedelta(days=6))):
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


def _orders_value_by_supplier(supplier, start_date):
    orders_list = fetch.orders(supplier=supplier, start_date=start_date)
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
    orders_dict = fetch.orders(suppliers_list=suppliers_list, start_date=start_date)
    days = info.days_list(start_date)
    table = list()
    for supplier, orders_list in orders_dict.items():
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


def _orders_value_by_nm_list(nm_list, start_date):
    orders_dict = fetch.orders(suppliers_list=wb_info.all_suppliers(), start_date=start_date)
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


def orders_value(input_data, start_date=str(date.today()-timedelta(days=6))):
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


def _orders_category_by_supplier(supplier, start_date, visible_categories):
    orders_list = fetch.orders(supplier=supplier, start_date=start_date)
    days = info.days_list(start_date)
    buyouts_dict = dict()
    for item in fetch.buyouts():
        buyouts_dict.setdefault(int(item[1]), {'buyouts': []})
        buyouts_dict[int(item[1])]['buyouts'].append([datetime.strptime(item[0], '%d.%m.%Y').strftime('%d.%m'), int(item[2])])
    categories_dict = dict()
    for order in orders_list:
        if order['category'] == 'Обувь': category = 'Обувь'
        else: category = order['subject']
        if category not in categories_dict.keys():
            categories_dict[category] = {day: 0 for day in days}
        try:
            day = datetime.strptime(order['date'], '%Y-%m-%dT%H:%M:%S').date().strftime('%d.%m')
            final_price = order['totalPrice'] * (100 - order['discountPercent']) / 100
            categories_dict[category][day] += final_price
            if buyouts_dict.get(order['nmId']) is not None:
                buyouts_dict[order['nmId']].update({'category': category, 'price': final_price})
        except KeyError: pass

    for nm, values in buyouts_dict.items():
        if values.get('category') is not None:
            for buyout in values['buyouts']:
                if buyout[0] in days: categories_dict[values['category']][buyout[0]] -= values['price']

    table = list()
    total = [0] * len(days)
    other = [0] * len(days)
    for category, days_info in categories_dict.items():
        values = [days_info[day] for day in days]
        if category in visible_categories: table.append([category] + values)
        else: other = [other[i]+values[i] for i in range(len(values))]
        total = [total[i]+values[i] for i in range(len(values))]

    table.sort(key=lambda item: sum(item[1:]), reverse=True)
    table += [["Остальное"] + other, ["Итого"] + total]
    return table


def _orders_category_by_suppliers_list(suppliers_list, start_date, visible_categories):
    orders_dict = fetch.orders(suppliers_list=suppliers_list, start_date=start_date)
    days = info.days_list(start_date)
    buyouts_dict = dict()
    for item in fetch.buyouts():
        buyouts_dict.setdefault(int(item[1]), {'buyouts': []})
        buyouts_dict[int(item[1])]['buyouts'].append(
            [datetime.strptime(item[0], '%d.%m.%Y').strftime('%d.%m'), int(item[2])])
    categories_dict = dict()
    for supplier, orders_list in orders_dict.items():
        for order in orders_list:
            if order['category'] == 'Обувь': category = 'Обувь'
            else: category = order['subject']
            if category not in categories_dict.keys():
                categories_dict[category] = {day: 0 for day in days}
            try:
                day = datetime.strptime(order['date'], '%Y-%m-%dT%H:%M:%S').date().strftime('%d.%m')
                final_price = order['totalPrice'] * (100 - order['discountPercent']) / 100
                categories_dict[category][day] += final_price
                if buyouts_dict.get(order['nmId']) is not None:
                    buyouts_dict[order['nmId']].update({'category': category, 'price': final_price})
            except KeyError: pass

    for nm, values in buyouts_dict.items():
        if values.get('category') is not None:
            for buyout in values['buyouts']:
                if buyout[0] in days: categories_dict[values['category']][buyout[0]] -= values['price']

    table = list()
    total = [0]*len(days)
    other = [0]*len(days)
    for category, days_info in categories_dict.items():
        values = [days_info[day] for day in days]
        if category in visible_categories: table.append([category] + values)
        else: other = [other[i] + values[i] for i in range(len(values))]
        total = [total[i] + values[i] for i in range(len(values))]

    table.sort(key=lambda item: sum(item[1:]), reverse=True)
    table += [["Остальное"] + other, ["Итого"] + total]
    return table


def _orders_category_by_nm_list(nm_list, start_date, visible_categories):
    orders_dict = fetch.orders(suppliers_list=wb_info.all_suppliers(), start_date=start_date)
    days = info.days_list(start_date)
    buyouts_dict = dict()
    for item in fetch.buyouts():
        buyouts_dict.setdefault(int(item[1]), {'buyouts': []})
        buyouts_dict[int(item[1])]['buyouts'].append(
            [datetime.strptime(item[0], '%d.%m.%Y').strftime('%d.%m'), int(item[2])])
    categories_dict = dict()
    for supplier, orders_list in orders_dict.items():
        for order in orders_list:
            if order['nmId'] not in nm_list: continue
            if order['category'] == 'Обувь': category = 'Обувь'
            else: category = order['subject']
            if category not in categories_dict.keys():
                categories_dict[category] = {day: 0 for day in days}
            try:
                day = datetime.strptime(order['date'], '%Y-%m-%dT%H:%M:%S').date().strftime('%d.%m')
                final_price = order['totalPrice'] * (100 - order['discountPercent']) / 100
                categories_dict[category][day] += final_price
                if buyouts_dict.get(order['nmId']) is not None:
                    buyouts_dict[order['nmId']].update({'category': category, 'price': final_price})
            except KeyError: pass

    for nm, values in buyouts_dict.items():
        if values.get('category') is not None:
            for buyout in values['buyouts']:
                if buyout[0] in days: categories_dict[values['category']][buyout[0]] -= values['price']

    table = list()
    total = [0 for day in days]
    other = [0 for day in days]
    for category, days_info in categories_dict.items():
        values = [days_info[day] for day in days]
        if category in visible_categories: table.append([category] + values)
        else: other = [other[i]+values[i] for i in range(len(values))]
        total = [total[i]+values[i] for i in range(len(values))]

    table.sort(key=lambda item: sum(item[1:]), reverse=True)
    table += [["Остальное"] + other, ["Итого"] + total]
    return table


def orders_category(input_data, start_date=str(date.today()-timedelta(days=6)), categories_list=None):
    header = ['Заказано руб.'] + info.days_list(start_date)
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _orders_category_by_suppliers_list(input_data, start_date, categories_list)
        elif type(input_data[0]) == int: table = _orders_category_by_nm_list(input_data, start_date, categories_list)
    elif type(input_data) == str: table = _orders_category_by_supplier(input_data, start_date, categories_list)
    elif type(input_data) == int:  table = _orders_category_by_nm_list([input_data], start_date, categories_list)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _stocks_by_supplier(supplier, start_date):
    stocks_list = fetch.stocks(supplier=supplier, start_date=start_date)
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
    stocks_dict = fetch.stocks(suppliers_list=suppliers_list, start_date=start_date)
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
    stocks_dict = fetch.stocks(suppliers_list=wb_info.all_suppliers(), start_date=start_date)
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


def stocks(input_data, start_date=str(date.today()-timedelta(days=6))):
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


def _report_by_supplier(supplier, start_date):
    report_dict = fetch.report(supplier=supplier)
    days_dict = dict()
    for year_values in report_dict['consolidatedYears']:
        for month_values in year_values['consolidatedMonths']:
            for day_values in month_values['consolidatedDays']:
                day = day_values['day'].split('.')[0]
                month = month_values['month']
                year = year_values['year']
                days_dict[f"{year}-{month}-{day}"] = day_values
    table = [[day,
              days_dict[day]['ordered'], days_dict[day]['goodsOrdered'],
              days_dict[day]['paymentSalesRub'], days_dict[day]['paymentSalesPiece'],
              days_dict[day]['logisticsCost'], days_dict[day]['totalToTransfer']]
             for day in info.dates_list(from_date=start_date, to_yesterday=True)]
    return table


def _report_by_suppliers_list(suppliers_list, start_date):
    report_dict = fetch.report(suppliers_list=suppliers_list)
    days_dict = dict()
    for supplier, report in report_dict.items():
        for year_values in report['consolidatedYears']:
            for month_values in year_values['consolidatedMonths']:
                for day_values in month_values['consolidatedDays']:
                    day = day_values['day'].split('.')[0]
                    month = month_values['month']
                    year = year_values['year']
                    if days_dict.get(f"{year}-{month}-{day}") is None:
                        days_dict[f"{year}-{month}-{day}"] = day_values
                    else:
                        for key, value in day_values.items():
                            days_dict[f"{year}-{month}-{day}"][key] += value
    table = [[day,
              days_dict[day]['ordered'], days_dict[day]['goodsOrdered'],
              days_dict[day]['paymentSalesRub'], days_dict[day]['paymentSalesPiece'],
              days_dict[day]['logisticsCost'], days_dict[day]['totalToTransfer']]
             for day in info.dates_list(from_date=start_date, to_yesterday=True)]
    return table


def report(input_data, start_date=str(date.today()-timedelta(days=7))):
    header = ['Дата', 'Заказано руб.', 'Заказано шт.', 'Выкупили руб.', 'Выкупили шт.', 'Логистика руб.', 'К перечислению']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _report_by_suppliers_list(input_data, start_date)
        elif type(input_data[0]) == int: table = _report_by_nm_list(input_data, start_date)
    elif type(input_data) == str: table = _report_by_supplier(input_data, start_date)
    elif type(input_data) == int: table = _report_by_nm_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _shipments_by_suppliers_list(suppliers_list):
    today = str(date.today())
    start_date = str(date.today() - timedelta(days=7))
    stocks_dict = fetch.stocks(suppliers_list=suppliers_list)
    orders_dict = fetch.orders(suppliers_list=suppliers_list, start_date=start_date)
    table = list()
    for supplier in suppliers_list:
        items_dict = dict()
        for stock in stocks_dict[supplier]:
            dict_key = (wb_info.supplier_name(supplier),
                        stock['nmId'],
                        stock['supplierArticle'],
                        f"{stock['category']}/{stock['subject']}",
                        stock['brand'],
                        stock['techSize'])
            items_dict.setdefault(dict_key, {'orders': 0, 'stock': 0, 'date': start_date})
            items_dict[dict_key]['stock'] += stock['quantity']
            if items_dict[dict_key]['date'] < stock['lastChangeDate']: items_dict[dict_key]['date'] = stock[
                'lastChangeDate']
        for order in orders_dict[supplier]:
            if today in order['date']: continue
            dict_key = (wb_info.supplier_name(supplier),
                        order['nmId'],
                        order['supplierArticle'],
                        f"{order['category']}/{order['subject']}",
                        order['brand'],
                        order['techSize'])
            items_dict.setdefault(dict_key, {'orders': 0, 'stock': 0, 'date': start_date})
            items_dict[dict_key]['orders'] += order['quantity']
        supplier_table = list()
        for key, value in items_dict.items():
            if value['stock'] - value['orders'] > 0: ship = 0
            elif value['stock'] - value['orders'] < -10: ship = value['orders'] - value['stock']
            elif value['orders'] == 0:
                if value['stock'] < 10: ship = 10 - value['stock']
                else: ship = 0
            else:
                if ((value['stock'] - value['orders']) * (1.5 + value['stock']/value['orders'])) > -10: ship = 10
                else: ship = -(value['stock'] - value['orders']) * (1.5 + value['stock']/value['orders'])
            supplier_table.append(list(key) + [value['orders'], value['stock'],
                                               value['stock'] - value['orders'],
                                               ship, value['date']])
        table += sorted(supplier_table, key=lambda item: item[2])
    return table


def _shipments_by_supplier(supplier):
    today = str(date.today())
    start_date = str(date.today()-timedelta(days=7))
    stocks_list = fetch.stocks(supplier=supplier)
    orders_list = fetch.orders(supplier=supplier, start_date=start_date)
    items_dict = dict()
    for stock in stocks_list:
        dict_key = (wb_info.supplier_name(supplier),
                    stock['nmId'],
                    stock['supplierArticle'],
                    f"{stock['category']}/{stock['subject']}",
                    stock['brand'],
                    stock['techSize'])
        items_dict.setdefault(dict_key, {'orders': 0, 'stock': 0, 'date': start_date})
        items_dict[dict_key]['stock'] += stock['quantity']
        if items_dict[dict_key]['date'] < stock['lastChangeDate']: items_dict[dict_key]['date'] = stock['lastChangeDate']
    for order in orders_list:
        if today in order['date']: continue
        dict_key = (wb_info.supplier_name(supplier),
                    order['nmId'],
                    order['supplierArticle'],
                    f"{order['category']}/{order['subject']}",
                    order['brand'],
                    order['techSize'])
        items_dict.setdefault(dict_key, {'orders': 0, 'stock': 0, 'date': start_date})
        items_dict[dict_key]['orders'] += order['quantity']
    table = list()
    for key, value in items_dict.items():
        if value['stock'] - value['orders'] > 0: ship = 0
        elif value['stock'] - value['orders'] < -10: ship = value['orders'] - value['stock']
        elif value['orders'] == 0:
            if value['stock'] < 10: ship = 10 - value['stock']
            else: ship = 0
        else:
            if ((value['stock'] - value['orders']) * (1.5 + value['stock'] / value['orders'])) > -10: ship = 10
            else: ship = -(value['stock'] - value['orders']) * (1.5 + value['stock'] / value['orders'])
        table.append(list(key) + [value['orders'], value['stock'],
                                  value['stock'] - value['orders'],
                                  ship, value['date']])
    return sorted(table, key=lambda item: item[2])


def shipments(input_data):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд',
              'Размер', 'Заказы', 'Остаток', 'Дефицит', 'Отгрузка', 'Время обновления']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _shipments_by_suppliers_list(input_data)
        elif type(input_data[0]) == int: table = _shipments_by_nm_list(input_data)
    elif type(input_data) == str: table = _shipments_by_supplier(input_data)
    elif type(input_data) == int: table = _shipments_by_nm_list([input_data])
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _buyout_percent_by_supplier(supplier, weeks):
    report_list = fetch.detail_report(supplier=supplier, weeks=weeks)
    items_dict = dict()
    for sale in report_list:
        dict_key = (wb_info.supplier_name(supplier), sale['nm_id'],
                    sale['sa_name'], sale['subject_name'], sale['brand_name'], sale['ts_name'])
        items_dict.setdefault(dict_key, {'pure': 0, 'sales': 0, 'returns': 0, 'cancel': 0, 'update': ''})
        if sale['doc_type_name'] == 'Продажа' and sale['quantity'] == 1:
            items_dict[dict_key]['sales'] += 1
            items_dict[dict_key]['pure'] += 1
        elif sale['doc_type_name'] == 'Продажа' and sale['return_amount'] == 1:
            items_dict[dict_key]['cancel'] += 1
        elif sale['doc_type_name'] == 'Возврат' and sale['quantity'] == 1:
            items_dict[dict_key]['returns'] += 1
            items_dict[dict_key]['pure'] -= 1
        if sale['rr_dt'] > items_dict[dict_key]['update']: items_dict[dict_key]['update'] = sale['rr_dt']
    table = list()
    for key, value in items_dict.items():
        if (value['sales'] + value['cancel']) == 0:
            table.append(list(key) + [value['pure'], value['sales'],
                                               value['returns'], value['cancel'],
                                               0, value['update']])
        else:
            table.append(list(key) + [value['pure'], value['sales'],
                                               value['returns'], value['cancel'],
                                               value['pure'] / (value['sales'] + value['cancel']),
                                               value['update']])
    return sorted(table, key=lambda item: item[2])


def _buyout_percent_by_suppliers_list(suppliers_list, weeks):
    report_dict = fetch.detail_report(suppliers_list=suppliers_list, weeks=weeks)
    table = list()
    for supplier, report_list in report_dict.items():
        items_dict = dict()
        for sale in report_list:
            dict_key = (wb_info.supplier_name(supplier), sale['nm_id'],
                        sale['sa_name'], sale['subject_name'], sale['brand_name'], sale['ts_name'])
            items_dict.setdefault(dict_key, {'pure': 0, 'sales': 0, 'returns': 0, 'cancel': 0, 'update': ''})
            if sale['doc_type_name'] == 'Продажа' and sale['quantity'] == 1:
                items_dict[dict_key]['sales'] += 1
                items_dict[dict_key]['pure'] += 1
            elif sale['doc_type_name'] == 'Продажа' and sale['return_amount'] == 1:
                items_dict[dict_key]['cancel'] += 1
            elif sale['doc_type_name'] == 'Возврат' and sale['quantity'] == 1:
                items_dict[dict_key]['returns'] += 1
                items_dict[dict_key]['pure'] -= 1
            if sale['rr_dt'] > items_dict[dict_key]['update']: items_dict[dict_key]['update'] = sale['rr_dt']
        supplier_table = list()
        for key, value in items_dict.items():
            if (value['sales'] + value['cancel']) == 0:
                supplier_table.append(list(key) + [value['pure'], value['sales'],
                                                   value['returns'], value['cancel'],
                                                   0, value['update']])
            else: supplier_table.append(list(key)+[value['pure'], value['sales'],
                                     value['returns'], value['cancel'],
                                     value['pure']/(value['sales']+value['cancel']),
                                     value['update']])
        table += sorted(supplier_table, key=lambda item: item[2])
    return table


def buyout_percent(input_data, weeks=4):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд',
              'Размер', 'Чистые продажи', 'Продажи', 'Возвраты', 'Отказы', 'Процент выкупа', 'Последнее обновление']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _buyout_percent_by_suppliers_list(input_data, weeks)
        elif type(input_data[0]) == int: table = _buyout_percent_by_nm_list(input_data)
    elif type(input_data) == str: table = _buyout_percent_by_supplier(input_data, weeks)
    elif type(input_data) == int: table = _buyout_percent_by_nm_list([input_data])
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _positions_by_supplier(supplier, start_date):
    info_dict = {item['id']: item for item in fetch.mpstats_info(supplier=supplier)}
    cards_list = fetch.cards(supplier=supplier)
    positions_dict = fetch.mpstats_positions(supplier=supplier, start_date=start_date)
    table = list()
    for card in cards_list:
        for nomenclature in card['nomenclatures']:
            nm = nomenclature['nmId']
            try:
                category = info_dict[nm]['category']
                positions_list = positions_dict[nm]['categories'][category]
                for i in range(len(positions_list)):
                    if positions_list[i] == 'NaN': positions_list[i] = '-'
                table.append([wb_info.supplier_name(supplier), nm,
                              card['supplierVendorCode'] + nomenclature['vendorCode'],
                              category, info_dict[nm]['brand']] + positions_list)
            except (TypeError, KeyError):
                table.append([wb_info.supplier_name(supplier), nm,
                              card['supplierVendorCode'] + nomenclature['vendorCode'],
                              '', ''] + [''])

    return sorted(table, key=lambda item: item[2])


def _positions_by_suppliers_list(suppliers_list, start_date):
    fetched_info_dict = fetch.mpstats_info(suppliers_list=suppliers_list)
    info_dict = {supplier: {item['id']: item for item in fetched_info}
                 for supplier, fetched_info in fetched_info_dict.items()}
    cards_dict = fetch.cards(suppliers_list=suppliers_list)
    positions_dict = fetch.mpstats_positions(suppliers_list=suppliers_list, start_date=start_date)
    result_table = list()
    for supplier in suppliers_list:
        supplier_table = list()
        for card in cards_dict[supplier]:
            for nomenclature in card['nomenclatures']:
                nm = nomenclature['nmId']
                try:
                    category = info_dict[supplier][nm]['category']
                    positions_list = positions_dict[supplier][nm]['categories'][category]
                    for i in range(len(positions_list)):
                        if positions_list[i] == 'NaN': positions_list[i] = '-'
                    supplier_table.append([wb_info.supplier_name(supplier), nm,
                                           card['supplierVendorCode'] + nomenclature['vendorCode'],
                                           category, info_dict[supplier][nm]['brand']] + positions_list)
                except (TypeError, KeyError):
                    supplier_table.append([wb_info.supplier_name(supplier), nm,
                                           card['supplierVendorCode'] + nomenclature['vendorCode'],
                                           '', ''] +[''])
        result_table += sorted(supplier_table, key=lambda item: item[2])
    return result_table


def _positions_by_nm_list(nm_list, start_date):
    fetched_info_dict = fetch.mpstats_info(nm_list=nm_list)
    info_dict = {supplier: {item['id']: item for item in fetched_info}
                 for supplier, fetched_info in fetched_info_dict.items()}
    cards_dict = fetch.cards(suppliers_list=wb_info.all_suppliers())
    positions_dict = fetch.mpstats_positions(nm_list=nm_list, start_date=start_date)
    result_table = list()
    for supplier in info_dict.keys():
        supplier_table = list()
        for card in cards_dict[supplier]:
            for nomenclature in card['nomenclatures']:
                if nomenclature['nmId'] not in nm_list: continue
                else:
                    nm = nomenclature['nmId']
                    try:
                        category = info_dict[supplier][nm]['category']
                        positions_list = positions_dict[nm]['categories'][category]
                        for i in range(len(positions_list)):
                            if positions_list[i] == 'NaN': positions_list[i] = '-'
                        supplier_table.append([wb_info.supplier_name(supplier), nm,
                                               card['supplierVendorCode'] + nomenclature['vendorCode'],
                                               category, info_dict[supplier][nm]['brand']] + positions_list)
                    except (TypeError, KeyError):
                        supplier_table.append([wb_info.supplier_name(supplier), nm,
                                               card['supplierVendorCode'] + nomenclature['vendorCode'],
                                               '', ''] + [''])
        result_table += sorted(supplier_table, key=lambda item: item[2])
    return result_table


def positions(input_data, start_date):
    start_date = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд'] + \
             info.days_list(start_date, to_yesterday=True)
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _positions_by_suppliers_list(input_data, start_date)
        elif type(input_data[0]) == int: table = _positions_by_nm_list(input_data, start_date)
    elif type(input_data) == str: table = _positions_by_supplier(input_data, start_date)
    elif type(input_data) == int: table = _positions_by_nm_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _categories_by_supplier(supplier, start_date):
    days = info.days_list(start_date, to_yesterday=True)
    cards_list = fetch.cards(supplier=supplier)
    positions_dict = fetch.mpstats_positions(supplier=supplier, start_date=start_date)
    table = list()
    for card in cards_list:
        brand = ''
        for addin in card['addin']:
            if addin['type'] == 'Бренд': brand = addin['params'][0]['value']
        for nomenclature in card['nomenclatures']:
            nm = nomenclature['nmId']
            categories_by_days = list()
            try:
                for i in range(len(days)):
                    categories_raw = [values[i] for values in positions_dict[nm]['categories'].values()]
                    categories_count = len(categories_raw) - categories_raw.count('NaN')
                    categories_by_days.append(categories_count)
                table.append([wb_info.supplier_name(supplier), nm,
                              card['supplierVendorCode'] + nomenclature['vendorCode'],
                                       f"{card['parent']}/{card['object']}", brand] + categories_by_days)
            except (AttributeError, KeyError):
                table.append([wb_info.supplier_name(supplier), nm,
                              card['supplierVendorCode'] + nomenclature['vendorCode'],
                                       f"{card['parent']}/{card['object']}", brand] + ['-'] * len(days))
    return sorted(table, key=lambda item: item[2])


def _categories_by_suppliers_list(suppliers_list, start_date):
    positions_dict = fetch.mpstats_positions(suppliers_list=suppliers_list, start_date=start_date)
    days = info.days_list(start_date, to_yesterday=True)
    cards_dict = fetch.cards(suppliers_list=suppliers_list)
    result_table = list()
    for supplier, cards in cards_dict.items():
        supplier_table = list()
        for card in cards:
            brand = ''
            for addin in card['addin']:
                if addin['type'] == 'Бренд': brand = addin['params'][0]['value']
            for nomenclature in card['nomenclatures']:
                nm = nomenclature['nmId']
                categories_by_days = list()
                try:
                    for i in range(len(days)):
                        categories_raw = [values[i] for values in positions_dict[nm]['categories'].values()]
                        categories_count = len(categories_raw) - categories_raw.count('NaN')
                        categories_by_days.append(categories_count)
                    supplier_table.append([wb_info.supplier_name(supplier), nm,
                                           card['supplierVendorCode'] + nomenclature['vendorCode'],
                                           f"{card['parent']}/{card['object']}", brand] + categories_by_days)
                except (AttributeError, KeyError):
                    supplier_table.append([wb_info.supplier_name(supplier), nm,
                                           card['supplierVendorCode'] + nomenclature['vendorCode'],
                                           f"{card['parent']}/{card['object']}", brand] + ['-']*len(days))
        result_table += sorted(supplier_table, key=lambda item: item[2])
    return result_table


def _categories_by_nm_list(nm_list, start_date):
    positions_dict = fetch.mpstats_positions(nm_list=nm_list, start_date=start_date)
    days = info.days_list(start_date, to_yesterday=True)
    cards_dict = fetch.cards(suppliers_list=wb_info.all_suppliers())
    result_table = list()
    for supplier, cards in cards_dict.items():
        supplier_table = list()
        for card in cards:
            brand = ''
            for addin in card['addin']:
                if addin['type'] == 'Бренд': brand = addin['params'][0]['value']
            for nomenclature in card['nomenclatures']:
                if nomenclature['nmId'] not in nm_list: continue
                else:
                    nm = nomenclature['nmId']
                    categories_by_days = list()
                    try:
                        for i in range(len(days)):
                            categories_raw = [values[i] for values in positions_dict[nm]['categories'].values()]
                            categories_count = len(categories_raw) - categories_raw.count('NaN')
                            categories_by_days.append(categories_count)
                        supplier_table.append([wb_info.supplier_name(supplier), nm,
                                               card['supplierVendorCode'] + nomenclature['vendorCode'],
                                               f"{card['parent']}/{card['object']}", brand] + categories_by_days)
                    except (AttributeError, KeyError):
                        supplier_table.append([wb_info.supplier_name(supplier), nm,
                                               card['supplierVendorCode'] + nomenclature['vendorCode'],
                                               f"{card['parent']}/{card['object']}", brand] + ['-']*len(days))
        result_table += sorted(supplier_table, key=lambda item: item[2])
    return result_table


def categories(input_data, start_date):
    start_date = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд'] + \
             info.days_list(start_date, to_yesterday=True)
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _categories_by_suppliers_list(input_data, start_date)
        elif type(input_data[0]) == int: table = _categories_by_nm_list(input_data, start_date)
    elif type(input_data) == str: table = _categories_by_supplier(input_data, start_date)
    elif type(input_data) == int: table = _categories_by_nm_list([input_data], start_date)
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table










