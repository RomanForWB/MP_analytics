from datetime import date, timedelta, datetime

import modules.google_work as google_work
import modules.wildberries.info as wb_info
import modules.wildberries.fetch as fetch
import modules.single_requests as single_requests
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


def _orders_category_by_supplier(supplier, start_date, visible_categories=None):
    orders_list = fetch.orders(supplier=supplier, start_date=start_date)
    days = info.days_list(start_date)
    buyouts_dict = fetch.buyouts()
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
                buyouts_dict[order['nmId']].update({'category': category})
        except KeyError: pass

    for nm, values in buyouts_dict.items():
        if values.get('category') is not None:
            for buyout in values['buyouts']:
                if buyout[0] in days: categories_dict[values['category']][buyout[0]] -= buyout[1]*buyout[2]

    table = list()
    total = [0] * len(days)
    other = [0] * len(days)
    for category, days_info in categories_dict.items():
        values = [days_info[day] for day in days]
        if visible_categories is not None:
            if category in visible_categories: table.append([category] + values)
            else: other = [other[i]+values[i] for i in range(len(values))]
        else: table.append([category] + values)
        total = [total[i]+values[i] for i in range(len(values))]

    table.sort(key=lambda item: sum(item[1:]), reverse=True)
    if visible_categories is not None: table += [["Остальное"] + other, ["Итого"] + total]
    else: table += [["Итого"] + total]
    return table


def _orders_category_by_suppliers_list(suppliers_list, start_date, visible_categories=None):
    orders_dict = fetch.orders(suppliers_list=suppliers_list, start_date=start_date)
    days = info.days_list(start_date)
    buyouts_dict = fetch.buyouts()
    categories_dict = dict()
    for supplier, orders_list in orders_dict.items():
        for order in orders_list:
            if order['category'] == 'Обувь': category = 'Обувь'
            elif 'жилет' in order['subject'].lower(): category = 'Жилеты'
            else: category = order['subject']
            if category not in categories_dict.keys():
                categories_dict[category] = {day: 0 for day in days}
            try:
                day = datetime.strptime(order['date'], '%Y-%m-%dT%H:%M:%S').date().strftime('%d.%m')
                final_price = order['totalPrice'] * (100 - order['discountPercent']) / 100
                categories_dict[category][day] += final_price
                if buyouts_dict.get(order['nmId']) is not None:
                    buyouts_dict[order['nmId']].update({'category': category})
            except KeyError: pass

    for nm, values in buyouts_dict.items():
        if values.get('category') is not None:
            for buyout in values['buyouts']:
                if buyout[0] in days: categories_dict[values['category']][buyout[0]] -= buyout[1]*buyout[2]

    table = list()
    total = [0]*len(days)
    other = [0]*len(days)
    for category, days_info in categories_dict.items():
        values = [days_info[day] for day in days]
        if visible_categories is not None:
            if category in visible_categories: table.append([category] + values)
            else: other = [other[i]+values[i] for i in range(len(values))]
        else: table.append([category] + values)
        total = [total[i] + values[i] for i in range(len(values))]

    table.sort(key=lambda item: sum(item[1:]), reverse=True)
    if visible_categories is not None: table += [["Остальное"] + other, ["Итого"] + total]
    else: table += [["Итого"] + total]
    return table


def _orders_category_by_nm_list(nm_list, start_date, visible_categories=None):
    orders_dict = fetch.orders(suppliers_list=wb_info.all_suppliers(), start_date=start_date)
    days = info.days_list(start_date)
    buyouts_dict = fetch.buyouts()
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
                    buyouts_dict[order['nmId']].update({'category': category})
            except KeyError: pass

    for nm, values in buyouts_dict.items():
        if values.get('category') is not None:
            for buyout in values['buyouts']:
                if buyout[0] in days: categories_dict[values['category']][buyout[0]] -= buyout[1]*buyout[2]

    table = list()
    total = [0 for day in days]
    other = [0 for day in days]
    for category, days_info in categories_dict.items():
        values = [days_info[day] for day in days]
        if visible_categories is not None:
            if category in visible_categories: table.append([category] + values)
            else: other = [other[i]+values[i] for i in range(len(values))]
        else: table.append([category] + values)
        total = [total[i]+values[i] for i in range(len(values))]

    table.sort(key=lambda item: sum(item[1:]), reverse=True)
    if visible_categories is not None: table += [["Остальное"] + other, ["Итого"] + total]
    else: table += [["Итого"] + total]
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
    for supplier, analytic_report in report_dict.items():
        for year_values in analytic_report['consolidatedYears']:
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
    table = list()
    for day in info.dates_list(from_date=start_date, to_yesterday=True):
        try: row = [day,
              days_dict[day]['ordered'], days_dict[day]['goodsOrdered'],
              days_dict[day]['paymentSalesRub'], days_dict[day]['paymentSalesPiece'],
              days_dict[day]['logisticsCost'], days_dict[day]['totalToTransfer']]
        except KeyError: row = [day,0,0,0,0,0,0]
        table.append(row)
    # table = [[day,
    #           days_dict[day]['ordered'], days_dict[day]['goodsOrdered'],
    #           days_dict[day]['paymentSalesRub'], days_dict[day]['paymentSalesPiece'],
    #           days_dict[day]['logisticsCost'], days_dict[day]['totalToTransfer']]
    #          for day in info.dates_list(from_date=start_date, to_yesterday=True)]
    return table


def report(input_data, start_date=str(date.today()-timedelta(days=7))):
    header = ['Дата', 'Заказано руб.', 'Заказано шт.', 'Выкупили руб.', 'Выкупили шт.', 'Логистика руб.', 'К перечислению']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _report_by_suppliers_list(input_data, start_date)
        #elif type(input_data[0]) == int: table = _report_by_nm_list(input_data, start_date)
    elif type(input_data) == str: table = _report_by_supplier(input_data, start_date)
    #elif type(input_data) == int: table = _report_by_nm_list([input_data], start_date)
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
        #elif type(input_data[0]) == int: table = _shipments_by_nm_list(input_data)
    elif type(input_data) == str: table = _shipments_by_supplier(input_data)
    #elif type(input_data) == int: table = _shipments_by_nm_list([input_data])
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


# ================= for positions =================
main_category_exceptions = {'Жилеты': 'Женщинам/Пиджаки, жилеты и жакеты/Жилеты'}
main_categories = ['Женщинам/Одежда/', 'Мужчинам/Одежда/', 'Обувь/Женская/', 'Обувь/Мужская/']


def _positions_by_supplier(supplier, start_date):
    info_dict = {item['id']: item for item in fetch.mpstats_info(supplier=supplier)}
    cards_list = fetch.cards(supplier=supplier)
    positions_dict = fetch.mpstats_positions(supplier=supplier, start_date=start_date)
    table = list()
    for card in cards_list:
        for nomenclature in card['nomenclatures']:
            nm = nomenclature['nmId']
            if type(positions_dict[nm]['categories']) == list:
                table.append([wb_info.supplier_name(supplier), nm,
                                       card['supplierVendorCode'] + nomenclature['vendorCode'], '-', '-'])
                continue
            try:
                # ==================================
                if card['object'] in main_category_exceptions.keys(): main_category = main_category_exceptions[card['object']]
                else:
                    main_category_lenght = 0
                    main_category = None
                    for category in positions_dict[nm]['categories'].keys():
                        for start_category in main_categories:
                            if category.startswith(start_category) and len(category) > main_category_lenght:
                                main_category_lenght = len(category)
                                main_category = category
                    if main_category is None: main_category = info_dict[nm]['category']
                # ==================================
                positions_list = positions_dict[nm]['categories'][main_category]
                for i in range(len(positions_list)):
                    if positions_list[i] == 'NaN': positions_list[i] = '-'
                table.append([wb_info.supplier_name(supplier), nm,
                              card['supplierVendorCode'] + nomenclature['vendorCode'],
                              main_category, info_dict[nm]['brand']] + positions_list)
            except (TypeError, KeyError):
                table.append([wb_info.supplier_name(supplier), nm,
                              card['supplierVendorCode'] + nomenclature['vendorCode'], '-', '-'])

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
                if type(positions_dict[nm]['categories']) == list:
                    supplier_table.append([wb_info.supplier_name(supplier), nm,
                                           card['supplierVendorCode'] + nomenclature['vendorCode'], '-', '-'])
                    continue
                try:
                    # ==================================
                    if card['object'] in main_category_exceptions.keys(): main_category = main_category_exceptions[card['object']]
                    else:
                        main_category_lenght = 0
                        main_category = None
                        for category in positions_dict[nm]['categories'].keys():
                            for start_category in main_categories:
                                if category.startswith(start_category) and len(category) > main_category_lenght:
                                    main_category_lenght = len(category)
                                    main_category = category
                        if main_category is None: main_category = info_dict[nm]['category']
                    # ==================================
                    positions_list = positions_dict[supplier][nm]['categories'][main_category]
                    for i in range(len(positions_list)):
                        if positions_list[i] == 'NaN': positions_list[i] = '-'
                    supplier_table.append([wb_info.supplier_name(supplier), nm,
                                           card['supplierVendorCode'] + nomenclature['vendorCode'],
                                           main_category, info_dict[supplier][nm]['brand']] + positions_list)
                except (TypeError, KeyError):
                    supplier_table.append([wb_info.supplier_name(supplier), nm,
                                           card['supplierVendorCode'] + nomenclature['vendorCode'], '-', '-'])
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
                    if type(positions_dict[nm]['categories']) == list:
                        supplier_table.append([wb_info.supplier_name(supplier), nm,
                                               card['supplierVendorCode'] + nomenclature['vendorCode'], '-', '-'])
                        continue
                    try:
                        # ==================================
                        if card['object'] in main_category_exceptions.keys():
                            main_category = main_category_exceptions[card['object']]
                        else:
                            main_category_lenght = 0
                            main_category = None
                            for category in positions_dict[nm]['categories'].keys():
                                for start_category in main_categories:
                                    if category.startswith(start_category) and len(category) > main_category_lenght:
                                        main_category_lenght = len(category)
                                        main_category = category
                            if main_category is None: main_category = info_dict[nm]['category']
                        # ==================================
                        positions_list = positions_dict[nm]['categories'][main_category]
                        for i in range(len(positions_list)):
                            if positions_list[i] == 'NaN': positions_list[i] = '-'
                        supplier_table.append([wb_info.supplier_name(supplier), nm,
                                               card['supplierVendorCode'] + nomenclature['vendorCode'],
                                               main_category, info_dict[supplier][nm]['brand']] + positions_list)
                    except (TypeError, KeyError):
                        supplier_table.append([wb_info.supplier_name(supplier), nm,
                                               card['supplierVendorCode'] + nomenclature['vendorCode'], '-', '-'])
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


