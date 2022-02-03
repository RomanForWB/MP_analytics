from datetime import date, timedelta
from re import search

import modules.google_work as google_work
import modules.mpstats as mpstats
import modules.wildberries as wildberries

GOOGLE_WB_KEY = '1i639nTdBNRp3TyDvA1qPT-QP0RdNaJiwkxBIOPMZoLs'
choice = 'start'

def ask_start():
    """
    Основное меню программы
    """
    print("\n========================================")
    print("=========== Программа для WB ===========")
    print("1 - Отчет по категориям и позициям")
    print("2 - Отчет по категориям")
    print("3 - Отчет по позициям")
    print("4 - Отчет по остаткам")
    global choice
    choice = input("Выбор: ")
    if choice.strip() == '1': choice = 'categories_and_positions'
    elif choice.strip() == '2': choice = 'categories'
    elif choice.strip() == '3': choice = 'positions'
    elif choice.strip() == '4': choice = 'balance'
    else:
        choice = 'start'
        print("Неправильный выбор...")
def ask_sku_list(worksheet):
    """
    Спрашивает у пользователя про список sku
    :param worksheet: worksheet из gspread (использовать google_work.open_sheet())
    :return: список SKU в формате [00000000, 00000000...]
    """
    while(True):
        print("\n1 - Взять список SKU из Google таблицы")
        print("2 - В начало")
        sku_list_choice = input("Выбор: ")
        if sku_list_choice.strip() == '1':
            supply_sku_list, sku_list = google_work.get_columns(worksheet, 1, 1, 2)
            supply_sku_dict = {sku_list[i]: supply_sku_list[i] for i in range(len(sku_list))}
            if len(supply_sku_dict) < len(sku_list):
                print(f'Всего записей: {len(sku_list)}')
                print(f'Найдено {len(sku_list)-len(supply_sku_dict)} повторяющихся записей...')
                sku_list = sorted(list(supply_sku_dict.keys()))
                supply_sku_list = [[supply_sku_dict[sku]] for sku in sku_list]
                worksheet.update('A2', supply_sku_list)
                return sku_list
            else: return sorted(sku_list)
        elif sku_list_choice.strip() == '2':
            global choice
            choice = 'start'
            break
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

# ================== начало диалога ==================
while(True):
    if choice == 'start': ask_start()
    elif choice == 'categories':
        worksheet = google_work.open_sheet(GOOGLE_WB_KEY, 'Категории')
        sku_list = ask_sku_list(worksheet)
        if choice == 'start': continue
        start_date, end_date = ask_day_period()
        if choice == 'start': continue
        items_dict = mpstats.fetch_categories_and_positions(sku_list, start_date, end_date)
        categories_dict = wildberries.get_category_and_brand(sku_list)
        category_table = mpstats.categories(items_dict, categories_dict)
        google_work.clear(worksheet, 'B:ZZ')
        worksheet.update('B1', category_table)
        print(f"\nТаблица успешно обновлена - https://docs.google.com/spreadsheets/d/{GOOGLE_WB_KEY}")
        choice = 'start'
    elif choice == 'positions':
        worksheet = google_work.open_sheet(GOOGLE_WB_KEY, 'Позиции')
        sku_list = ask_sku_list(worksheet)
        if choice == 'start': continue
        start_date, end_date = ask_day_period()
        if choice == 'start': continue
        items_dict = mpstats.fetch_categories_and_positions(sku_list, start_date, end_date)
        categories_dict = wildberries.get_category_and_brand(sku_list)
        position_table = mpstats.positions(items_dict, categories_dict)
        google_work.clear(worksheet, 'B:ZZ')
        worksheet.update('B1', position_table)
        print(f"\nТаблица успешно обновлена - https://docs.google.com/spreadsheets/d/{GOOGLE_WB_KEY}")
        choice = 'start'
    elif choice == 'categories_and_positions':
        worksheet = google_work.open_sheet(GOOGLE_WB_KEY, 'Категории')
        sku_list = ask_sku_list(worksheet)
        if choice == 'start': continue
        start_date, end_date = ask_day_period()
        if choice == 'start': continue
        items_dict = mpstats.fetch_categories_and_positions(sku_list, start_date, end_date)
        categories_dict = wildberries.get_category_and_brand(sku_list)
        category_table = mpstats.categories(items_dict, categories_dict)
        google_work.clear(worksheet, 'B:ZZ')
        worksheet.update('B1', category_table)
        print(f"\nТаблица успешно обновлена - https://docs.google.com/spreadsheets/d/{GOOGLE_WB_KEY}")
        worksheet = google_work.open_sheet(GOOGLE_WB_KEY, 'Позиции')
        position_table = mpstats.positions(items_dict, categories_dict)
        google_work.clear(worksheet, 'B:ZZ')
        worksheet.update('B1', position_table)
        print(f"\nТаблица успешно обновлена - https://docs.google.com/spreadsheets/d/{GOOGLE_WB_KEY}")
        choice = 'start'
    elif choice == 'balance':
        worksheet = google_work.open_sheet(GOOGLE_WB_KEY, 'Остатки')
        sku_list = ask_sku_list(worksheet)
        if choice == 'start': continue
        start_date, end_date = ask_day_period()
        if choice == 'start': continue
        items_dict = mpstats.fetch_orders_and_balance(sku_list, start_date, end_date)
        categories_dict = wildberries.get_category_and_brand(sku_list)
        balance_table = mpstats.balance(items_dict, categories_dict)
        google_work.clear(worksheet, 'B:ZZ')
        worksheet.update('B1', balance_table)
        print(f"\nТаблица успешно обновлена - https://docs.google.com/spreadsheets/d/{GOOGLE_WB_KEY}")
        choice = 'start'
    else: raise KeyError(f"Check menu choices - {choice} have not found")
