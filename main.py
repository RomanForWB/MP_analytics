from datetime import date, timedelta, datetime
from re import search, sub

import modules.info as info

import modules.google_work as google_work
import modules.google_special as google_special

import modules.wildberries.analytics as wb_analytics
import modules.wildberries.info as wb_info

import modules.ozon.analytics as ozon_analytics
import modules.ozon.info as ozon_info

choice = 'start'


def ask_start():
    """Asking a marketplace."""
    print("\n=======================================")
    print("========== Торговые площадки ==========")
    print("1 - Wildberries")
    print("2 - Ozon")
    print("3 - Сгенерировать ежедневные отчеты Wildberries")
    print("4 - Сгенерировать еженедельные отчеты Wildberries")
    print("5 - Сгенерировать аналитику Wildberries")
    print("6 - Сгенерировать ежедневные отчеты Ozon")
    print("7 - Сгенерировать аналитику Ozon")
    print("8 - Супертаблица Wildberries")
    global choice
    choice = input("Выбор: ")
    if choice.strip() == '1': choice = 'wb'
    elif choice.strip() == '2': choice = 'ozon'
    elif choice.strip() == '3': choice = 'wb_all_day_reports'
    elif choice.strip() == '4': choice = 'wb_all_week_reports'
    elif choice.strip() == '5': choice = 'wb_all_analytics'
    elif choice.strip() == '6': choice = 'ozon_all_day_reports'
    elif choice.strip() == '7': choice = 'ozon_all_analytics'
    elif choice.strip() == '8': choice = 'wb_consolidated'
    else:
        choice = 'start'
        print("Неправильный выбор...")


def ask_wb():
    """Presents wildberries actions to the user."""
    print("\n=======================================")
    print("============ Wildberries ==============")
    print("1 - Отчет по категориям")
    print("2 - Отчет по позициям")
    print("3 - Отчет по остаткам")
    print("4 - Отчет по отзывам")
    print("5 - Отчет по отгрузке")
    print("6 - Отчет по проценту выкупа (размер)")
    print("7 - Отчет по проценту выкупа (цвет)")
    print("8 - Отчет по проценту выкупа (артикул)")
    print("9 - Отчет по проценту выкупа (предмет)")
    print("10 - Отчет (день)")
    print("11 - Отчет (неделя)")
    print("12 - Отчет (месяц)")
    print("13 - Заказы (все)")
    print("14 - Заказы (топ 500)")
    print("15 - Заказы (новинки)")
    print("16 - Заказы (все категории)")
    print("17 - Заказы по товарам (кол-во)")
    print("18 - Заказы по товарам (сумма)")
    print("19 - Рентабельность (расчет)")
    print("20 - Рентабельность (размер)")
    print("21 - Рентабельность (цвет)")
    print("22 - Рентабельность (артикул)")
    print("23 - Рентабельность (предмет)")
    print("24 - Рентабельность (недели)")
    print("25 - Отчет по выручке")
    print("26 - Отчет по наибольшим категориям")
    print("27 - Отчет по трендам")
    print("28 - Супертаблица")
    print("29 - В начало")
    global choice
    choice = input("Выбор: ")
    if choice.strip() == '1': choice = 'wb_categories'
    elif choice.strip() == '2': choice = 'wb_positions'
    elif choice.strip() == '3': choice = 'wb_stocks'
    elif choice.strip() == '4': choice = 'wb_feedbacks'
    elif choice.strip() == '5': choice = 'wb_shipments'
    elif choice.strip() == '6': choice = 'wb_buyout_percent_size'
    elif choice.strip() == '7': choice = 'wb_buyout_percent_color'
    elif choice.strip() == '8': choice = 'wb_buyout_percent_article'
    elif choice.strip() == '9': choice = 'wb_buyout_percent_category'
    elif choice.strip() == '10': choice = 'wb_day_report'
    elif choice.strip() == '11': choice = 'wb_week_report'
    elif choice.strip() == '12': choice = 'wb_month_report'
    elif choice.strip() == '13': choice = 'wb_orders_category_all'
    elif choice.strip() == '14': choice = 'wb_orders_category_500'
    elif choice.strip() == '15': choice = 'wb_orders_category_new'
    elif choice.strip() == '16': choice = 'wb_orders_category_all_categories'
    elif choice.strip() == '17': choice = 'wb_orders_count'
    elif choice.strip() == '18': choice = 'wb_orders_value'
    elif choice.strip() == '19': choice = 'wb_profit'
    elif choice.strip() == '20': choice = 'wb_profit_size'
    elif choice.strip() == '21': choice = 'wb_profit_color'
    elif choice.strip() == '22': choice = 'wb_profit_article'
    elif choice.strip() == '23': choice = 'wb_profit_category'
    elif choice.strip() == '24': choice = 'wb_profit_compare'
    elif choice.strip() == '25': choice = 'wb_categories_revenue'
    elif choice.strip() == '26': choice = 'wb_max_categories'
    elif choice.strip() == '27': choice = 'wb_trends'
    elif choice.strip() == '28': choice = 'wb_consolidated'
    elif choice.strip() == '29': choice = 'start'
    else:
        choice = 'wb'
        print("Неправильный выбор...")