def max_categories(start_date):
    days = info.days_list(start_date, to_yesterday=True)
    table = [['Основная категория'] + days + ['Все возможные категории']]
    top_dict = fetch.top_nms()
    nm_list = [nm for category, sub_categories in top_dict.items()
                  for sub_category, nms in sub_categories.items()
                  for nm in nms]
    positions_dict = fetch.mpstats_positions(nm_list=nm_list, start_date=start_date)
    for category, sub_categories in top_dict.items():
        for sub_category, nms in sub_categories.items():
            max_categories_by_days = {day: 0 for day in days}
            categories_set = set()
            for nm in nms:
                categories_by_days = {day: 0 for day in days}
                try:
                    categories_set.update(positions_dict[nm]['categories'].keys())
                    for i in range(len(days)):
                        categories_raw = [values[i] for values in positions_dict[nm]['categories'].values()]
                        categories_count = len(categories_raw) - categories_raw.count('NaN')
                        categories_by_days[days[i]] = categories_count
                except (AttributeError, KeyError): pass
                for day in days:
                    if max_categories_by_days[day] < categories_by_days[day]:
                        max_categories_by_days[day] = categories_by_days[day]
            table.append([f'{category}/{sub_category}'] +
                         [max_categories_by_days[day] for day in days] +
                         ['\n'.join(sorted(list(categories_set)))])
    return table


def categories_revenue(categories_list, start_date=str(date.today()-timedelta(days=6)),
                       end_date=str(date.today())):
    start_date = str((datetime.strptime(start_date, '%Y-%m-%d')-timedelta(days=1)).date())
    end_date = str((datetime.strptime(end_date, '%Y-%m-%d')-timedelta(days=1)).date())
    categories_info_dict = fetch.mpstats_categories_info(categories_list, start_date, end_date)
    dates_list = info.dates_list(from_date=start_date, to_date=end_date)
    dates_list.reverse()
    table = [['Дата']]
    for day in dates_list: table[0] += ['', datetime.strptime(day, '%Y-%m-%d').strftime('%d.%m'), '']
    table.append(['Категории'])
    for day in dates_list: table[1] += ['Выручка руб.', 'Продажи шт.', 'Средняя цена руб.']
    for category, day_values in categories_info_dict.items():
        row = [category]
        for day in dates_list:
            try: row += [day_values[day]['revenue'], day_values[day]['sales'], day_values[day]['avg_sale_price']]
            except KeyError: row += ['','','']
        table.append(row)
    return table


def trends(start_date=str(date.today()-timedelta(days=6)), end_date=str(date.today())):
    start_date = str((datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=1)).date())
    end_date = str((datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=1)).date())
    orders_dict = fetch.orders(suppliers_list=wb_info.all_suppliers(), start_date=start_date)
    days = info.days_list(from_date=start_date, to_date=end_date)
    dates_list = info.dates_list(from_date=start_date, to_date=end_date)
    buyouts_dict = fetch.buyouts()
    categories_dict = dict()
    for supplier, orders_list in orders_dict.items():
        for order in orders_list:
            category = order['subject']
            categories_dict.setdefault(category, {day: 0 for day in days})
            try:
                day = datetime.strptime(order['date'], '%Y-%m-%dT%H:%M:%S').strftime('%d.%m')
                final_price = order['totalPrice'] * (100 - order['discountPercent']) / 100
                categories_dict[category][day] += final_price
                if buyouts_dict.get(order['nmId']) is not None:
                    buyouts_dict[order['nmId']].update({'category': category})
            except KeyError: pass

    for nm, values in buyouts_dict.items():
        if values.get('category') is not None:
            for buyout in values['buyouts']:
                if buyout[0] in days: categories_dict[values['category']][buyout[0]] -= buyout[1] * buyout[2]

    category_convert_dict = {'Женщинам/Одежда/Верхняя одежда/Куртка': 'Куртки',
                             'Женщинам/Одежда/Блузки и рубашки/Блузка': 'Блузки',
                             'Женщинам/Джемперы, водолазки и кардиганы/Водолазка': 'Водолазки',
                             'Обувь/Женская/Кеды и кроссовки/Кроссовки': 'Кроссовки',
                             'Спорт/Туризм/Походы/Одежда/Жилет спортивный': 'Жилеты спортивные',
                             'Женщинам/Пиджаки, жилеты и жакеты/Жилет': 'Жилеты',
                             'Женщинам/Одежда/Верхняя одежда/Плащ': 'Плащи',
                             'Женщинам/Одежда/Юбки': 'Юбки',
                             'Женщинам/Одежда/Костюмы/Костюм спортивный': 'Костюмы спортивные',
                             'Женщинам/Одежда/Блузки и рубашки/Рубашка': 'Рубашки',
                             'Женщинам/Джемперы, водолазки и кардиганы/Свитер': 'Свитеры',
                             'Женщинам/Верхняя одежда/Тренчкот': 'Тренчкоты',
                             'Женщинам/Брюки/Брюки': 'Брюки',
                             'Женщинам/Верхняя одежда/Пуховик': 'Пуховики',
                             'Женщинам/Верхняя одежда/Косуха': 'Косухи',
                             'Женщинам/Одежда/Платья и сарафаны/Платье': 'Платья',
                             'Женщинам/Верхняя одежда/Дубленка': 'Дубленки',
                             'Женщинам/Одежда/Пиджаки и жакеты/Пиджак': 'Пиджаки',
                             'Женщинам/Джинсы/Джинсы': 'Джинсы',
                             'Женщинам/Верхняя одежда/Пальто': 'Пальто',
                             'Аксессуары/Сумки и рюкзаки/Сумки': 'Сумки',
                             'Женщинам/Одежда/Лонгсливы': 'Лонгсливы',
                             'Женщинам/Одежда/Шорты/Шорты': 'Шорты',
                             'Женщинам/Толстовки, свитшоты и худи/Худи': 'Худи',
                             'Женщинам/Верхняя одежда/Полупальто': 'Полупальто',
                             'Женщинам/Одежда/Костюмы/Костюм': 'Костюмы',
                             'Женщинам/Брюки/Велосипедки': 'Велосипедки',
                             'Женщинам/Верхняя одежда/Ветровка': 'Ветровки',
                             'Женщинам/Одежда/Футболки и топы/Топ': 'Топы'}
    categories_info_dict = fetch.mpstats_categories_info(list(category_convert_dict.keys()), start_date, end_date)
    category_rows = list()
    for mp_category, wb_category in category_convert_dict.items():
        category_row = [wb_category]
        trand_row = ['Тренд']
        our_dynamic_row = ['Динамика наша']
        market_dynamic_row = ['Динамика рынка']
        for i in range(len(days)):
            category_row.append(categories_dict[wb_category][days[i]])
            trand_row.append(categories_info_dict[mp_category][dates_list[i]]['revenue'])
            if i == 0:
                our_dynamic_row.append('')
                market_dynamic_row.append('')
            else:
                try: our_dynamic_row.append(categories_dict[wb_category][days[i]] /
                                           categories_dict[wb_category][days[i - 1]] - 1)
                except (ZeroDivisionError): our_dynamic_row.append(0)
                try: market_dynamic_row.append(categories_info_dict[mp_category][dates_list[i]]['revenue'] /
                                              categories_info_dict[mp_category][dates_list[i - 1]]['revenue'] - 1)
                except (ZeroDivisionError): market_dynamic_row.append(0)
        category_row.append(sum(category_row[1:]))
        trand_row.append(sum(trand_row[1:]))
        try: our_dynamic_row.append(category_row[-2]/category_row[1] - 1)
        except ZeroDivisionError: our_dynamic_row.append(0)
        try: market_dynamic_row.append(trand_row[-2]/trand_row[1] - 1)
        except ZeroDivisionError: market_dynamic_row.append(0)
        category_rows.append([category_row, trand_row, our_dynamic_row, market_dynamic_row])
    table = [['Категории'] + days + ['Итог 7 дней']]
    category_rows.sort(key=lambda item: sum(item[0][1:-1]), reverse=True)
    for rows in category_rows:
        for row in rows: table.append(row)
    return table


def _buyout_percent_size_by_supplier(supplier, weeks):
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


def _buyout_percent_size_by_suppliers_list(suppliers_list, weeks):
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


