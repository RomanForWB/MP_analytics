from datetime import date, timedelta
from re import search

import modules.google_work as google_work
import modules.mpstats as mpstats
import modules.wildberries as wildberries

WILDBERRIES_SUPPLIER_KEYS = {'ИП Марьина А.А.' : 'MmY1ZTU0ZTUtN2E2NC00YmI5LTgwNTgtODU4MWVlZTRlNzVh',
                             'ИП Туманян А.А.' : 'OGY2MWFhYWEtMmJjYi00YzdkLWFjMDYtZDY1Y2FkMzFjZmUy',
                             'ООО НЬЮЭРАМЕДИА' : 'NmEyMWYyZTItNTNmZi00NjZkLWIwNTMtYTU1MTI0NzgwZTIw',
                             'ИП Ахметов В.Р.' : 'OWVhNTlhMTQtNjAwYi00ZmZkLTgzNGQtNzFlZTI1NTdmMGVi'}
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
    print("4 - Отчет по остаткам (с MPStats)")
    print("5 - Отчет по остаткам (с Wildberries)")
    print("6 - Отчет по отзывам")
    global choice
    choice = input("Выбор: ")
    if choice.strip() == '1': choice = 'categories_and_positions'
    elif choice.strip() == '2': choice = 'categories'
    elif choice.strip() == '3': choice = 'positions'
    elif choice.strip() == '4': choice = 'balance'
    elif choice.strip() == '5': choice = 'balance-wb'
    elif choice.strip() == '6': choice = 'feedbacks'
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
def ask_company():
    while (True):
        print("\n1 - Для всех")
        print("2 - ИП Марьина А.А.")
        print("3 - ИП Туманян А.А.")
        print("4 - ООО НЬЮЭРАМЕДИА")
        print("5 - ИП Ахметов В.Р.")
        print("6 - В начало")
        company_choice = input("Выбор: ")
        if company_choice.strip() == '1': return WILDBERRIES_SUPPLIER_KEYS
        if company_choice.strip() == '2': return {'ИП Марьина А.А.': WILDBERRIES_SUPPLIER_KEYS['ИП Марьина А.А.']}
        if company_choice.strip() == '3': return {'ИП Туманян А.А.': WILDBERRIES_SUPPLIER_KEYS['ИП Туманян А.А.']}
        if company_choice.strip() == '4': return {'ООО НЬЮЭРАМЕДИА': WILDBERRIES_SUPPLIER_KEYS['ООО НЬЮЭРАМЕДИА']}
        if company_choice.strip() == '5': return {'ИП Ахметов В.Р.': WILDBERRIES_SUPPLIER_KEYS['ИП Ахметов В.Р.']}
        elif company_choice.strip() == '6':
            global choice
            choice = 'start'
            return None
        else:
            print("Неправильный выбор...")
def ask_supplier():
    while (True):
        print("\n1 - Для всех")
        print("2 - ИП Марьина А.А.")
        print("3 - ИП Туманян А.А.")
        print("4 - ООО НЬЮЭРАМЕДИА")
        print("5 - ИП Ахметов В.Р.")
        print("6 - В начало")
        supplier_choice = input("Выбор: ")
        if supplier_choice.strip() == '1': return list(WILDBERRIES_SUPPLIER_KEYS.keys())
        if supplier_choice.strip() == '2': return 'ИП Марьина А.А.'
        if supplier_choice.strip() == '3': return 'ИП Туманян А.А.'
        if supplier_choice.strip() == '4': return 'ООО НЬЮЭРАМЕДИА'
        if supplier_choice.strip() == '5': return 'ИП Ахметов В.Р.'
        elif supplier_choice.strip() == '6':
            global choice
            choice = 'start'
            return None
        else:
            print("Неправильный выбор...")

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
        worksheet = google_work.open_sheet(GOOGLE_WB_KEY, 'Остатки с MPSTATS')
        sku_list = ask_sku_list(worksheet)
        if choice == 'start': continue
        start_date, end_date = ask_day_period()
        if choice == 'start': continue
        items_dict = mpstats.fetch_orders_and_balance(sku_list, start_date, end_date)
        categories_dict = wildberries.get_category_and_brand(sku_list)
        balance_table = mpstats.stocks(items_dict, categories_dict)
        google_work.clear(worksheet, 'B:ZZ')
        worksheet.update('B1', balance_table)
        print(f"\nТаблица успешно обновлена - https://docs.google.com/spreadsheets/d/{GOOGLE_WB_KEY}")
        choice = 'start'
    elif choice == 'balance-wb':
        worksheet = google_work.open_sheet(GOOGLE_WB_KEY, 'Остатки с WB')
        start_date = ask_start_day()
        if choice == 'start': continue
        company_keys = ask_company()
        if choice == 'start': continue
        items_dict = wildberries.fetch_all_stocks(company_keys, start_date)
        balance_table = wildberries.all_stocks(items_dict)
        google_work.clear(worksheet)
        worksheet.update(balance_table)
        print(f"\nТаблица успешно обновлена - https://docs.google.com/spreadsheets/d/{GOOGLE_WB_KEY}")
        choice = 'start'
    elif choice == 'feedbacks':
        worksheet = google_work.open_sheet(GOOGLE_WB_KEY, 'Отзывы (тест)')
        supplier = ask_supplier()
        if choice == 'start': continue
        if type(supplier) == str: feedbacks_table = wildberries.feedbacks(supplier)
        else: feedbacks_table = wildberries.feedbacks_for_all(supplier)
        google_work.clear(worksheet)
        worksheet.update(feedbacks_table)
        print(f"\nТаблица успешно обновлена - https://docs.google.com/spreadsheets/d/{GOOGLE_WB_KEY}")
        choice = 'start'
    else: raise KeyError(f"Check menu choices - {choice} have not found")