def ask_ozon():
    """Presents ozon actions to the user."""
    print("\n=======================================")
    print("================ Ozon =================")
    print("1 - Отчет по категориям")
    print("2 - Отчет по позициям")
    print("3 - Отчет по остаткам")
    print("4 - Отчет (день)")
    print("5 - Отчет (неделя)")
    print("6 - Отчет (месяц)")
    print("7 - Заказы по товарам (кол-во)")
    print("8 - Заказы по товарам (сумма)")
    print("9 - Заказы (все)")
    print("10 - Заказы (все категории)")
    print("11 - В начало")
    global choice
    choice = input("Выбор: ")
    if choice.strip() == '1': choice = 'ozon_categories'
    elif choice.strip() == '2': choice = 'ozon_positions'
    elif choice.strip() == '3': choice = 'ozon_stocks'
    elif choice.strip() == '4': choice = 'ozon_day_report'
    elif choice.strip() == '5': choice = 'ozon_week_report'
    elif choice.strip() == '6': choice = 'ozon_month_report'
    elif choice.strip() == '7': choice = 'ozon_orders_count'
    elif choice.strip() == '8': choice = 'ozon_orders_value'
    elif choice.strip() == '9': choice = 'ozon_orders_category_all'
    elif choice.strip() == '10': choice = 'ozon_orders_category_all_categories'
    elif choice.strip() == '11': choice = 'start'
    else:
        choice = 'ozon'
        print("Неправильный выбор...")


def ask_start_date():
    """Ask user about start date.

    :return: date string 'YYYY-MM-DD'
    :rtype: str
    """
    while True:
        print("\n1 - За последние 7 дней")
        print("2 - За последние 30 дней")
        print("3 - Свой вариант")
        day_choice = input("Выбор: ")
        if day_choice.strip() == '1': return str(date.today() - timedelta(days=6))
        elif day_choice.strip() == '2': return str(date.today() - timedelta(days=29))
        elif day_choice.strip() == '3':
            while True:
                input_date = input("Введите дату (YYYY-MM-DD): ").strip()
                if search(r'\d\d\d\d-\d\d-\d\d', input_date): return input_date
                else: print("Неправильная дата...")
        else: print("Неправильный выбор...")


def ask_report_period(skip_one=False):
    """Ask user about report period.

    :return: report start date (string 'YYYY-MM-DD')
    :rtype: str
    """
    while True:
        print("\n1 - По дню")
        print("2 - За неделю")
        print("3 - За месяц")
        print("4 - Свой вариант")
        day_choice = input("Выбор: ")
        if day_choice.strip() == '1':
            return str(date.today() - timedelta(days=8))
        elif day_choice.strip() == '2':
            return str(info.current_monday(skip_one))
        elif day_choice.strip() == '3':
            return str(info.current_month_start_date(skip_one))
        elif day_choice.strip() == '4':
            while True:
                start_date = input("Введите дату начала (YYYY-MM-DD): ").strip()
                if search(r'\d\d\d\d-\d\d-\d\d', start_date): return start_date
                else: print("Неправильная дата...")
        else: print("Неправильный выбор...")