def buyout_percent_size(input_data, weeks=4):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд',
              'Размер', 'Чистые продажи', 'Продажи', 'Возвраты', 'Отказы', 'Процент выкупа', 'Последнее обновление']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _buyout_percent_size_by_suppliers_list(input_data, weeks)
        #elif type(input_data[0]) == int: table = _buyout_percent_by_nm_list(input_data)
    elif type(input_data) == str: table = _buyout_percent_size_by_supplier(input_data, weeks)
    #elif type(input_data) == int: table = _buyout_percent_by_nm_list([input_data])
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _buyout_percent_color_by_supplier(supplier, weeks):
    report_list = fetch.detail_report(supplier=supplier, weeks=weeks)
    items_dict = dict()
    last_date = ''
    for sale in report_list:
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
    days = info.days_list(to_date=last_date.split('T')[0],
           from_date=str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=27)).date()))
    buyouts_dict = dict()
    for nm, values in fetch.buyouts().items():
        buyouts_dict[nm] = {'buyouts_count': 0, 'buyouts_value': 0}
        for buyout in values['buyouts']:
            if buyout[0] in days:
                buyouts_dict[nm]['buyouts_count'] += buyout[1]
                buyouts_dict[nm]['buyouts_value'] += buyout[1] * buyout[2]
    for sale in report_list:
        dict_key = (wb_info.supplier_name(supplier), sale['nm_id'],
                    sale['sa_name'], sale['subject_name'], sale['brand_name'])
        items_dict.setdefault(dict_key, {'pure': 0, 'sales': 0, 'returns': 0, 'cancel': 0, 'update': ''})
        if buyouts_dict.get(sale['nm_id']) is not None:
            items_dict[dict_key]['sales'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
            items_dict[dict_key]['pure'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
            buyouts_dict.pop(sale['nm_id'])
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


def _buyout_percent_color_by_suppliers_list(suppliers_list, weeks):
    report_dict = fetch.detail_report(suppliers_list=suppliers_list, weeks=weeks)
    table = list()
    last_date = ''
    for supplier, report_list in report_dict.items():
        for sale in report_list:
            if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
        days = info.days_list(to_date=last_date.split('T')[0],
            from_date=str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=27)).date()))
        buyouts_dict = dict()
        for nm, values in fetch.buyouts().items():
            buyouts_dict[nm] = {'buyouts_count': 0, 'buyouts_value': 0}
            for buyout in values['buyouts']:
                if buyout[0] in days:
                    buyouts_dict[nm]['buyouts_count'] += buyout[1]
                    buyouts_dict[nm]['buyouts_value'] += buyout[1] * buyout[2]
        items_dict = dict()
        for sale in report_list:
            dict_key = (wb_info.supplier_name(supplier), sale['nm_id'],
                        sale['sa_name'], sale['subject_name'], sale['brand_name'])
            items_dict.setdefault(dict_key, {'pure': 0, 'sales': 0, 'returns': 0, 'cancel': 0, 'update': ''})
            if buyouts_dict.get(sale['nm_id']) is not None:
                items_dict[dict_key]['sales'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
                items_dict[dict_key]['pure'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
                buyouts_dict.pop(sale['nm_id'])
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


def buyout_percent_color(input_data, weeks=4):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд',
              'Чистые продажи', 'Продажи', 'Возвраты', 'Отказы', 'Процент выкупа', 'Последнее обновление']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _buyout_percent_color_by_suppliers_list(input_data, weeks)
        #elif type(input_data[0]) == int: table = _buyout_percent_by_nm_list(input_data)
    elif type(input_data) == str: table = _buyout_percent_color_by_supplier(input_data, weeks)
    #elif type(input_data) == int: table = _buyout_percent_by_nm_list([input_data])
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _buyout_percent_article_by_supplier(supplier, weeks):
    report_list = fetch.detail_report(supplier=supplier, weeks=weeks)
    items_dict = dict()
    last_date = ''
    for sale in report_list:
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
    days = info.days_list(to_date=last_date.split('T')[0],
                          from_date=str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=27)).date()))
    buyouts_dict = dict()
    for nm, values in fetch.buyouts().items():
        buyouts_dict[nm] = {'buyouts_count': 0, 'buyouts_value': 0}
        for buyout in values['buyouts']:
            if buyout[0] in days:
                buyouts_dict[nm]['buyouts_count'] += buyout[1]
                buyouts_dict[nm]['buyouts_value'] += buyout[1] * buyout[2]
    for sale in report_list:
        dict_key = (wb_info.supplier_name(supplier),
                    sale['sa_name'].split('/')[0]+'/',
                    sale['subject_name'], sale['brand_name'])
        items_dict.setdefault(dict_key, {'pure': 0, 'sales': 0, 'returns': 0, 'cancel': 0, 'update': ''})
        if buyouts_dict.get(sale['nm_id']) is not None:
            items_dict[dict_key]['sales'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
            items_dict[dict_key]['pure'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
            buyouts_dict.pop(sale['nm_id'])
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
    return sorted(table, key=lambda item: item[1])


def _buyout_percent_article_by_suppliers_list(suppliers_list, weeks):
    report_dict = fetch.detail_report(suppliers_list=suppliers_list, weeks=weeks)
    table = list()
    last_date = ''
    for supplier, report_list in report_dict.items():
        for sale in report_list:
            if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
        days = info.days_list(to_date=last_date.split('T')[0],
            from_date=str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=27)).date()))
        items_dict = dict()
        buyouts_dict = dict()
        for nm, values in fetch.buyouts().items():
            buyouts_dict[nm] = {'buyouts_count': 0, 'buyouts_value': 0}
            for buyout in values['buyouts']:
                if buyout[0] in days:
                    buyouts_dict[nm]['buyouts_count'] += buyout[1]
                    buyouts_dict[nm]['buyouts_value'] += buyout[1] * buyout[2]
        for sale in report_list:
            dict_key = (wb_info.supplier_name(supplier),
                        sale['sa_name'].split('/')[0]+'/',
                        sale['subject_name'], sale['brand_name'])
            items_dict.setdefault(dict_key, {'pure': 0, 'sales': 0, 'returns': 0, 'cancel': 0, 'update': ''})
            if buyouts_dict.get(sale['nm_id']) is not None:
                items_dict[dict_key]['sales'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
                items_dict[dict_key]['pure'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
                buyouts_dict.pop(sale['nm_id'])
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
        table += sorted(supplier_table, key=lambda item: item[1])
    return table


def buyout_percent_article(input_data, weeks=4):
    header = ['Организация', 'Артикул поставщика', 'Предмет', 'Бренд',
              'Чистые продажи', 'Продажи', 'Возвраты', 'Отказы', 'Процент выкупа', 'Последнее обновление']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _buyout_percent_article_by_suppliers_list(input_data, weeks)
        #elif type(input_data[0]) == int: table = _buyout_percent_by_nm_list(input_data)
    elif type(input_data) == str: table = _buyout_percent_article_by_supplier(input_data, weeks)
    #elif type(input_data) == int: table = _buyout_percent_by_nm_list([input_data])
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _buyout_percent_category_by_supplier(supplier, weeks):
    report_list = fetch.detail_report(supplier=supplier, weeks=weeks)
    items_dict = dict()
    last_date = ''
    for sale in report_list:
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
    days = info.days_list(to_date=last_date.split('T')[0],
        from_date=str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=27)).date()))
    buyouts_dict = dict()
    for nm, values in fetch.buyouts().items():
        buyouts_dict[nm] = {'buyouts_count': 0, 'buyouts_value': 0}
        for buyout in values['buyouts']:
            if buyout[0] in days:
                buyouts_dict[nm]['buyouts_count'] += buyout[1]
                buyouts_dict[nm]['buyouts_value'] += buyout[1] * buyout[2]
    for sale in report_list:
        dict_key = tuple([sale['subject_name']])
        items_dict.setdefault(dict_key, {'pure': 0, 'sales': 0, 'returns': 0, 'cancel': 0, 'update': ''})
        if buyouts_dict.get(sale['nm_id']) is not None:
            items_dict[dict_key]['sales'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
            items_dict[dict_key]['pure'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
            buyouts_dict.pop(sale['nm_id'])
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
    return sorted(table, key=lambda item: item[1], reverse=True)


def _buyout_percent_category_by_suppliers_list(suppliers_list, weeks):
    report_dict = fetch.detail_report(suppliers_list=suppliers_list, weeks=weeks)
    last_date = ''
    items_dict = dict()
    for supplier, report_list in report_dict.items():
        for sale in report_list:
            if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
        days = info.days_list(to_date=last_date.split('T')[0],
            from_date=str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=27)).date()))
        buyouts_dict = dict()
        for nm, values in fetch.buyouts().items():
            buyouts_dict[nm] = {'buyouts_count': 0, 'buyouts_value': 0}
            for buyout in values['buyouts']:
                if buyout[0] in days:
                    buyouts_dict[nm]['buyouts_count'] += buyout[1]
                    buyouts_dict[nm]['buyouts_value'] += buyout[1] * buyout[2]
        for sale in report_list:
            dict_key = tuple([sale['subject_name']])
            items_dict.setdefault(dict_key, {'pure': 0, 'sales': 0, 'returns': 0, 'cancel': 0, 'update': ''})
            if buyouts_dict.get(sale['nm_id']) is not None:
                items_dict[dict_key]['sales'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
                items_dict[dict_key]['pure'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
                buyouts_dict.pop(sale['nm_id'])
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
        else: table.append(list(key)+[value['pure'], value['sales'],
                                 value['returns'], value['cancel'],
                                 value['pure']/(value['sales']+value['cancel']),
                                 value['update']])
    return sorted(table, key=lambda item: item[1], reverse=True)


def buyout_percent_category(input_data, weeks=4):
    header = ['Категория', 'Чистые продажи', 'Продажи', 'Возвраты', 'Отказы', 'Процент выкупа', 'Последнее обновление']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _buyout_percent_category_by_suppliers_list(input_data, weeks)
        #elif type(input_data[0]) == int: table = _buyout_percent_by_nm_list(input_data)
    elif type(input_data) == str: table = _buyout_percent_category_by_supplier(input_data, weeks)
    #elif type(input_data) == int: table = _buyout_percent_by_nm_list([input_data])
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _profit_by_supplier(supplier, weeks):
    report_list = fetch.detail_report(supplier=supplier, weeks=weeks)
    analytic_report = fetch.report(supplier=supplier)
    items_dict = dict()
    last_date = ''

    for sale in report_list:
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
    days = info.days_list(to_date=last_date.split('T')[0],
           from_date=str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=6)).date()))

    for sale in report_list:
        if datetime.strptime(sale['rr_dt'], '%Y-%m-%dT00:00:00Z').strftime('%d.%m') not in days: continue
        dict_key = (wb_info.supplier_name(supplier), sale['nm_id'],
                    sale['sa_name'], sale['subject_name'], sale['brand_name'], sale['ts_name'])
        items_dict.setdefault(dict_key, {'sales_value': 0, 'sales_count': 0, 'delivery_value': 0,
                                         'return_value': 0, 'update': ''})
        if sale['doc_type_name'] == 'Продажа' and sale['quantity'] == 1:
            items_dict[dict_key]['sales_value'] += sale['ppvz_for_pay']
            items_dict[dict_key]['sales_count'] += 1
        elif sale['doc_type_name'] == 'Возврат' and sale['quantity'] == 1:
            items_dict[dict_key]['sales_value'] -= sale['ppvz_for_pay']
            items_dict[dict_key]['sales_count'] -= 1
            items_dict[dict_key]['return_value'] += sale['ppvz_reward']
        elif sale['delivery_rub'] != 0:
            items_dict[dict_key]['delivery_value'] += sale['delivery_rub']
        if sale['rr_dt'] > items_dict[dict_key]['update']:
            items_dict[dict_key]['update'] = sale['rr_dt']
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']

    storage_value = 0
    for year_values in analytic_report['consolidatedYears']:
        for month_values in year_values['consolidatedMonths']:
            for day_values in month_values['consolidatedDays']:
                day = day_values['day'].split('.')[0]
                month = month_values['month']
                if f'{day}.{month}' in days: storage_value += day_values['storageCost']
    sales_count = sum([value['sales_count'] for key, value in items_dict.items()])
    if sales_count == 0: storage_value_by_item = 0
    else: storage_value_by_item = storage_value/sales_count

    cost_dict = fetch.cost()
    for key, value in items_dict.items():
        if cost_dict['nm'].get(key[1]) is not None:
            cost = cost_dict['nm'][key[1]]
        elif cost_dict['article'].get(key[2].split('/')[0]+'/') is not None:
            cost = cost_dict['article'][key[2].split('/')[0]+'/']
        else: cost = 0
        items_dict[key].update({'cost': cost,
                                'cost_value': cost*value['sales_count'],
                                'storage_value': storage_value_by_item*value['sales_count']})

    table = sorted([list(key) + [value['sales_value'], value['sales_count'],
                                   value['delivery_value'], value['return_value'],
                                   value['storage_value'], value['cost'],
                                   value['sales_value'] - value['delivery_value'] -
                                   value['return_value'] - value['storage_value'] - value['cost_value'],
                                   value['update']]
                   for key, value in items_dict.items()],
                   key=lambda item: item[2])
    return table


