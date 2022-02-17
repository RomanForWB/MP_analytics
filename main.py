from datetime import date, timedelta
from re import search

import modules.google_work as google_work
import modules.info as info
import modules.wildberries.mpstats as wb_mpstats
import modules.wildberries.analytics as wb_analytics
import modules.wildberries.info as wb_info
import modules.ozon.mpstats as ozon_mpstats
import modules.ozon.analytics as ozon_analytics
import modules.ozon.info as ozon_info


choice = 'start'


def ask_start():
    """Asking a marketplace."""
    print("\n=======================================")
    print("========== Торговая площадка ==========")
    print("1 - Wildberries")
    print("2 - Ozon")
    global choice
    choice = input("Выбор: ")
    if choice.strip() == '1': choice = 'wb'
    elif choice.strip() == '2': choice = 'ozon'
    else:
        choice = 'start'
        print("Неправильный выбор...")


def ask_wb():
    """Presents wildberries actions to the user."""
    print("\n=======================================")
    print("============ Wildberries ==============")
    print("1 - Обновить все отчеты (в работе)")
    print("2 - Отчет по категориям")
    print("3 - Отчет по позициям")
    print("4 - Отчет по остаткам")
    print("5 - Отчет по отзывам")
    print("6 - Отчет по заказам (кол-во)")
    print("7 - Отчет по заказам (сумма)")
    print("8 - Отчет по заказам (категории)")
    print("9 - В начало")
    global choice
    choice = input("Выбор: ")
    if choice.strip() == '1': choice = 'wb_reports'
    elif choice.strip() == '2': choice = 'wb_categories'
    elif choice.strip() == '3': choice = 'wb_positions'
    elif choice.strip() == '4': choice = 'wb_stocks'
    elif choice.strip() == '5': choice = 'wb_feedbacks'
    elif choice.strip() == '6': choice = 'wb_orders_count'
    elif choice.strip() == '7': choice = 'wb_orders_value'
    elif choice.strip() == '8': choice = 'wb_orders_category'
    elif choice.strip() == '9': choice = 'start'
    else:
        choice = 'wb'
        print("Неправильный выбор...")


def ask_ozon():
    """Presents ozon actions to the user."""
    print("\n=======================================")
    print("================ Ozon =================")
    print("1 - Обновить все отчеты (в работе)")
    print("2 - Отчет по категориям")
    print("3 - Отчет по позициям")
    print("4 - В начало")
    global choice
    choice = input("Выбор: ")
    if choice.strip() == '1': choice = 'ozon_reports'
    elif choice.strip() == '2': choice = 'ozon_categories'
    elif choice.strip() == '3': choice = 'ozon_positions'
    elif choice.strip() == '4': choice = 'start'
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
        if day_choice.strip() == '1':
            start_date = str(date.today() - timedelta(days=6))
            return start_date
        elif day_choice.strip() == '2':
            start_date = str(date.today() - timedelta(days=29))
            return start_date
        elif day_choice.strip() == '3':
            while(True):
                start_date = input("Введите дату (YYYY-MM-DD): ").strip()
                if search(r'\d\d\d\d\-\d\d\-\d\d', start_date):
                    return start_date
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


if __name__ == '__main__':
    # ================== начало диалога ==================
    while True:
        if choice == 'start': ask_start()
        elif choice == 'wb': ask_wb()
        elif choice == 'wb_categories':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Категории')
            input_data = ask_wb_input(worksheet)
            if choice == 'start': continue
            start_date = ask_start_date()
            if choice == 'start': continue
            categories_table = wb_mpstats.categories(input_data, start_date)
            google_work.insert_table(worksheet, categories_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_positions':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Позиции')
            input_data = ask_wb_input(worksheet)
            if choice == 'start': continue
            start_date = ask_start_date()
            if choice == 'start': continue
            positions_table = wb_mpstats.positions(input_data, start_date)
            google_work.insert_table(worksheet, positions_table, replace=True)
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
        elif choice == 'wb_orders_count':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Заказы (кол-во)')
            input_data = ask_wb_input(worksheet)
            if choice == 'start': continue
            start_date = ask_start_date()
            if choice == 'start': continue
            orders_table = wb_analytics.orders_count(input_data, start_date)
            google_work.insert_table(worksheet, orders_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_orders_value':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Заказы (сумма)')
            input_data = ask_wb_input(worksheet)
            if choice == 'start': continue
            start_date = ask_start_date()
            if choice == 'start': continue
            orders_table = wb_analytics.orders_value(input_data, start_date)
            google_work.insert_table(worksheet, orders_table, replace=True)
            choice = 'wb'
        elif choice == 'wb_orders_category':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Заказы (категории)')
            input_data = ask_wb_input(worksheet)
            if choice == 'start': continue
            start_date = ask_start_date()
            if choice == 'start': continue
            orders_table = wb_analytics.orders_category(input_data, start_date)
            google_work.clear(worksheet, 'A:I')
            google_work.insert_table(worksheet, orders_table, replace=False)
            choice = 'wb'
        elif choice == 'ozon': ask_ozon()
        elif choice == 'ozon_positions':
            worksheet = google_work.open_sheet(info.google_key('ozon_analytics'), 'Позиции')
            input_data = ask_ozon_input(worksheet)
            if choice == 'start': continue
            start_date = ask_start_date()
            if choice == 'start': continue
            positions_table = ozon_mpstats.positions(input_data, start_date)
            google_work.insert_table(worksheet, positions_table, replace=True)
            choice = 'ozon'
        elif choice == 'ozon_categories':
            worksheet = google_work.open_sheet(info.google_key('ozon_analytics'), 'Категории')
            input_data = ask_ozon_input(worksheet)
            if choice == 'start': continue
            start_date = ask_start_date()
            if choice == 'start': continue
            categories_table = ozon_mpstats.categories(input_data, start_date)
            google_work.insert_table(worksheet, categories_table, replace=True)
            choice = 'ozon'
        else: raise KeyError(f"Check menu choices - {choice} have not found")