def ask_nm_list():
    print('Введите список номенклатур (Enter нужно нажать два раза)')
    nm_list = list(iter(input, ""))
    return nm_list


def ask_wb_input(worksheet, skip_suppliers=False, skip_nm=False):
    while True:
        all_choice = None
        supplier_choices = None
        google_choice = None
        manual_choice = None
        # ========= Printing choices =========
        choice_counter = 0
        if not skip_suppliers:
            choice_counter += 1
            all_choice = choice_counter
            print(f"\n{all_choice} - Для всех")
            supplier_choices = dict()
            for supplier in wb_info.all_suppliers():
                choice_counter += 1
                print(f'{choice_counter} - {wb_info.supplier_name(supplier)}')
                supplier_choices[choice_counter] = supplier
        if not skip_nm:
            choice_counter += 1
            google_choice = choice_counter
            print(f'{google_choice} - Взять список номенклатур из таблицы \"{worksheet.title}\"')
            choice_counter += 1
            manual_choice = choice_counter
            print(f'{manual_choice} - Ввести список номенклатур')
        back_choice = choice_counter + 1
        print(f'{back_choice} - Назад')
        # ============= Selection =============
        try:
            input_choice = int(input("Выбор: ").strip())
            if all_choice is not None and input_choice == all_choice:
                return wb_info.all_suppliers()
            elif supplier_choices is not None and input_choice in supplier_choices.keys():
                return supplier_choices[input_choice]
            elif google_choice is not None and input_choice == google_choice:
                try:
                    if worksheet.title == "Заказы (категории)": nm_column = 10
                    else: nm_column = 2
                    return list(map(int, google_work.get_columns(worksheet, 1, nm_column)))
                except ValueError: print("Проверьте значения списка номенклатур...")
            elif manual_choice is not None and input_choice == manual_choice:
                return ask_nm_list()
            elif input_choice == back_choice:
                global choice
                choice = 'wb'
                return None
            else: print("Неправильный выбор...")
        except ValueError:
            print("Неправильный выбор...")


def ask_ozon_input(worksheet, skip_suppliers=False, skip_nm=False):
    while True:
        all_choice = None
        supplier_choices = None
        google_choice = None
        manual_choice = None
        # ========= Printing choices =========
        choice_counter = 0
        if not skip_suppliers:
            choice_counter += 1
            all_choice = choice_counter
            print(f"\n{all_choice} - Для всех")
            supplier_choices = dict()
            for supplier in ozon_info.all_suppliers():
                choice_counter += 1
                print(f'{choice_counter} - {ozon_info.supplier_name(supplier)}')
                supplier_choices[choice_counter] = supplier
        if not skip_nm:
            choice_counter += 1
            google_choice = choice_counter
            print(f'{google_choice} - Взять список номенклатур из таблицы \"{worksheet.title}\"')
            choice_counter += 1
            manual_choice = choice_counter
            print(f'{manual_choice} - Ввести список номенклатур')
        back_choice = choice_counter + 1
        print(f'{back_choice} - Назад')
        # ============= Selection =============
        try:
            input_choice = int(input("Выбор: ").strip())
            if all_choice is not None and input_choice == all_choice:
                return ozon_info.all_suppliers()
            elif supplier_choices is not None and input_choice in supplier_choices.keys():
                return supplier_choices[input_choice]
            elif google_choice is not None and input_choice == google_choice:
                try:
                    if worksheet.title == "Заказы (категории)": sku_column = 11
                    else: sku_column = 2
                    return list(map(int, google_work.get_columns(worksheet, 1, sku_column)))
                except ValueError: print("Проверьте значения списка номенклатур...")
            elif manual_choice is not None and input_choice == manual_choice:
                return ask_nm_list()
            elif input_choice == back_choice:
                global choice
                choice = 'wb'
                return None
            else: print("Неправильный выбор...")
        except ValueError:
            print("Неправильный выбор...")


def get_int_column(worksheet, header, column_number, keep_lenght=True):
    column = google_work.get_columns(worksheet, header, column_number)
    int_values = list()
    for item in column:
        try:
            item = sub(r"[^0-9]", '', item)
            int_values.append(int(item))
        except ValueError:
            if keep_lenght: int_values.append(0)
    return int_values