def _profit_by_suppliers_list(suppliers_list, weeks):
    report_dict = fetch.detail_report(suppliers_list=suppliers_list, weeks=weeks)
    analytic_report_dict = fetch.report(suppliers_list=suppliers_list)
    last_date = ''
    table = list()
    for supplier, report_list in report_dict.items():
        items_dict = dict()
        for sale in report_list:
            if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
        days = info.days_list(to_date=last_date.split('T')[0],
            from_date=str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=6)).date()))
        for sale in report_list:
            if datetime.strptime(sale['rr_dt'], '%Y-%m-%dT00:00:00Z').strftime('%d.%m') not in days: continue
            dict_key = (wb_info.supplier_name(supplier), sale['nm_id'],
                        sale['sa_name'], sale['subject_name'], sale['brand_name'], sale['ts_name'])
            items_dict.setdefault(dict_key, {'sales_value': 0, 'sales_count': 0, 'delivery_value': 0,
                                             'return_value': 0, 'update': ''})
            if sale['doc_type_name'] == 'Продажа' and sale['quantity'] == 1:
                items_dict[dict_key]['sales_value'] += sale['ppvz_for_pay']
                items_dict[dict_key]['sales_count'] += 1
            elif sale['doc_type_name'] == 'Возврат' and sale['quantity'] == 1:
                items_dict[dict_key]['sales_value'] -= sale['ppvz_for_pay']
                items_dict[dict_key]['sales_count'] -= 1
                items_dict[dict_key]['return_value'] += sale['ppvz_reward']
            elif sale['delivery_rub'] != 0:
                items_dict[dict_key]['delivery_value'] += sale['delivery_rub']
            if sale['rr_dt'] > items_dict[dict_key]['update']:
                items_dict[dict_key]['update'] = sale['rr_dt']
            if sale['rr_dt'] > last_date: last_date = sale['rr_dt']

        analytic_report = analytic_report_dict[supplier]
        storage_value = 0
        for year_values in analytic_report['consolidatedYears']:
            for month_values in year_values['consolidatedMonths']:
                for day_values in month_values['consolidatedDays']:
                    day = day_values['day'].split('.')[0]
                    month = month_values['month']
                    if f'{day}.{month}' in days: storage_value += day_values['storageCost']
        sales_count = sum([value['sales_count'] for key, value in items_dict.items()])
        if sales_count == 0: storage_value_by_item = 0
        else: storage_value_by_item = storage_value/sales_count

        cost_dict = fetch.cost()
        for key, value in items_dict.items():
            if cost_dict['nm'].get(key[1]) is not None:
                cost = cost_dict['nm'][key[1]]
            elif cost_dict['article'].get(key[2].split('/')[0]+'/') is not None:
                cost = cost_dict['article'][key[2].split('/')[0]+'/']
            else: cost = 0
            items_dict[key].update({'cost': cost,
                                    'cost_value': cost*value['sales_count'],
                                    'storage_value': storage_value_by_item*value['sales_count']})

        supplier_table = [list(key) + [value['sales_value'], value['sales_count'],
                                      value['delivery_value'], value['return_value'],
                                      value['storage_value'], value['cost'],
                                      value['sales_value']-value['delivery_value']-
                                      value['return_value']-value['storage_value']- value['cost_value'],
                                      value['update']]
                          for key, value in items_dict.items()]
        table += sorted(supplier_table, key=lambda item: item[2])
    return table


def profit(input_data, weeks=4):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд',
              'Размер', 'Продажи, руб', 'Продажи, шт', 'Логистика', 'Возвраты, руб',
              'Хранение, руб', 'Закуп', 'Операционная прибыль', 'Время обновления']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _profit_by_suppliers_list(input_data, weeks)
        #elif type(input_data[0]) == int: table = _profit_by_nm_list(input_data)
    elif type(input_data) == str: table = _profit_by_supplier(input_data, weeks)
    #elif type(input_data) == int: table = _profit_by_nm_list([input_data])
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _profit_size_by_supplier(supplier, weeks):
    report_list = fetch.detail_report(supplier=supplier, weeks=weeks)
    analytic_report = fetch.report(supplier=supplier)
    cost_dict = fetch.cost()
    items_dict = dict()
    last_date = ''

    for sale in report_list:
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
    days = info.days_list(to_date=last_date.split('T')[0],
           from_date=str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=6)).date()))

    for sale in report_list:
        if datetime.strptime(sale['rr_dt'], '%Y-%m-%dT00:00:00Z').strftime('%d.%m') not in days: continue
        dict_key = (wb_info.supplier_name(supplier), sale['nm_id'],
                    sale['sa_name'], sale['subject_name'], sale['brand_name'], sale['ts_name'])
        items_dict.setdefault(dict_key, {'sales_value': 0, 'sales_count': 0, 'delivery_value': 0,
                                         'return_value': 0, 'update': ''})
        if sale['doc_type_name'] == 'Продажа' and sale['quantity'] == 1:
            items_dict[dict_key]['sales_value'] += sale['ppvz_for_pay']
            items_dict[dict_key]['sales_count'] += 1
        elif sale['doc_type_name'] == 'Возврат' and sale['quantity'] == 1:
            items_dict[dict_key]['sales_value'] -= sale['ppvz_for_pay']
            items_dict[dict_key]['sales_count'] -= 1
            items_dict[dict_key]['return_value'] += sale['ppvz_reward']
        elif sale['delivery_rub'] != 0:
            items_dict[dict_key]['delivery_value'] += sale['delivery_rub']
        if sale['rr_dt'] > items_dict[dict_key]['update']:
            items_dict[dict_key]['update'] = sale['rr_dt']
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']

    storage_value = 0
    for year_values in analytic_report['consolidatedYears']:
        for month_values in year_values['consolidatedMonths']:
            for day_values in month_values['consolidatedDays']:
                day = day_values['day'].split('.')[0]
                month = month_values['month']
                if f'{day}.{month}' in days: storage_value += day_values['storageCost']
    sales_count = sum([value['sales_count'] for key, value in items_dict.items()])
    if sales_count == 0: storage_value_by_item = 0
    else: storage_value_by_item = storage_value/sales_count

    for key, value in items_dict.items():
        if cost_dict['nm'].get(key[1]) is not None:
            cost = cost_dict['nm'][key[1]]
        elif cost_dict['article'].get(key[2].split('/')[0]+'/') is not None:
            cost = cost_dict['article'][key[2].split('/')[0]+'/']
        else: cost = 0
        oper_profit = value['sales_value'] - value['delivery_value'] - \
                      value['return_value'] - storage_value_by_item*value['sales_count'] - \
                      cost*value['sales_count']
        if value['sales_count'] == 0: oper_profit_by_item = 0
        else: oper_profit_by_item = oper_profit/value['sales_count']
        items_dict[key].update({'profit_value': oper_profit,
                                'profit_value_by_item': oper_profit_by_item})

    table = sorted([list(key) + [value['sales_count'], value['profit_value'], value['profit_value_by_item']]
                   for key, value in items_dict.items()],
                   key=lambda item: item[2])
    return table


def _profit_size_by_suppliers_list(suppliers_list, weeks):
    report_dict = fetch.detail_report(suppliers_list=suppliers_list, weeks=weeks)
    analytic_report_dict = fetch.report(suppliers_list=suppliers_list)
    cost_dict = fetch.cost()
    last_date = ''
    table = list()
    for supplier, report_list in report_dict.items():
        items_dict = dict()
        for sale in report_list:
            if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
        days = info.days_list(to_date=last_date.split('T')[0],
            from_date=str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=6)).date()))
        for sale in report_list:
            if datetime.strptime(sale['rr_dt'], '%Y-%m-%dT00:00:00Z').strftime('%d.%m') not in days: continue
            dict_key = (wb_info.supplier_name(supplier), sale['nm_id'],
                        sale['sa_name'], sale['subject_name'], sale['brand_name'], sale['ts_name'])
            items_dict.setdefault(dict_key, {'sales_value': 0, 'sales_count': 0, 'delivery_value': 0,
                                             'return_value': 0, 'update': ''})
            if sale['doc_type_name'] == 'Продажа' and sale['quantity'] == 1:
                items_dict[dict_key]['sales_value'] += sale['ppvz_for_pay']
                items_dict[dict_key]['sales_count'] += 1
            elif sale['doc_type_name'] == 'Возврат' and sale['quantity'] == 1:
                items_dict[dict_key]['sales_value'] -= sale['ppvz_for_pay']
                items_dict[dict_key]['sales_count'] -= 1
                items_dict[dict_key]['return_value'] += sale['ppvz_reward']
            elif sale['delivery_rub'] != 0:
                items_dict[dict_key]['delivery_value'] += sale['delivery_rub']
            if sale['rr_dt'] > items_dict[dict_key]['update']:
                items_dict[dict_key]['update'] = sale['rr_dt']
            if sale['rr_dt'] > last_date: last_date = sale['rr_dt']

        analytic_report = analytic_report_dict[supplier]
        storage_value = 0
        for year_values in analytic_report['consolidatedYears']:
            for month_values in year_values['consolidatedMonths']:
                for day_values in month_values['consolidatedDays']:
                    day = day_values['day'].split('.')[0]
                    month = month_values['month']
                    if f'{day}.{month}' in days: storage_value += day_values['storageCost']
        sales_count = sum([value['sales_count'] for key, value in items_dict.items()])
        if sales_count == 0: storage_value_by_item = 0
        else: storage_value_by_item = storage_value/sales_count

        for key, value in items_dict.items():
            if cost_dict['nm'].get(key[1]) is not None:
                cost = cost_dict['nm'][key[1]]
            elif cost_dict['article'].get(key[2].split('/')[0]+'/') is not None:
                cost = cost_dict['article'][key[2].split('/')[0]+'/']
            else: cost = 0
            oper_profit = value['sales_value'] - value['delivery_value'] - \
                          value['return_value'] - storage_value_by_item*value['sales_count'] - \
                          cost*value['sales_count']
            if value['sales_count'] == 0: oper_profit_by_item = 0
            else: oper_profit_by_item = oper_profit/value['sales_count']
            items_dict[key].update({'profit_value': oper_profit,
                                    'profit_value_by_item': oper_profit_by_item})

        table += sorted([list(key) + [value['sales_count'], value['profit_value'], value['profit_value_by_item']]
                         for key, value in items_dict.items()], key=lambda item: item[2])
    return table


