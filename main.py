from datetime import date, timedelta
from re import search

import modules.google_work as google_work
import modules.mpstats as mpstats
import modules.wildberries as wildberries
import modules.files as files
import modules.info as info


choice = 'start'


def ask_start():
    """Present main actions to the user."""
    print("\n========================================")
    print("=========== Программа для WB ===========")
    print("1 - Обновить все отчеты (в работе)")
    print("2 - Отчет по категориям")
    print("3 - Отчет по позициям")
    print("4 - Отчет по остаткам")
    print("5 - Отчет по отзывам")
    print("6 - Отчет по заказам (кол-во)")
    print("7 - Отчет по заказам (сумма)")
    print("8 - Отчет по заказам (категории)")
    global choice
    choice = input("Выбор: ")
    if choice.strip() == '1': choice = 'all_reports'
    elif choice.strip() == '2': choice = 'categories'
    elif choice.strip() == '3': choice = 'positions'
    elif choice.strip() == '4': choice = 'stocks'
    elif choice.strip() == '5': choice = 'feedbacks'
    elif choice.strip() == '6': choice = 'orders_count'
    elif choice.strip() == '7': choice = 'orders_value'
    elif choice.strip() == '8': choice = 'orders_category'
    else:
        choice = 'start'
        print("Неправильный выбор...")


def ask_start_date():
    """Ask user about start date.

    :return: date string 'YYYY-MM-DD'
    :rtype: str
    """
    while(True):
        print("\n1 - За последние 7 дней")
        print("2 - За последние 30 дней")
        print("3 - Свой вариант")
        print("4 - В начало")
        day_choice = input("Выбор: ")
        if day_choice.strip() == '1':
            start_date = str(date.today() - timedelta(days=7))
            return start_date
        elif day_choice.strip() == '2':
            start_date = str(date.today() - timedelta(days=30))
            return start_date
        elif day_choice.strip() == '3':
            while(True):
                start_date = input("Введите дату (YYYY-MM-DD): ").strip()
                if search(r'\d\d\d\d\-\d\d\-\d\d', start_date):
                    return start_date
                else: print("Неправильная дата...")
        elif day_choice.strip() == '4':
            global choice
            choice = 'start'
            return None
        else: print("Неправильный выбор...")


def ask_nm_list():
    print('Введите список номенклатур (Enter нужно нажать два раза)')
    nm_list = list(iter(input, ""))
    return nm_list


def ask_input(worksheet, skip_suppliers=False, skip_nm=False):
    while (True):
        all_choice = None
        supplier_choices = None
        google_choice = None
        manual_choice = None
        # ========= Printing choices =========
        choice_counter = 0
        if skip_suppliers == False:
            choice_counter += 1
            all_choice = choice_counter
            print(f"\n{all_choice} - Для всех")
            supplier_choices = dict()
            for supplier in info.all_suppliers():
                choice_counter += 1
                print(f'{choice_counter} - {info.supplier_name(supplier)}')
                supplier_choices[choice_counter] = supplier
        if skip_nm == False:
            choice_counter += 1
            google_choice = choice_counter
            print(f'{google_choice} - Взять список номенклатур из таблицы \"{worksheet.title}\"')
            choice_counter += 1
            manual_choice = choice_counter
            print(f'{manual_choice} - Ввести список номенклатур')
        back_choice = choice_counter + 1
        print(f'{back_choice} - В начало')
        # ============= Selection =============
        try:
            input_choice = int(input("Выбор: ").strip())
            if all_choice is not None and input_choice == all_choice:
                return info.all_suppliers()
            elif supplier_choices is not None and input_choice in supplier_choices.keys():
                return supplier_choices[input_choice]
            elif google_choice is not None and input_choice == google_choice:
                try: return list(map(int, google_work.get_columns(worksheet, 1, 2)))
                except ValueError: print("Проверьте значения списка номенклатур...")
            elif manual_choice is not None and input_choice == manual_choice:
                return ask_nm_list()
            elif input_choice == back_choice:
                global choice
                choice = 'start'
                return None
            else: print("Неправильный выбор...")
        except ValueError:
            print("Неправильный выбор...")

# ================== начало диалога ==================
if __name__ == '__main__':
    while(True):
        if choice == 'start': ask_start()
        # elif choice == 'all_reports':
        elif choice == 'categories':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Категории')
            input_data = ask_input(worksheet, skip_suppliers=True)
            if choice == 'start': continue
            start_date = ask_start_date()
            if choice == 'start': continue
            categories_table = mpstats.categories(input_data, start_date)
            google_work.insert_table(worksheet, categories_table, replace=True)
            choice = 'start'
        elif choice == 'positions':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Позиции')
            input_data = ask_input(worksheet)
            if choice == 'start': continue
            start_date = ask_start_date()
            if choice == 'start': continue
            positions_table = mpstats.positions(input_data, start_date)
            google_work.insert_table(worksheet, positions_table, replace=True)
            choice = 'start'
        elif choice == 'stocks':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Остатки')
            input_data = ask_input(worksheet, skip_nm=True)
            if choice == 'start': continue
            stocks_table = wildberries.stocks(input_data)
            google_work.insert_table(worksheet, stocks_table, replace=True)
            choice = 'start'
        elif choice == 'feedbacks':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Отзывы')
            input_data = ask_input(worksheet)
            if choice == 'start': continue
            feedbacks_table = wildberries.feedbacks(input_data)
            google_work.insert_table(worksheet, feedbacks_table, replace=True)
            choice = 'start'
        elif choice == 'orders_count':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Заказы (кол-во)')
            input_data = ask_input(worksheet, skip_nm=True)
            if choice == 'start': continue
            start_date = ask_start_date()
            if choice == 'start': continue
            orders_table = wildberries.orders_count(input_data, start_date)
            google_work.insert_table(worksheet, orders_table, replace=True)
            choice = 'start'
        elif choice == 'orders_value':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Заказы (сумма)')
            input_data = ask_input(worksheet, skip_nm=True)
            if choice == 'start': continue
            start_date = ask_start_date()
            if choice == 'start': continue
            orders_table = wildberries.orders_value(input_data, start_date)
            google_work.insert_table(worksheet, orders_table, replace=True)
            choice = 'start'
        elif choice == 'orders_category':
            worksheet = google_work.open_sheet(info.google_key('wb_analytics'), 'Заказы (категории)')
            input_data = ask_input(worksheet, skip_nm=True)
            if choice == 'start': continue
            start_date = ask_start_date()
            if choice == 'start': continue
            orders_table = wildberries.orders_category(input_data, start_date)
            google_work.insert_table(worksheet, orders_table, replace=True)
            choice = 'start'
        else: raise KeyError(f"Check menu choices - {choice} have not found")
