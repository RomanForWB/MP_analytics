from datetime import date, timedelta
from re import search

import modules.google_work as google_work
import modules.mpstats as mpstats
import modules.wildberries as wildberries
import modules.files as files

supplier_identifiers = {"ИП Марьина А.А.": "maryina",
                        "ИП Туманян А.А.": "tumanyan",
                        "ООО НЬЮЭРАМЕДИА": "neweramedia",
                        "ИП Ахметов В.Р.": "ahmetov",
                        "ИП Фурсов И.Н.": "fursov"}
supplier_names = {value: key for key, value in supplier_identifiers.items()}

choice = 'start'
def ask_start():
    """Основное меню программы."""
    print("\n========================================")
    print("=========== Программа для WB ===========")
    print("1 - Обновить все отчеты (в работе)")
    print("2 - Отчет по категориям")
    print("3 - Отчет по позициям (долго)")
    print("4 - Отчет по остаткам")
    print("5 - Отчет по отзывам")
    global choice
    choice = input("Выбор: ")
    if choice.strip() == '1': choice = 'all_reports'
    elif choice.strip() == '2': choice = 'categories'
    elif choice.strip() == '3': choice = 'positions'
    elif choice.strip() == '4': choice = 'balance'
    elif choice.strip() == '5': choice = 'feedbacks'
    else:
        choice = 'start'
        print("Неправильный выбор...")
def ask_sku_list(worksheet):
    """Спрашивает у пользователя про список sku

    :param worksheet: worksheet из gspread (использовать google_work.open_sheet())
    :return: список SKU в формате [00000000, 00000000...]
    """
    while(True):
        print("\n1 - Взять список SKU из Google таблицы")
        print("2 - В начало")
        sku_list_choice = input("Выбор: ")
        if sku_list_choice.strip() == '1':
            sku_list = google_work.get_columns(worksheet, 1, 2)
            return sku_list
        elif sku_list_choice.strip() == '2':
            global choice
            choice = 'start'
            return None
        else: print("Неправильный выбор...")
def ask_day_period():
    """
    Спрашивает у пользователя про даты начала и конца
    :return: (start_date, end_date) даты в формате 'YYYY-MM-DD'
    """
    while(True):
        print("\n1 - За последние 7 дней")
        print("2 - За последние 30 дней")
        print("3 - Свой вариант")
        print("4 - В начало")
        day_choice = input("Выбор: ")
        if day_choice.strip() == '1':
            start_date = date.today() - timedelta(days=7)
            end_date = date.today()
            return start_date, end_date
        elif day_choice.strip() == '2':
            start_date = date.today() - timedelta(days=30)
            end_date = date.today()
            return start_date, end_date
        elif day_choice.strip() == '3':
            while(True):
                start_date = input("Введите дату начала периода (YYYY-MM-DD): ").strip()
                end_date = input("Введите дату конца периода (YYYY-MM-DD): ").strip()
                if search(r'\d\d\d\d\-\d\d\-\d\d', start_date) \
                and search(r'\d\d\d\d\-\d\d\-\d\d', end_date):
                    return start_date, end_date
                else: print("Неправильные даты...")
        elif day_choice.strip() == '4':
            global choice
            choice = 'start'
            return None, None
        else: print("Неправильный выбор...")
def ask_start_day():
    """
    Спрашивает у пользователя про дату начала
    :return: start_date дату в формате 'YYYY-MM-DD'
    """
    while(True):
        print("\n1 - За последние 7 дней")
        print("2 - За последние 30 дней")
        print("3 - Свой вариант")
        print("4 - В начало")
        day_choice = input("Выбор: ")
        if day_choice.strip() == '1':
            start_date = date.today() - timedelta(days=7)
            return start_date
        elif day_choice.strip() == '2':
            start_date = date.today() - timedelta(days=30)
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
def ask_supplier():
    while (True):
        print("\n1 - Для всех")
        supplier_number = 1
        supplier_choices = dict()
        for supplier in supplier_identifiers.keys():
            supplier_number += 1
            supplier_choices[supplier_number] = supplier
            print(f'{supplier_number} - {supplier}')
        print(f'{supplier_number + 1} - В начало')
        try:
            choice_number = int(input("Выбор: ").strip())
            if choice_number == 1: return list(supplier_identifiers.values())
            elif choice_number == (supplier_number + 1):
                global choice
                choice = 'start'
                return None
            else: return supplier_identifiers[supplier_choices[choice_number]]
        except ValueError:
            print("Неправильный выбор...")

# ================== начало диалога ==================
if __name__ == '__main__':
    while(True):
        if choice == 'start': ask_start()
        # elif choice == 'all_reports':
        elif choice == 'categories':
            worksheet = google_work.open_sheet(files.get_google_key('wb_analytics'), 'Категории')
            sku_list = ask_sku_list(worksheet)
            if choice == 'start': continue
            start_date, end_date = ask_day_period()
            if choice == 'start': continue
            items_dict = mpstats.fetch_categories_and_positions(sku_list, start_date, end_date)
            categories_dict = wildberries.fetch_simple_category_and_brand(sku_list)
            category_table = mpstats.categories(items_dict, categories_dict)
            google_work.clear(worksheet, 'B:ZZ')
            worksheet.update('B1', category_table)
            print(f"\nТаблица успешно обновлена - https://docs.google.com/spreadsheets/d/{files.get_google_key('wb_analytics')}")
            choice = 'start'
        elif choice == 'positions':
            worksheet = google_work.open_sheet(files.get_google_key('wb_analytics'), 'Позиции')
            sku_list = ask_sku_list(worksheet)
            if choice == 'start': continue
            start_date, end_date = ask_day_period()
            if choice == 'start': continue
            items_dict = mpstats.fetch_categories_and_positions(sku_list, start_date, end_date)
            categories_dict = wildberries.get_category_and_brand(sku_list)
            position_table = mpstats.positions(items_dict, categories_dict)
            google_work.clear(worksheet, 'B:ZZ')
            worksheet.update('B1', position_table)
            print(f"\nТаблица успешно обновлена - https://docs.google.com/spreadsheets/d/{files.get_google_key('wb_analytics')}")
            choice = 'start'
        elif choice == 'balance':
            worksheet = google_work.open_sheet(files.get_google_key('wb_analytics'), 'Остатки')
            company_keys = {name: files.get_wb_key('x64', supplier) for supplier, name in supplier_names.items()}
            items_dict = wildberries.fetch_all_stocks(company_keys, date.today()-timedelta(days=7))
            balance_table = wildberries.all_stocks(items_dict)
            google_work.clear(worksheet)
            worksheet.update(balance_table)
            print(f"\nТаблица успешно обновлена - https://docs.google.com/spreadsheets/d/{files.get_google_key('wb_analytics')}")
            choice = 'start'
        elif choice == 'feedbacks':
            worksheet = google_work.open_sheet(files.get_google_key('wb_analytics'), 'Отзывы')
            supplier = ask_supplier()
            if choice == 'start': continue
            feedbacks_table = wildberries.feedbacks(supplier)
            google_work.clear(worksheet)
            worksheet.update(feedbacks_table)
            print(f"\nТаблица успешно обновлена - https://docs.google.com/spreadsheets/d/{files.get_google_key('wb_analytics')}")
            choice = 'start'
        else: raise KeyError(f"Check menu choices - {choice} have not found")