def profit_size(input_data, weeks=4):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд',
              'Размер', 'Продажи, шт', 'Операционная прибыль, руб', 'Прибыль на шт, руб']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _profit_size_by_suppliers_list(input_data, weeks)
        #elif type(input_data[0]) == int: table = _profit_size_by_nm_list(input_data)
    elif type(input_data) == str: table = _profit_size_by_supplier(input_data, weeks)
    #elif type(input_data) == int: table = _profit_size_by_nm_list([input_data])
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _profit_color_by_supplier(supplier, weeks):
    report_list = fetch.detail_report(supplier=supplier, weeks=weeks)
    analytic_report = fetch.report(supplier=supplier)
    cost_dict = fetch.cost()
    items_dict = dict()
    last_date = ''

    for sale in report_list:
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
    days = info.days_list(to_date=last_date.split('T')[0],
           from_date=str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=6)).date()))
    buyouts_dict = dict()
    for nm, values in fetch.buyouts().items():
        buyouts_dict[nm] = {'buyouts_count': 0, 'buyouts_value': 0}
        for buyout in values['buyouts']:
            if buyout[0] in days:
                buyouts_dict[nm]['buyouts_count'] += buyout[1]
                buyouts_dict[nm]['buyouts_value'] += buyout[1] * buyout[2]

    for sale in report_list:
        if datetime.strptime(sale['rr_dt'], '%Y-%m-%dT00:00:00Z').strftime('%d.%m') not in days: continue
        dict_key = (wb_info.supplier_name(supplier), sale['nm_id'],
                    sale['sa_name'], sale['subject_name'], sale['brand_name'], sale['ts_name'])
        items_dict.setdefault(dict_key, {'sales_value': 0, 'sales_count': 0, 'delivery_value': 0,
                                         'return_value': 0, 'update': ''})
        if buyouts_dict.get(sale['nm_id']) is not None:
            items_dict[dict_key]['sales_value'] -= buyouts_dict[sale['nm_id']]['buyouts_value']
            items_dict[dict_key]['sales_count'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
            buyouts_dict.pop(sale['nm_id'])
        if sale['doc_type_name'] == 'Продажа' and sale['quantity'] == 1:
            items_dict[dict_key]['sales_value'] += sale['ppvz_for_pay']
            items_dict[dict_key]['sales_count'] += 1
        elif sale['doc_type_name'] == 'Возврат' and sale['quantity'] == 1:
            items_dict[dict_key]['sales_value'] -= sale['ppvz_for_pay']
            items_dict[dict_key]['sales_count'] -= 1
            items_dict[dict_key]['return_value'] += sale['ppvz_reward']
        elif sale['delivery_rub'] != 0:
            items_dict[dict_key]['delivery_value'] += sale['delivery_rub']
        if sale['rr_dt'] > items_dict[dict_key]['update']:
            items_dict[dict_key]['update'] = sale['rr_dt']
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']

    storage_value = 0
    for year_values in analytic_report['consolidatedYears']:
        for month_values in year_values['consolidatedMonths']:
            for day_values in month_values['consolidatedDays']:
                day = day_values['day'].split('.')[0]
                month = month_values['month']
                if f'{day}.{month}' in days: storage_value += day_values['storageCost']
    sales_count = sum([value['sales_count'] for key, value in items_dict.items()])
    if sales_count == 0: storage_value_by_item = 0
    else: storage_value_by_item = storage_value/sales_count

    for key, value in items_dict.items():
        if cost_dict['nm'].get(key[1]) is not None:
            cost = cost_dict['nm'][key[1]]
        elif cost_dict['article'].get(key[2].split('/')[0]+'/') is not None:
            cost = cost_dict['article'][key[2].split('/')[0]+'/']
        else: cost = 0
        oper_profit = value['sales_value'] - value['delivery_value'] - \
                      value['return_value'] - storage_value_by_item*value['sales_count'] - \
                      cost*value['sales_count']
        if value['sales_count'] == 0: oper_profit_by_item = 0
        else: oper_profit_by_item = oper_profit/value['sales_count']
        items_dict[key].update({'profit_value': oper_profit,
                                'profit_value_by_item': oper_profit_by_item})

    color_items_dict = dict()
    for key, value in items_dict.items():
        dict_key = (key[0], key[1], key[2], key[3], key[4])
        color_items_dict.setdefault(dict_key, {'sales_count': 0, 'profit_value': 0, 'profit_value_by_item': 0})
        color_items_dict[dict_key]['sales_count'] += value['sales_count']
        color_items_dict[dict_key]['profit_value'] += value['profit_value']
        if color_items_dict[dict_key]['sales_count'] == 0:
            color_items_dict[dict_key]['profit_value_by_item'] = 0
        else: color_items_dict[dict_key]['profit_value_by_item'] = \
            color_items_dict[dict_key]['profit_value'] / color_items_dict[dict_key]['sales_count']

    table = sorted([list(key) + [value['sales_count'], value['profit_value'], value['profit_value_by_item']]
                   for key, value in color_items_dict.items()],
                   key=lambda item: item[2])
    return table


def _profit_color_by_suppliers_list(suppliers_list, weeks):
    report_dict = fetch.detail_report(suppliers_list=suppliers_list, weeks=weeks)
    analytic_report_dict = fetch.report(suppliers_list=suppliers_list)
    cost_dict = fetch.cost()
    last_date = ''
    for sale in report_dict['tumanyan']:
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
    days = info.days_list(to_date=last_date.split('T')[0],
                          from_date=str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=6)).date()))
    buyouts_dict = dict()
    for nm, values in fetch.buyouts().items():
        buyouts_dict[nm] = {'buyouts_count': 0, 'buyouts_value': 0}
        for buyout in values['buyouts']:
            if buyout[0] in days:
                buyouts_dict[nm]['buyouts_count'] += buyout[1]
                buyouts_dict[nm]['buyouts_value'] += buyout[1] * buyout[2]

    table = list()
    for supplier, report_list in report_dict.items():
        items_dict = dict()
        for sale in report_list:
            if datetime.strptime(sale['rr_dt'], '%Y-%m-%dT00:00:00Z').strftime('%d.%m') not in days: continue
            dict_key = (wb_info.supplier_name(supplier), sale['nm_id'],
                        sale['sa_name'], sale['subject_name'], sale['brand_name'], sale['ts_name'])
            items_dict.setdefault(dict_key, {'sales_value': 0, 'sales_count': 0, 'delivery_value': 0,
                                             'return_value': 0, 'update': ''})
            if buyouts_dict.get(sale['nm_id']) is not None:
                items_dict[dict_key]['sales_value'] -= buyouts_dict[sale['nm_id']]['buyouts_value']
                items_dict[dict_key]['sales_count'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
                buyouts_dict.pop(sale['nm_id'])
            if sale['doc_type_name'] == 'Продажа' and sale['quantity'] == 1:
                items_dict[dict_key]['sales_value'] += sale['ppvz_for_pay']
                items_dict[dict_key]['sales_count'] += 1
            elif sale['doc_type_name'] == 'Возврат' and sale['quantity'] == 1:
                items_dict[dict_key]['sales_value'] -= sale['ppvz_for_pay']
                items_dict[dict_key]['sales_count'] -= 1
                items_dict[dict_key]['return_value'] += sale['ppvz_reward']
            elif sale['delivery_rub'] != 0:
                items_dict[dict_key]['delivery_value'] += sale['delivery_rub']
            if sale['rr_dt'] > items_dict[dict_key]['update']:
                items_dict[dict_key]['update'] = sale['rr_dt']
            if sale['rr_dt'] > last_date: last_date = sale['rr_dt']

        analytic_report = analytic_report_dict[supplier]
        storage_value = 0
        for year_values in analytic_report['consolidatedYears']:
            for month_values in year_values['consolidatedMonths']:
                for day_values in month_values['consolidatedDays']:
                    day = day_values['day'].split('.')[0]
                    month = month_values['month']
                    if f'{day}.{month}' in days: storage_value += day_values['storageCost']
        sales_count = sum([value['sales_count'] for key, value in items_dict.items()])
        if sales_count == 0: storage_value_by_item = 0
        else: storage_value_by_item = storage_value/sales_count

        for key, value in items_dict.items():
            if cost_dict['nm'].get(key[1]) is not None:
                cost = cost_dict['nm'][key[1]]
            elif cost_dict['article'].get(key[2].split('/')[0]+'/') is not None:
                cost = cost_dict['article'][key[2].split('/')[0]+'/']
            else: cost = 0
            oper_profit = value['sales_value'] - value['delivery_value'] - \
                          value['return_value'] - storage_value_by_item*value['sales_count'] - \
                          cost*value['sales_count']
            if value['sales_count'] == 0: oper_profit_by_item = 0
            else: oper_profit_by_item = oper_profit/value['sales_count']
            items_dict[key].update({'profit_value': oper_profit,
                                    'profit_value_by_item': oper_profit_by_item})

        color_items_dict = dict()
        for key, value in items_dict.items():
            dict_key = (key[0], key[1], key[2], key[3], key[4])
            color_items_dict.setdefault(dict_key, {'sales_count': 0, 'profit_value': 0, 'profit_value_by_item': 0})
            color_items_dict[dict_key]['sales_count'] += value['sales_count']
            color_items_dict[dict_key]['profit_value'] += value['profit_value']
            if color_items_dict[dict_key]['sales_count'] == 0:
                color_items_dict[dict_key]['profit_value_by_item'] = 0
            else:
                color_items_dict[dict_key]['profit_value_by_item'] = \
                    color_items_dict[dict_key]['profit_value'] / color_items_dict[dict_key]['sales_count']

        table += sorted([list(key) + [value['sales_count'], value['profit_value'], value['profit_value_by_item']]
                         for key, value in color_items_dict.items()], key=lambda item: item[2])
    return table


def profit_color(input_data, weeks=4):
    header = ['Организация', 'Номенклатура', 'Артикул поставщика', 'Предмет', 'Бренд',
              'Продажи, шт', 'Операционная прибыль, руб', 'Прибыль на шт, руб']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _profit_color_by_suppliers_list(input_data, weeks)
        #elif type(input_data[0]) == int: table = _profit_size_by_nm_list(input_data)
    elif type(input_data) == str: table = _profit_color_by_supplier(input_data, weeks)
    #elif type(input_data) == int: table = _profit_size_by_nm_list([input_data])
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _profit_article_by_supplier(supplier, weeks):
    report_list = fetch.detail_report(supplier=supplier, weeks=weeks)
    analytic_report = fetch.report(supplier=supplier)
    cost_dict = fetch.cost()
    items_dict = dict()
    last_date = ''

    for sale in report_list:
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
    days = info.days_list(to_date=last_date.split('T')[0],
           from_date=str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=6)).date()))
    buyouts_dict = dict()
    for nm, values in fetch.buyouts().items():
        buyouts_dict[nm] = {'buyouts_count': 0, 'buyouts_value': 0}
        for buyout in values['buyouts']:
            if buyout[0] in days:
                buyouts_dict[nm]['buyouts_count'] += buyout[1]
                buyouts_dict[nm]['buyouts_value'] += buyout[1] * buyout[2]
    for sale in report_list:
        if datetime.strptime(sale['rr_dt'], '%Y-%m-%dT00:00:00Z').strftime('%d.%m') not in days: continue
        dict_key = (wb_info.supplier_name(supplier), sale['nm_id'],
                    sale['sa_name'], sale['subject_name'], sale['brand_name'], sale['ts_name'])
        items_dict.setdefault(dict_key, {'sales_value': 0, 'sales_count': 0, 'delivery_value': 0,
                                         'return_value': 0, 'update': ''})
        if buyouts_dict.get(sale['nm_id']) is not None:
            items_dict[dict_key]['sales_value'] -= buyouts_dict[sale['nm_id']]['buyouts_value']
            items_dict[dict_key]['sales_count'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
            buyouts_dict.pop(sale['nm_id'])
        if sale['doc_type_name'] == 'Продажа' and sale['quantity'] == 1:
            items_dict[dict_key]['sales_value'] += sale['ppvz_for_pay']
            items_dict[dict_key]['sales_count'] += 1
        elif sale['doc_type_name'] == 'Возврат' and sale['quantity'] == 1:
            items_dict[dict_key]['sales_value'] -= sale['ppvz_for_pay']
            items_dict[dict_key]['sales_count'] -= 1
            items_dict[dict_key]['return_value'] += sale['ppvz_reward']
        elif sale['delivery_rub'] != 0:
            items_dict[dict_key]['delivery_value'] += sale['delivery_rub']
        if sale['rr_dt'] > items_dict[dict_key]['update']:
            items_dict[dict_key]['update'] = sale['rr_dt']
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']

    storage_value = 0
    for year_values in analytic_report['consolidatedYears']:
        for month_values in year_values['consolidatedMonths']:
            for day_values in month_values['consolidatedDays']:
                day = day_values['day'].split('.')[0]
                month = month_values['month']
                if f'{day}.{month}' in days: storage_value += day_values['storageCost']
    sales_count = sum([value['sales_count'] for key, value in items_dict.items()])
    if sales_count == 0: storage_value_by_item = 0
    else: storage_value_by_item = storage_value/sales_count

    for key, value in items_dict.items():
        if cost_dict['nm'].get(key[1]) is not None:
            cost = cost_dict['nm'][key[1]]
        elif cost_dict['article'].get(key[2].split('/')[0]+'/') is not None:
            cost = cost_dict['article'][key[2].split('/')[0]+'/']
        else: cost = 0
        oper_profit = value['sales_value'] - value['delivery_value'] - \
                      value['return_value'] - storage_value_by_item*value['sales_count'] - \
                      cost*value['sales_count']
        if value['sales_count'] == 0: oper_profit_by_item = 0
        else: oper_profit_by_item = oper_profit/value['sales_count']
        items_dict[key].update({'profit_value': oper_profit,
                                'profit_value_by_item': oper_profit_by_item})

    article_items_dict = dict()
    for key, value in items_dict.items():
        dict_key = (key[0], key[2].split('/')[0]+'/', key[3], key[4])
        article_items_dict.setdefault(dict_key, {'sales_count': 0, 'profit_value': 0, 'profit_value_by_item': 0})
        article_items_dict[dict_key]['sales_count'] += value['sales_count']
        article_items_dict[dict_key]['profit_value'] += value['profit_value']
        if article_items_dict[dict_key]['sales_count'] == 0:
            article_items_dict[dict_key]['profit_value_by_item'] = 0
        else: article_items_dict[dict_key]['profit_value_by_item'] = \
            article_items_dict[dict_key]['profit_value'] / article_items_dict[dict_key]['sales_count']

    table = sorted([list(key) + [value['sales_count'], value['profit_value'], value['profit_value_by_item']]
                   for key, value in article_items_dict.items()],
                   key=lambda item: item[1])
    return table


def _profit_article_by_suppliers_list(suppliers_list, weeks):
    report_dict = fetch.detail_report(suppliers_list=suppliers_list, weeks=weeks)
    analytic_report_dict = fetch.report(suppliers_list=suppliers_list)
    cost_dict = fetch.cost()
    last_date = ''
    for sale in report_dict['tumanyan']:
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
    days = info.days_list(to_date=last_date.split('T')[0],
                          from_date=str(
                              (datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=6)).date()))
    buyouts_dict = dict()
    for nm, values in fetch.buyouts().items():
        buyouts_dict[nm] = {'buyouts_count': 0, 'buyouts_value': 0}
        for buyout in values['buyouts']:
            if buyout[0] in days:
                buyouts_dict[nm]['buyouts_count'] += buyout[1]
                buyouts_dict[nm]['buyouts_value'] += buyout[1] * buyout[2]

    table = list()
    for supplier, report_list in report_dict.items():
        items_dict = dict()
        for sale in report_list:
            if datetime.strptime(sale['rr_dt'], '%Y-%m-%dT00:00:00Z').strftime('%d.%m') not in days: continue
            dict_key = (wb_info.supplier_name(supplier), sale['nm_id'],
                        sale['sa_name'], sale['subject_name'], sale['brand_name'], sale['ts_name'])
            items_dict.setdefault(dict_key, {'sales_value': 0, 'sales_count': 0, 'delivery_value': 0,
                                             'return_value': 0, 'update': ''})
            if buyouts_dict.get(sale['nm_id']) is not None:
                items_dict[dict_key]['sales_value'] -= buyouts_dict[sale['nm_id']]['buyouts_value']
                items_dict[dict_key]['sales_count'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
                buyouts_dict.pop(sale['nm_id'])
            if sale['doc_type_name'] == 'Продажа' and sale['quantity'] == 1:
                items_dict[dict_key]['sales_value'] += sale['ppvz_for_pay']
                items_dict[dict_key]['sales_count'] += 1
            elif sale['doc_type_name'] == 'Возврат' and sale['quantity'] == 1:
                items_dict[dict_key]['sales_value'] -= sale['ppvz_for_pay']
                items_dict[dict_key]['sales_count'] -= 1
                items_dict[dict_key]['return_value'] += sale['ppvz_reward']
            elif sale['delivery_rub'] != 0:
                items_dict[dict_key]['delivery_value'] += sale['delivery_rub']
            if sale['rr_dt'] > items_dict[dict_key]['update']:
                items_dict[dict_key]['update'] = sale['rr_dt']
            if sale['rr_dt'] > last_date: last_date = sale['rr_dt']

        analytic_report = analytic_report_dict[supplier]
        storage_value = 0
        for year_values in analytic_report['consolidatedYears']:
            for month_values in year_values['consolidatedMonths']:
                for day_values in month_values['consolidatedDays']:
                    day = day_values['day'].split('.')[0]
                    month = month_values['month']
                    if f'{day}.{month}' in days: storage_value += day_values['storageCost']
        sales_count = sum([value['sales_count'] for key, value in items_dict.items()])
        if sales_count == 0: storage_value_by_item = 0
        else: storage_value_by_item = storage_value/sales_count

        for key, value in items_dict.items():
            if cost_dict['nm'].get(key[1]) is not None:
                cost = cost_dict['nm'][key[1]]
            elif cost_dict['article'].get(key[2].split('/')[0]+'/') is not None:
                cost = cost_dict['article'][key[2].split('/')[0]+'/']
            else: cost = 0
            oper_profit = value['sales_value'] - value['delivery_value'] - \
                          value['return_value'] - storage_value_by_item*value['sales_count'] - \
                          cost*value['sales_count']
            if value['sales_count'] == 0: oper_profit_by_item = 0
            else: oper_profit_by_item = oper_profit/value['sales_count']
            items_dict[key].update({'profit_value': oper_profit,
                                    'profit_value_by_item': oper_profit_by_item})

        article_items_dict = dict()
        for key, value in items_dict.items():
            dict_key = (key[0], key[2].split('/')[0]+'/', key[3], key[4])
            article_items_dict.setdefault(dict_key, {'sales_count': 0, 'profit_value': 0, 'profit_value_by_item': 0})
            article_items_dict[dict_key]['sales_count'] += value['sales_count']
            article_items_dict[dict_key]['profit_value'] += value['profit_value']
            if article_items_dict[dict_key]['sales_count'] == 0:
                article_items_dict[dict_key]['profit_value_by_item'] = 0
            else:
                article_items_dict[dict_key]['profit_value_by_item'] = \
                    article_items_dict[dict_key]['profit_value'] / article_items_dict[dict_key]['sales_count']

        table += sorted([list(key) + [value['sales_count'], value['profit_value'], value['profit_value_by_item']]
                         for key, value in article_items_dict.items()], key=lambda item: item[1])
    return table


def profit_article(input_data, weeks=4):
    header = ['Организация', 'Артикул поставщика', 'Предмет', 'Бренд',
              'Продажи, шт', 'Операционная прибыль, руб', 'Прибыль на шт, руб']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _profit_article_by_suppliers_list(input_data, weeks)
        #elif type(input_data[0]) == int: table = _profit_size_by_nm_list(input_data)
    elif type(input_data) == str: table = _profit_article_by_supplier(input_data, weeks)
    #elif type(input_data) == int: table = _profit_size_by_nm_list([input_data])
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _profit_category_by_supplier(supplier, weeks):
    report_list = fetch.detail_report(supplier=supplier, weeks=weeks)
    analytic_report = fetch.report(supplier=supplier)
    cost_dict = fetch.cost()
    items_dict = dict()
    last_date = ''

    for sale in report_list:
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
    days = info.days_list(to_date=last_date.split('T')[0],
           from_date=str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=6)).date()))
    buyouts_dict = dict()
    for nm, values in fetch.buyouts().items():
        buyouts_dict[nm] = {'buyouts_count': 0, 'buyouts_value': 0}
        for buyout in values['buyouts']:
            if buyout[0] in days:
                buyouts_dict[nm]['buyouts_count'] += buyout[1]
                buyouts_dict[nm]['buyouts_value'] += buyout[1] * buyout[2]
    for sale in report_list:
        if datetime.strptime(sale['rr_dt'], '%Y-%m-%dT00:00:00Z').strftime('%d.%m') not in days: continue
        dict_key = (wb_info.supplier_name(supplier), sale['nm_id'],
                    sale['sa_name'], sale['subject_name'], sale['brand_name'], sale['ts_name'])
        items_dict.setdefault(dict_key, {'sales_value': 0, 'sales_count': 0, 'delivery_value': 0,
                                         'return_value': 0, 'update': ''})
        if buyouts_dict.get(sale['nm_id']) is not None:
            items_dict[dict_key]['sales_value'] -= buyouts_dict[sale['nm_id']]['buyouts_value']
            items_dict[dict_key]['sales_count'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
            buyouts_dict.pop(sale['nm_id'])
        if sale['doc_type_name'] == 'Продажа' and sale['quantity'] == 1:
            items_dict[dict_key]['sales_value'] += sale['ppvz_for_pay']
            items_dict[dict_key]['sales_count'] += 1
        elif sale['doc_type_name'] == 'Возврат' and sale['quantity'] == 1:
            items_dict[dict_key]['sales_value'] -= sale['ppvz_for_pay']
            items_dict[dict_key]['sales_count'] -= 1
            items_dict[dict_key]['return_value'] += sale['ppvz_reward']
        elif sale['delivery_rub'] != 0:
            items_dict[dict_key]['delivery_value'] += sale['delivery_rub']
        if sale['rr_dt'] > items_dict[dict_key]['update']:
            items_dict[dict_key]['update'] = sale['rr_dt']
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']

    storage_value = 0
    for year_values in analytic_report['consolidatedYears']:
        for month_values in year_values['consolidatedMonths']:
            for day_values in month_values['consolidatedDays']:
                day = day_values['day'].split('.')[0]
                month = month_values['month']
                if f'{day}.{month}' in days: storage_value += day_values['storageCost']
    sales_count = sum([value['sales_count'] for key, value in items_dict.items()])
    if sales_count == 0: storage_value_by_item = 0
    else: storage_value_by_item = storage_value/sales_count

    for key, value in items_dict.items():
        if cost_dict['nm'].get(key[1]) is not None:
            cost = cost_dict['nm'][key[1]]
        elif cost_dict['article'].get(key[2].split('/')[0]+'/') is not None:
            cost = cost_dict['article'][key[2].split('/')[0]+'/']
        else: cost = 0
        oper_profit = value['sales_value'] - value['delivery_value'] - \
                      value['return_value'] - storage_value_by_item*value['sales_count'] - \
                      cost*value['sales_count']
        if value['sales_count'] == 0: oper_profit_by_item = 0
        else: oper_profit_by_item = oper_profit/value['sales_count']
        items_dict[key].update({'profit_value': oper_profit,
                                'profit_value_by_item': oper_profit_by_item})

    category_items_dict = dict()
    for key, value in items_dict.items():
        dict_key = tuple([key[3]])
        category_items_dict.setdefault(dict_key, {'sales_count': 0, 'profit_value': 0, 'profit_value_by_item': 0})
        category_items_dict[dict_key]['sales_count'] += value['sales_count']
        category_items_dict[dict_key]['profit_value'] += value['profit_value']
        if category_items_dict[dict_key]['sales_count'] == 0:
            category_items_dict[dict_key]['profit_value_by_item'] = 0
        else: category_items_dict[dict_key]['profit_value_by_item'] = \
            category_items_dict[dict_key]['profit_value'] / category_items_dict[dict_key]['sales_count']

    table = sorted([list(key) + [value['sales_count'], value['profit_value'], value['profit_value_by_item']]
                   for key, value in category_items_dict.items()],
                   key=lambda item: item[1], reverse=True)
    return table


def _profit_category_by_suppliers_list(suppliers_list, weeks):
    report_dict = fetch.detail_report(suppliers_list=suppliers_list, weeks=weeks)
    analytic_report_dict = fetch.report(suppliers_list=suppliers_list)
    cost_dict = fetch.cost()
    last_date = ''
    for sale in report_dict['tumanyan']:
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
    days = info.days_list(to_date=last_date.split('T')[0],
                          from_date=str(
                              (datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=6)).date()))
    buyouts_dict = dict()
    for nm, values in fetch.buyouts().items():
        buyouts_dict[nm] = {'buyouts_count': 0, 'buyouts_value': 0}
        for buyout in values['buyouts']:
            if buyout[0] in days:
                buyouts_dict[nm]['buyouts_count'] += buyout[1]
                buyouts_dict[nm]['buyouts_value'] += buyout[1] * buyout[2]
    items_dict = dict()
    for supplier, report_list in report_dict.items():
        for sale in report_list:
            if datetime.strptime(sale['rr_dt'], '%Y-%m-%dT00:00:00Z').strftime('%d.%m') not in days: continue
            dict_key = (wb_info.supplier_name(supplier), sale['nm_id'],
                        sale['sa_name'], sale['subject_name'], sale['brand_name'], sale['ts_name'])
            items_dict.setdefault(dict_key, {'sales_value': 0, 'sales_count': 0, 'delivery_value': 0,
                                             'return_value': 0, 'update': ''})
            if buyouts_dict.get(sale['nm_id']) is not None:
                items_dict[dict_key]['sales_value'] -= buyouts_dict[sale['nm_id']]['buyouts_value']
                items_dict[dict_key]['sales_count'] -= buyouts_dict[sale['nm_id']]['buyouts_count']
                buyouts_dict.pop(sale['nm_id'])
            if sale['doc_type_name'] == 'Продажа' and sale['quantity'] == 1:
                items_dict[dict_key]['sales_value'] += sale['ppvz_for_pay']
                items_dict[dict_key]['sales_count'] += 1
            elif sale['doc_type_name'] == 'Возврат' and sale['quantity'] == 1:
                items_dict[dict_key]['sales_value'] -= sale['ppvz_for_pay']
                items_dict[dict_key]['sales_count'] -= 1
                items_dict[dict_key]['return_value'] += sale['ppvz_reward']
            elif sale['delivery_rub'] != 0:
                items_dict[dict_key]['delivery_value'] += sale['delivery_rub']
            if sale['rr_dt'] > items_dict[dict_key]['update']:
                items_dict[dict_key]['update'] = sale['rr_dt']
            if sale['rr_dt'] > last_date: last_date = sale['rr_dt']

        analytic_report = analytic_report_dict[supplier]
        storage_value = 0
        for year_values in analytic_report['consolidatedYears']:
            for month_values in year_values['consolidatedMonths']:
                for day_values in month_values['consolidatedDays']:
                    day = day_values['day'].split('.')[0]
                    month = month_values['month']
                    if f'{day}.{month}' in days: storage_value += day_values['storageCost']
        sales_count = sum([value['sales_count'] for key, value in items_dict.items()])
        if sales_count == 0: storage_value_by_item = 0
        else: storage_value_by_item = storage_value/sales_count

        for key, value in items_dict.items():
            if cost_dict['nm'].get(key[1]) is not None:
                cost = cost_dict['nm'][key[1]]
            elif cost_dict['article'].get(key[2].split('/')[0]+'/') is not None:
                cost = cost_dict['article'][key[2].split('/')[0]+'/']
            else: cost = 0
            oper_profit = value['sales_value'] - value['delivery_value'] - \
                          value['return_value'] - storage_value_by_item*value['sales_count'] - \
                          cost*value['sales_count']
            if value['sales_count'] == 0: oper_profit_by_item = 0
            else: oper_profit_by_item = oper_profit/value['sales_count']
            items_dict[key].update({'profit_value': oper_profit,
                                    'profit_value_by_item': oper_profit_by_item})

    category_items_dict = dict()
    for key, value in items_dict.items():
        dict_key = tuple([key[3]])
        category_items_dict.setdefault(dict_key, {'sales_count': 0, 'profit_value': 0, 'profit_value_by_item': 0})
        category_items_dict[dict_key]['sales_count'] += value['sales_count']
        category_items_dict[dict_key]['profit_value'] += value['profit_value']
        if category_items_dict[dict_key]['sales_count'] == 0:
            category_items_dict[dict_key]['profit_value_by_item'] = 0
        else:
            category_items_dict[dict_key]['profit_value_by_item'] = \
                category_items_dict[dict_key]['profit_value'] / category_items_dict[dict_key]['sales_count']

    return sorted([list(key) + [value['sales_count'], value['profit_value'], value['profit_value_by_item']]
                         for key, value in category_items_dict.items()], key=lambda item: item[1], reverse=True)