def ask_week_count():
    while True:
        try: return int(input("Введите количество недель: ").strip())
        except: print("Неправильный выбор...")


if __name__ == '__main__':
    # ================== начало диалога ==================
    while True:
        if choice == 'start': ask_start()
        elif choice == 'wb': ask_wb()
        elif choice == 'ozon': ask_ozon()
        elif choice == 'wb_all_day_reports':
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'динамика, шт')
            input_data = wb_info.all_suppliers()
            start_date = str(date.today() - timedelta(days=7))
            orders_table = wb_analytics.orders_count(input_data, start_date)
            google_work.insert_table(worksheet, orders_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'динамика, руб')
            orders_table = wb_analytics.orders_value(input_data, start_date)
            google_work.insert_table(worksheet, orders_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'заказы общие')
            categories_list = google_work.get_columns(worksheet, 1, 10)
            orders_table = wb_analytics.orders_category(input_data, start_date, categories_list)
            google_work.clear(worksheet, 'A:I')
            google_work.insert_table(worksheet, orders_table, replace=False)
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'заказы топ 500')
            categories_list = google_work.get_columns(worksheet, 1, 10)
            input_data = get_int_column(worksheet, 1, 11)
            orders_table = wb_analytics.orders_category(input_data, start_date, categories_list)
            google_work.clear(worksheet, 'A:I')
            google_work.insert_table(worksheet, orders_table, replace=False)
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'новинки')
            categories_list = google_work.get_columns(worksheet, 1, 10)
            input_data = get_int_column(worksheet, 1, 11)
            orders_table = wb_analytics.orders_category(input_data, start_date, categories_list)
            google_work.clear(worksheet, 'A:I')
            google_work.insert_table(worksheet, orders_table, replace=False)
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'все категории')
            input_data = wb_info.all_suppliers()
            orders_table = wb_analytics.orders_category(input_data, start_date)
            google_work.clear(worksheet, 'A:I')
            google_work.insert_table(worksheet, orders_table, replace=False)
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'День')
            input_data = wb_info.all_suppliers()
            start_date = str(date.today() - timedelta(days=8))
            report_table = wb_analytics.report(input_data, start_date)
            google_special.day_report(worksheet, report_table)
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'Неделя')
            start_date = str(info.current_monday(skip_one=True))
            report_table = wb_analytics.report(input_data, start_date)
            google_special.week_report(worksheet, report_table)
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'Месяц')
            start_date = str(info.current_month_start_date(skip_one=True))
            report_table = wb_analytics.report(input_data, start_date)
            google_special.month_report(worksheet, report_table)
            choice = 'start'
        elif choice == 'wb_all_week_reports':
            input_data = wb_info.all_suppliers()
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'проц выкуп арт-размер')
            buyout_table = wb_analytics.buyout_percent_size(input_data)
            google_work.insert_table(worksheet, buyout_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'проц выкуп арт-цвет')
            buyout_table = wb_analytics.buyout_percent_color(input_data)
            google_work.insert_table(worksheet, buyout_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'проц выкуп арт')
            buyout_table = wb_analytics.buyout_percent_article(input_data)
            google_work.insert_table(worksheet, buyout_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'проц выкуп предмет')
            buyout_table = wb_analytics.buyout_percent_category(input_data)
            google_work.insert_table(worksheet, buyout_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'рент расчет')
            profit_table = wb_analytics.profit(input_data)
            google_work.insert_table(worksheet, profit_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'рент арт-размер')
            profit_table = wb_analytics.profit_size(input_data)
            google_work.insert_table(worksheet, profit_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'рент арт-цвет')
            profit_table = wb_analytics.profit_color(input_data)
            google_work.insert_table(worksheet, profit_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'рент арт')
            profit_table = wb_analytics.profit_article(input_data)
            google_work.insert_table(worksheet, profit_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'рент предмет')
            profit_table = wb_analytics.profit_category(input_data)
            google_work.insert_table(worksheet, profit_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'рент недели')
            profit_table = wb_analytics.profit_compare(input_data)
            google_work.insert_table(worksheet, profit_table, replace=True)
            choice = 'start'
        elif choice == 'wb_all_analytics':
            start_date = str(date.today() - timedelta(days=6))
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Категории')
            input_data = get_int_column(worksheet, 1, 2)
            categories_table = wb_analytics.categories(input_data, start_date)
            google_work.insert_table(worksheet, categories_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Позиции')
            input_data = get_int_column(worksheet, 1, 2)
            positions_table = wb_analytics.positions(input_data, start_date)
            google_work.insert_table(worksheet, positions_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Остатки')
            input_data = wb_info.all_suppliers()
            stocks_table = wb_analytics.stocks(input_data)
            google_work.insert_table(worksheet, stocks_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Отзывы')
            input_data = wb_info.all_suppliers()
            feedbacks_table = wb_analytics.feedbacks(input_data)
            google_work.insert_table(worksheet, feedbacks_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Отгрузка')
            input_data = wb_info.all_suppliers()
            shipments_table = wb_analytics.shipments(input_data)
            google_work.insert_table(worksheet, shipments_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Выручка')
            categories_list = google_work.get_columns(worksheet, 2, 1)
            revenue_table = wb_analytics.categories_revenue(categories_list, start_date)
            google_work.insert_table(worksheet, revenue_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Тренды')
            trends_table = wb_analytics.trends(start_date)
            google_work.insert_table(worksheet, trends_table, replace=True)
            choice = 'wb'
        elif choice == 'ozon_all_day_reports':
            worksheet = google_work.open_sheet(info.google_key('ozon_day_reports'), 'День')
            input_data = ozon_info.all_suppliers()
            start_date = str(date.today() - timedelta(days=8))
            report_table = ozon_analytics.report(input_data, start_date)
            google_special.day_report(worksheet, report_table)
            worksheet = google_work.open_sheet(info.google_key('ozon_day_reports'), 'Неделя')
            input_data = ozon_info.all_suppliers()
            start_date = str(info.current_monday(skip_one=True))
            report_table = ozon_analytics.report(input_data, start_date)
            google_special.week_report(worksheet, report_table)
            worksheet = google_work.open_sheet(info.google_key('ozon_day_reports'), 'Месяц')
            input_data = ozon_info.all_suppliers()
            start_date = str(info.current_month_start_date(skip_one=True))
            report_table = ozon_analytics.report(input_data, start_date)
            google_special.month_report(worksheet, report_table)
            worksheet = google_work.open_sheet(info.google_key('ozon_day_reports'), 'динамика шт.')
            input_data = ozon_info.all_suppliers()
            start_date = str(date.today() - timedelta(days=7))
            orders_table = ozon_analytics.orders_count(input_data, start_date)
            google_work.insert_table(worksheet, orders_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('ozon_day_reports'), 'динамика руб.')
            orders_table = ozon_analytics.orders_value(input_data, start_date)
            google_work.insert_table(worksheet, orders_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('ozon_day_reports'), 'заказы общие')
            categories_list = google_work.get_columns(worksheet, 1, 10)
            orders_table = ozon_analytics.orders_category(input_data, start_date, categories_list)
            google_work.clear(worksheet, 'A:I')
            google_work.insert_table(worksheet, orders_table, replace=False)
            worksheet = google_work.open_sheet(info.google_key('ozon_day_reports'), 'все категории')
            orders_table = ozon_analytics.orders_category(input_data, start_date)
            google_work.insert_table(worksheet, orders_table, replace=True)
            choice = 'start'
        elif choice == 'ozon_all_analytics':
            worksheet = google_work.open_sheet(info.google_key('ozon_analytics'), 'Позиции')
            input_data = get_int_column(worksheet, 1, 2)
            positions_table = ozon_analytics.positions(input_data)
            google_work.insert_table(worksheet, positions_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('ozon_analytics'), 'Категории')
            input_data = get_int_column(worksheet, 1, 2)
            categories_table = ozon_analytics.categories(input_data)
            google_work.insert_table(worksheet, categories_table, replace=True)
            worksheet = google_work.open_sheet(info.google_key('ozon_analytics'), 'Остатки')
            input_data = ozon_info.all_suppliers()
            old_stocks_columns = google_work.get_columns(worksheet, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
            stocks_table = ozon_analytics.stocks(input_data, old_stocks_columns)
            google_work.insert_table(worksheet, stocks_table, replace=True)
            choice = 'start'
        elif choice == 'wb_categories':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Категории')
            input_data = ask_wb_input(worksheet)
            if choice == 'start': continue
            start_date = ask_start_date()
            if choice == 'start': continue
            categories_table = wb_analytics.categories(input_data, start_date)
            google_work.insert_table(worksheet, categories_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_positions':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Позиции')
            input_data = ask_wb_input(worksheet)
            if choice == 'start': continue
            start_date = ask_start_date()
            if choice == 'start': continue
            positions_table = wb_analytics.positions(input_data, start_date)
            google_work.insert_table(worksheet, positions_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_max_categories':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Категории макс')
            start_date = str(date.today() - timedelta(days=7))
            max_categories_table = wb_analytics.max_categories(start_date)
            google_work.insert_table(worksheet, max_categories_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_trends':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Тренды')
            start_date = ask_start_date()
            if choice == 'start': continue
            trends_table = wb_analytics.trends(start_date)
            google_work.insert_table(worksheet, trends_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_stocks':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Остатки')
            input_data = ask_wb_input(worksheet)
            if choice == 'start': continue
            stocks_table = wb_analytics.stocks(input_data)
            google_work.insert_table(worksheet, stocks_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_feedbacks':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Отзывы')
            input_data = ask_wb_input(worksheet)
            if choice == 'start': continue
            feedbacks_table = wb_analytics.feedbacks(input_data)
            google_work.insert_table(worksheet, feedbacks_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_shipments':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Отгрузка')
            input_data = ask_wb_input(worksheet, skip_nm=True)
            if choice == 'start': continue
            shipments_table = wb_analytics.shipments(input_data)
            google_work.insert_table(worksheet, shipments_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_categories_revenue':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Выручка')
            categories_list = google_work.get_columns(worksheet, 2, 1)
            start_date = ask_start_date()
            if choice == 'start': continue
            revenue_table = wb_analytics.categories_revenue(categories_list, start_date)
            google_work.insert_table(worksheet, revenue_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_orders_count':
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'динамика, шт')
            input_data = wb_info.all_suppliers()
            start_date = ask_start_date()
            if choice == 'start': continue
            orders_table = wb_analytics.orders_count(input_data, start_date)
            google_work.insert_table(worksheet, orders_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_orders_value':
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'динамика, руб')
            input_data = wb_info.all_suppliers()
            start_date = ask_start_date()
            if choice == 'start': continue
            orders_table = wb_analytics.orders_value(input_data, start_date)
            google_work.insert_table(worksheet, orders_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_orders_category_all':
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'заказы общие')
            input_data = wb_info.all_suppliers()
            start_date = ask_start_date()
            if choice == 'start': continue
            categories_list = google_work.get_columns(worksheet, 1, 10)
            orders_table = wb_analytics.orders_category(input_data, start_date, categories_list)
            google_work.clear(worksheet, 'A:I')
            google_work.insert_table(worksheet, orders_table, replace=False)
            choice = 'wb'
        elif choice == 'wb_orders_category_500':
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'заказы топ 500')
            categories_list = google_work.get_columns(worksheet, 1, 10)
            input_data = list(map(int, google_work.get_columns(worksheet, 1, 11)))
            start_date = ask_start_date()
            if choice == 'start': continue
            orders_table = wb_analytics.orders_category(input_data, start_date, categories_list)
            google_work.clear(worksheet, 'A:I')
            google_work.insert_table(worksheet, orders_table, replace=False)
            choice = 'wb'
        elif choice == 'wb_orders_category_all_categories':
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'все категории')
            input_data = wb_info.all_suppliers()
            start_date = ask_start_date()
            if choice == 'start': continue
            orders_table = wb_analytics.orders_category(input_data, start_date)
            google_work.clear(worksheet, 'A:I')
            google_work.insert_table(worksheet, orders_table, replace=False)
            choice = 'wb'
        elif choice == 'wb_orders_category_new':
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'новинки')
            categories_list = google_work.get_columns(worksheet, 1, 10)
            input_data = list(map(int, google_work.get_columns(worksheet, 1, 11)))
            start_date = ask_start_date()
            if choice == 'start': continue
            orders_table = wb_analytics.orders_category(input_data, start_date, categories_list)
            google_work.clear(worksheet, 'A:I')
            google_work.insert_table(worksheet, orders_table, replace=False)
            choice = 'wb'
        elif choice == 'wb_day_report':
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'День')
            input_data = wb_info.all_suppliers()
            start_date = str(date.today() - timedelta(days=8))
            report_table = wb_analytics.report(input_data, start_date)
            google_special.day_report(worksheet, report_table)
            choice = 'wb'
        elif choice == 'wb_week_report':
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'Неделя')
            input_data = wb_info.all_suppliers()
            start_date = str(info.current_monday(skip_one=True))
            report_table = wb_analytics.report(input_data, start_date)
            google_special.week_report(worksheet, report_table)
            choice = 'wb'
        elif choice == 'wb_month_report':
            worksheet = google_work.open_sheet(info.google_key('wb_day_reports'), 'Месяц')
            input_data = wb_info.all_suppliers()
            start_date = str(info.current_month_start_date(skip_one=True))
            report_table = wb_analytics.report(input_data, start_date)
            google_special.month_report(worksheet, report_table)
            choice = 'wb'
        elif choice == 'wb_buyout_percent_size':
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'проц выкуп арт-размер')
            input_data = wb_info.all_suppliers()
            buyout_table = wb_analytics.buyout_percent_size(input_data)
            google_work.insert_table(worksheet, buyout_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_buyout_percent_color':
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'проц выкуп арт-цвет')
            input_data = wb_info.all_suppliers()
            buyout_table = wb_analytics.buyout_percent_color(input_data)
            google_work.insert_table(worksheet, buyout_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_buyout_percent_article':
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'проц выкуп арт')
            input_data = wb_info.all_suppliers()
            buyout_table = wb_analytics.buyout_percent_article(input_data)
            google_work.insert_table(worksheet, buyout_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_buyout_percent_category':
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'проц выкуп предмет')
            input_data = wb_info.all_suppliers()
            buyout_table = wb_analytics.buyout_percent_category(input_data)
            google_work.insert_table(worksheet, buyout_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_profit':
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'рент расчет')
            input_data = wb_info.all_suppliers()
            profit_table = wb_analytics.profit(input_data)
            google_work.insert_table(worksheet, profit_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_profit_size':
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'рент арт-размер')
            input_data = wb_info.all_suppliers()
            profit_table = wb_analytics.profit_size(input_data)
            google_work.insert_table(worksheet, profit_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_profit_color':
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'рент арт-цвет')
            input_data = wb_info.all_suppliers()
            profit_table = wb_analytics.profit_color(input_data)
            google_work.insert_table(worksheet, profit_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_profit_article':
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'рент арт')
            input_data = wb_info.all_suppliers()
            profit_table = wb_analytics.profit_article(input_data)
            google_work.insert_table(worksheet, profit_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_profit_category':
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'рент предмет')
            input_data = wb_info.all_suppliers()
            profit_table = wb_analytics.profit_category(input_data)
            google_work.insert_table(worksheet, profit_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_profit_compare':
            worksheet = google_work.open_sheet(info.google_key('wb_week_reports'), 'рент недели')
            input_data = wb_info.all_suppliers()
            weeks = ask_week_count()
            profit_table = wb_analytics.profit_compare(input_data, weeks)
            google_work.insert_table(worksheet, profit_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_consolidated':
            worksheet = google_work.open_sheet(info.google_key('wb_consolidated'), 'Главная')
            consolidated_table, notes = wb_analytics.consolidated()
            google_work.clear(worksheet, ['B:T', 'V:V', 'X:X'])
            worksheet.update(consolidated_table, value_input_option='USER_ENTERED')
            google_work.update_notes(worksheet, start_row=2, start_column=14, note_rows=notes)
            choice = 'wb'
# ==============================================================================================================
        elif choice == 'ozon_positions':
            worksheet = google_work.open_sheet(info.google_key('ozon_analytics'), 'Позиции')
            input_data = get_int_column(worksheet, 1, 2)
            positions_table = ozon_analytics.positions(input_data)
            google_work.insert_table(worksheet, positions_table, replace=True)
            choice = 'ozon'
        elif choice == 'ozon_categories':
            worksheet = google_work.open_sheet(info.google_key('ozon_analytics'), 'Категории')
            input_data = get_int_column(worksheet, 1, 2)
            categories_table = ozon_analytics.categories(input_data)
            google_work.insert_table(worksheet, categories_table, replace=True)
            choice = 'ozon'
        elif choice == 'ozon_stocks':
            worksheet = google_work.open_sheet(info.google_key('ozon_analytics'), 'Остатки')
            input_data = ozon_info.all_suppliers()
            old_stocks_columns = google_work.get_columns(worksheet, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
            stocks_table = ozon_analytics.stocks(input_data, old_stocks_columns)
            google_work.insert_table(worksheet, stocks_table, replace=True)
            choice = 'ozon'
        elif choice == 'ozon_day_report':
            worksheet = google_work.open_sheet(info.google_key('ozon_day_reports'), 'День')
            input_data = ozon_info.all_suppliers()
            start_date = str(date.today() - timedelta(days=8))
            report_table = ozon_analytics.report(input_data, start_date)
            google_special.day_report(worksheet, report_table)
            choice = 'ozon'
        elif choice == 'ozon_week_report':
            worksheet = google_work.open_sheet(info.google_key('ozon_day_reports'), 'Неделя')
            input_data = ozon_info.all_suppliers()
            start_date = str(info.current_monday(skip_one=True))
            report_table = ozon_analytics.report(input_data, start_date)
            google_special.week_report(worksheet, report_table)
            choice = 'ozon'
        elif choice == 'ozon_month_report':
            worksheet = google_work.open_sheet(info.google_key('ozon_day_reports'), 'Месяц')
            input_data = ozon_info.all_suppliers()
            start_date = str(info.current_month_start_date(skip_one=True))
            report_table = ozon_analytics.report(input_data, start_date)
            google_special.month_report(worksheet, report_table)
            choice = 'ozon'
        elif choice == 'ozon_orders_count':
            worksheet = google_work.open_sheet(info.google_key('ozon_day_reports'), 'динамика шт.')
            input_data = ozon_info.all_suppliers()
            start_date = str(date.today() - timedelta(days=7))
            orders_table = ozon_analytics.orders_count(input_data, start_date)
            google_work.insert_table(worksheet, orders_table, replace=True)
            choice = 'ozon'
        elif choice == 'ozon_orders_value':
            worksheet = google_work.open_sheet(info.google_key('ozon_day_reports'), 'динамика руб.')
            input_data = ozon_info.all_suppliers()
            start_date = str(date.today() - timedelta(days=7))
            orders_table = ozon_analytics.orders_value(input_data, start_date)
            google_work.insert_table(worksheet, orders_table, replace=True)
            choice = 'ozon'
        elif choice == 'ozon_orders_category_all':
            worksheet = google_work.open_sheet(info.google_key('ozon_day_reports'), 'заказы общие')
            input_data = ozon_info.all_suppliers()
            categories_list = google_work.get_columns(worksheet, 1, 10)
            start_date = str(date.today() - timedelta(days=7))
            orders_table = ozon_analytics.orders_category(input_data, start_date, categories_list)
            google_work.clear(worksheet, 'A:I')
            google_work.insert_table(worksheet, orders_table, replace=False)
            choice = 'ozon'
        elif choice == 'ozon_orders_category_all_categories':
            worksheet = google_work.open_sheet(info.google_key('ozon_day_reports'), 'все категории')
            input_data = ozon_info.all_suppliers()
            start_date = str(date.today() - timedelta(days=7))
            orders_table = ozon_analytics.orders_category(input_data, start_date)
            google_work.insert_table(worksheet, orders_table, replace=True)
            choice = 'ozon'
        else: raise KeyError(f"Check menu choices - {choice} have not found")