def profit_category(input_data, weeks=4):
    header = ['Категория', 'Продажи, шт', 'Операционная прибыль, руб', 'Прибыль на шт, руб']
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _profit_category_by_suppliers_list(input_data, weeks)
        #elif type(input_data[0]) == int: table = _profit_size_by_nm_list(input_data)
    elif type(input_data) == str: table = _profit_category_by_supplier(input_data, weeks)
    #elif type(input_data) == int: table = _profit_size_by_nm_list([input_data])
    else: raise ValueError("Unable to recognize input data")
    table.insert(0, header)
    return table


def _profit_compare_by_suppliers_list(suppliers_list, weeks):
    report_dict = fetch.detail_report(suppliers_list=suppliers_list, weeks=weeks)
    analytic_report_dict = fetch.report(suppliers_list=suppliers_list)
    last_date = ''
    for sale in report_dict[suppliers_list[0]]:
        if sale['rr_dt'] > last_date: last_date = sale['rr_dt']
    start_date = str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=(weeks*7-1))).date())
    orders_dict = fetch.orders(suppliers_list=suppliers_list, start_date=start_date)
    buyouts_dict = fetch.buyouts()
    cost_dict = fetch.cost()

    period = list()
    result_dict = dict()
    for i in range(weeks):
        items_dict = dict()
        days = info.days_list(to_date=str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=(7*i))).date()),
               from_date=str((datetime.strptime(last_date, '%Y-%m-%dT00:00:00Z') - timedelta(days=(6+7*i))).date()))
        buyouts_week_dict = dict()
        for nm, values in fetch.buyouts().items():
            buyouts_week_dict[nm] = {'buyouts_count': 0, 'buyouts_value': 0}
            for buyout in values['buyouts']:
                if buyout[0] in days:
                    buyouts_week_dict[nm]['buyouts_count'] += buyout[1]
                    buyouts_week_dict[nm]['buyouts_value'] += buyout[1] * buyout[2]
        for supplier, report_list in report_dict.items():
            for sale in report_list:
                if datetime.strptime(sale['rr_dt'], '%Y-%m-%dT00:00:00Z').strftime('%d.%m') not in days: continue
                dict_key = (wb_info.supplier_name(supplier), sale['nm_id'],
                            sale['sa_name'], sale['subject_name'], sale['brand_name'], sale['ts_name'])
                items_dict.setdefault(dict_key, {'sales_value': 0, 'sales_count': 0, 'delivery_value': 0,
                                                 'return_value': 0, 'update': ''})
                if buyouts_week_dict.get(sale['nm_id']) is not None:
                    items_dict[dict_key]['sales_value'] -= buyouts_week_dict[sale['nm_id']]['buyouts_value']
                    items_dict[dict_key]['sales_count'] -= buyouts_week_dict[sale['nm_id']]['buyouts_count']
                    buyouts_week_dict.pop(sale['nm_id'])
                if sale['doc_type_name'] == 'Продажа' and sale['quantity'] == 1:
                    items_dict[dict_key]['sales_value'] += sale['ppvz_for_pay']
                    items_dict[dict_key]['sales_count'] += 1
                elif sale['doc_type_name'] == 'Возврат' and sale['quantity'] == 1:
                    items_dict[dict_key]['sales_value'] -= sale['ppvz_for_pay']
                    items_dict[dict_key]['sales_count'] -= 1
                    items_dict[dict_key]['return_value'] += sale['ppvz_reward']
                elif sale['delivery_rub'] != 0:
                    items_dict[dict_key]['delivery_value'] += sale['delivery_rub']
                if sale['rr_dt'] > items_dict[dict_key]['update']:
                    items_dict[dict_key]['update'] = sale['rr_dt']
                if sale['rr_dt'] > last_date: last_date = sale['rr_dt']

            analytic_report = analytic_report_dict[supplier]
            storage_value = 0
            for year_values in analytic_report['consolidatedYears']:
                for month_values in year_values['consolidatedMonths']:
                    for day_values in month_values['consolidatedDays']:
                        day = day_values['day'].split('.')[0]
                        month = month_values['month']
                        if f'{day}.{month}' in days: storage_value += day_values['storageCost']
            sales_count = sum([value['sales_count'] for key, value in items_dict.items()])
            if sales_count == 0: storage_value_by_item = 0
            else: storage_value_by_item = storage_value/sales_count

            for key, value in items_dict.items():
                if cost_dict['nm'].get(key[1]) is not None:
                    cost = cost_dict['nm'][key[1]]
                elif cost_dict['article'].get(key[2].split('/')[0]+'/') is not None:
                    cost = cost_dict['article'][key[2].split('/')[0]+'/']
                else: cost = 0
                items_dict[key]['profit_value'] = value['sales_value'] - value['delivery_value'] - \
                              value['return_value'] - storage_value_by_item*value['sales_count'] - \
                              cost*value['sales_count']

        categories_orders_dict = dict()
        for supplier, orders_list in orders_dict.items():
            for order in orders_list:
                category = order['subject']
                if categories_orders_dict.get(category) is None: categories_orders_dict[category] = 0
                try:
                    day = datetime.strptime(order['date'], '%Y-%m-%dT%H:%M:%S').date().strftime('%d.%m')
                    if day in days:
                        final_price = order['totalPrice'] * (100 - order['discountPercent']) / 100
                        categories_orders_dict[category] += final_price
                    if buyouts_dict.get(order['nmId']) is not None:
                        buyouts_dict[order['nmId']].update({'category': category})
                except KeyError: pass

        for nm, values in buyouts_dict.items():
            if values.get('category') is not None:
                for buyout in values['buyouts']:
                    if buyout[0] in days: categories_orders_dict[values['category']] -= buyout[1] * buyout[2]

        period.append(f'{days[0]} - {days[-1]}')
        for key, value in items_dict.items():
            category = key[3]
            if result_dict.get(category) is None: result_dict[category] = dict()
            result_dict[category].setdefault(period[i], {'profit_value': 0, 'orders_value': 0})
            result_dict[category][period[i]]['profit_value'] += value['profit_value']
        for category, value in categories_orders_dict.items():
            if result_dict.get(category) is None: result_dict[category] = dict()
            result_dict[category].setdefault(period[i], {'profit_value': 0, 'orders_value': 0})
            result_dict[category][period[i]]['orders_value'] += value

    table = list()
    for category, period_values in result_dict.items():
        row = [category]
        for day_period in period:
            row += [period_values[day_period]['profit_value'], period_values[day_period]['orders_value']]
        table.append(row)
    table.sort(key=lambda item: sum(item[1:]), reverse=True)
    period_with_spaces = list()
    for item in period:
        period_with_spaces.append(item)
        period_with_spaces.append('')
    table = [['Недели'] + period_with_spaces, ['Категории'] + ['Операционная прибыль, руб', 'Заказы, руб']*weeks] + table
    return table


def profit_compare(input_data, weeks=4):
    table = list()
    if type(input_data) == list:
        if type(input_data[0]) == str: table = _profit_compare_by_suppliers_list(input_data, weeks)
        #elif type(input_data[0]) == int: table = _profit_size_by_nm_list(input_data)
    #elif type(input_data) == str: table = _profit_compare_by_supplier(input_data, weeks)
    #elif type(input_data) == int: table = _profit_size_by_nm_list([input_data])
    else: raise ValueError("Unable to recognize input data")
    return table

max_categories_convert_dict = { 'Одежда/Туники': 'Женщинам/Блузки и рубашки',
                        'Одежда/Куртки': 'Женщинам/Верхняя одежда',
                        'Обувь/Ботинки': 'Обувь/Женская',
                        'Одежда/Платья': 'Женщинам/Платья и сарафаны',
                        'Одежда/Костюмы': 'Женщинам/Костюмы',
                        'Одежда/Футболки': 'Женщинам/Футболки и топы',
                        'Одежда/Брюки': 'Женщинам/Брюки',
                        'Одежда/Блузки': 'Женщинам/Блузки и рубашки',
                        'Одежда/Леггинсы': 'Женщинам/Брюки',
                        'Одежда/Топы': 'Женщинам/Футболки и топы',
                        'Одежда/Юбки': 'Женщинам/Юбки',
                        'Одежда/Водолазки': 'Женщинам/Джемперы, водолазки и кардиганы',
                        'Одежда/Тренчкоты': 'Женщинам/Верхняя одежда',
                        'Одежда/Лонгсливы': 'Женщинам/Лонгсливы',
                        'Одежда/Пальто': 'Женщинам/Верхняя одежда',
                        'Одежда/Свитеры': 'Женщинам/Джемперы, водолазки и кардиганы',
                        'Одежда/Кардиганы': 'Женщинам/Джемперы, водолазки и кардиганы',
                        'Одежда/Жакеты': 'Женщинам/Пиджаки, жилеты и жакеты',
                        'Одежда/Шорты': 'Женщинам/Шорты',
                        'Одежда/Велосипедки': 'Женщинам/Шорты',
                        'Одежда/Рубашки': 'Женщинам/Блузки и рубашки',
                        'Одежда/Пиджаки': 'Женщинам/Пиджаки, жилеты и жакеты',
                        'Одежда/Джинсы': 'Женщинам/Джинсы',
                        'Обувь/Сабо': 'Обувь/Женская',
                        'Аксессуары/Сумки': 'Обувь/Женская',
                        'Обувь/Кроссовки': 'Обувь/Женская',
                        'Обувь/Угги': 'Обувь/Женская',
                        'Обувь/Лоферы': 'Обувь/Женская',
                        'Обувь/Мюли': 'Обувь/Женская',
                        'Обувь/Эспадрильи': 'Обувь/Женская',
                        'Обувь/Сандалии': 'Обувь/Женская',
                        'Обувь/Полуботинки': 'Обувь/Женская',
                        'Одежда/Блузки-боди': 'Женщинам/Блузки и рубашки',
                        'Спортивная одежда/Костюмы спортивные': 'Женщинам/Костюмы',
                        'Одежда/Косухи': 'Женщинам/Верхняя одежда',
                        'Спортивная одежда/Жилеты спортивные': 'Женщинам/Пиджаки, жилеты и жакеты',
                        'Одежда/Дубленки': 'Женщинам/Верхняя одежда',
                        'Одежда/Толстовки': 'Женщинам/Джемперы, водолазки и кардиганы',
                        'Одежда/Плащи': 'Женщинам/Верхняя одежда',
                        'Одежда/Жилеты': 'Женщинам/Пиджаки, жилеты и жакеты',
                        'Одежда/Свитшоты': 'Женщинам/Лонгсливы',
                        'Одежда/Ветровки': 'Женщинам/Верхняя одежда',
                        'Одежда/Худи': 'Женщинам/Лонгсливы',
                        'Одежда/Полупальто': 'Женщинам/Верхняя одежда',
                        'Обувь/Ботфорты': 'Обувь/Женская',
                        'Обувь/Кеды': 'Обувь/Женская',
                        'Обувь/Тапочки': 'Обувь/Женская',
                        'Одежда/Пуховики': 'Женщинам/Верхняя одежда',
                        'Обувь/Дутики': 'Обувь/Женская'}
def consolidated():
    worksheet = google_work.open_sheet(info.google_key('wb_consolidated'), 'Главная')
    input_columns = google_work.get_columns(worksheet, 1, 1, 3, 21, 22, 23, 24, 25, 26)
    items_dict = dict()
    for i in range(len(input_columns[0])):
        try:
            nm = int(input_columns[1][i])
            items_dict[nm] = {'is_new': True if input_columns[0][i] == 'TRUE' else False,
                              'is_card_actions': True if input_columns[2][i] == 'TRUE' else False,
                              'card_actions': input_columns[3][i],
                              'is_price_actions': True if input_columns[4][i] == 'TRUE' else False,
                              'price_actions': input_columns[5][i],
                              'is_shipment': True if input_columns[6][i] == 'TRUE' else False,
                              'is_order': True if input_columns[7][i] == 'TRUE' else False,
                              'rating': '',
                              'orders': [0,0,0,0,0,0,0],
                              'stocks': 0,
                              'all_stocks': 'Да',
                              'article': '',
                              'price': 0,
                              'category': '',
                              'max_category': 'Нет',
                              'our_stocks': 0,
                              'our_in_way': 0}
        except ValueError: pass

    cards_dict = fetch.cards(suppliers_list=wb_info.all_suppliers())
    for supplier, cards in cards_dict.items():
        for card in cards:
            category = f"{card['parent']}/{card['object']}"
            for nomenclature in card['nomenclatures']:
                article = f"{card['supplierVendorCode']}{nomenclature['vendorCode']}"
                if items_dict.get(nomenclature['nmId']) is not None:
                    items_dict[nomenclature['nmId']]['article'] = article
                    items_dict[nomenclature['nmId']]['category'] = category

    price_dict = {supplier: single_requests.fetch('GET', content_type='json',
                                                  url='https://suppliers-api.wildberries.ru/public/api/v1/info?quantity=0',
                                                  headers={'Authorization': wb_info.api_key('token', supplier)})
                  for supplier in wb_info.all_suppliers()}
    for items in price_dict.values():
        for item in items:
            nm = item['nmId']
            if items_dict.get(nm) is not None: items_dict[nm]['price'] = item['price']*(100-item['discount'])

    worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Категории')
    items_categories_columns = google_work.get_columns(worksheet, 1, 2, 12)
    items_categories_dict = {items_categories_columns[0][i]: items_categories_columns[1][i]
                           for i in range(len(items_categories_columns[0]))}
    worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Категории макс')
    max_categories_columns = google_work.get_columns(worksheet, 1, 2, 8)
    max_categories_dict = {max_categories_columns[0][i]: max_categories_columns[1][i]
                           for i in range(len(max_categories_columns[0]))}
    for nm, values in items_dict.items():
        if max_categories_convert_dict.get(items_dict[nm]['category']) is None: continue
        elif max_categories_convert_dict.get(items_categories_dict[nm]) is None: continue
        else:
            if max_categories_dict[max_categories_convert_dict[items_dict[nm]['category']]] == items_categories_dict[nm]:
                items_dict[nm]['max_category'] = 'Да'

    worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Отзывы')
    feedbacks_columns = google_work.get_columns(worksheet, 1, 2, 6)
    for i in range(len(feedbacks_columns[0])):
        try: items_dict[int(feedbacks_columns[0][i])]['rating'] = feedbacks_columns[1][i]
        except KeyError: pass

    worksheet = google_work.open_sheet(info.google_key('wb_consolidated'), 'Остатки наш склад')
    our_stocks_columns = google_work.get_columns(worksheet, 1, 2, 6)
    for i in range(len(our_stocks_columns[0])):
        article = our_stocks_columns[0][i]
        for nm, values in items_dict.items():
            if values['article'] == article: items_dict[nm]['our_stocks'] += our_stocks_columns[1][i]

    worksheet = google_work.open_sheet(info.google_key('wb_consolidated'), 'Заказы у поставщиков')
    our_orders_columns = google_work.get_columns(worksheet, 1, 5, 9)
    for i in range(len(our_orders_columns[0])):
        try: items_dict[int(our_orders_columns[0][i])]['our_in_way'] += our_orders_columns[1][i]
        except KeyError: pass

    worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'динамика, шт')
    orders_columns = google_work.get_columns(worksheet, 1, 2, 6, 7, 8, 9, 10, 11, 12)
    for i in range(len(orders_columns[0])):
        try: items_dict[int(orders_columns[0][i])]['orders'] = [int(orders_columns[j][i]) for j in range(1, len(orders_columns))]
        except KeyError: pass

    worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Остатки')
    stocks_columns = google_work.get_columns(worksheet, 1, 2, 9)
    for i in range(len(stocks_columns[0])):
        try:
            if int(stocks_columns[1][i]) == 0: items_dict[int(stocks_columns[0][i])]['all_stocks'] = 'Нет'
            else: items_dict[int(stocks_columns[0][i])]['stocks'] += int(stocks_columns[1][i])
        except KeyError: pass

    table = [['Новинка', 'Артикул', 'Номенклатура', 'Предмет', 'Макс категорий',
              'Высокий рейтинг'] + info.days_list(from_date=str(date.today()-timedelta(days=7)), to_yesterday=True) +
             ['График заказов',	'Все размеры', 'Остатки WB',
              'Оборот', 'Цена без СПП', 'Наши остатки', 'В пути к нам', 'Действия по карточке',
              'Действия по карточке', 'Действия по цене', 'Новая цена без СПП',
              'Нужно ли отгрузить?', 'Нужно ли заказать?']]
    notes = list()
    i = 1
    for nm, value in items_dict.items():
        i += 1
        row = list()
        row.append(value['is_new'])
        row.append(value['article'])
        row.append(nm)
        row.append(value['category'])
        row.append(value['max_category'])
        row.append(value['rating'])
        row += value['orders']
        row.append(f"""=SPARKLINE(G{i}:M{i};"""+"{\"charttype\"\\\"column\";\"color\"\\\"green\";\"ymin\"\\0})")
        row.append(value['all_stocks'])
        row.append(value['stocks'])
        row.append(value['stocks']/(sum(value['orders'])/7) if sum(value['orders']) > 0 else '')
        row.append(value['price'])
        row.append(value['our_stocks'])
        row.append(value['our_in_way'])
        row.append(value['is_card_actions'])
        row.append(value['card_actions'])
        row.append(value['is_price_actions'])
        row.append(value['price_actions'])
        row.append(value['is_shipment'])
        row.append(value['is_order'])
        table.append(row)
        notes.append([', '.join(list(map(str, value['orders'])))])
    return table, notes




