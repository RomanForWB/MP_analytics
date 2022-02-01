from gspread import authorize
from oauth2client.service_account import ServiceAccountCredentials
# EMAIL: roman-wb@roman-wb.iam.gserviceaccount.com

# === подключение к google ===
def initialize_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    gc = authorize(credentials)
    return gc

# === получить лист google-документа ===
def open_sheet(google_sheet_key, sheet_name=1):
    print(f'Подключение к https://docs.google.com/spreadsheets/d/{google_sheet_key}...')
    gc = initialize_connection()
    if sheet_name == 1:
        google_sheet = gc.open_by_key(google_sheet_key)
        worksheet = google_sheet.get_worksheet(0)
    else:
        google_sheet = gc.open_by_key(google_sheet_key)
        worksheet = google_sheet.worksheet(sheet_name)
    return worksheet

# === получить столбцы google-таблицы без шапки ===
def get_columns(worksheet, header_count, *columns):
    max_length = max([len(worksheet.col_values(column)[header_count:]) for column in columns])
    table = list()
    for column in columns:
        cells = worksheet.col_values(column)[header_count:]
        if len(cells) == max_length:
            table.append(cells)
        else:
            end_cells = [''] * (max_length - len(cells))
            table.append(cells + end_cells)

    if len(table) == 1: return table[0]
    else: return table

# === очистить лист или несколько range сразу ===
def clear(worksheet, ranges=None):
    if ranges is not None:
        if type(ranges) == str: ranges = [ranges]
        worksheet.batch_clear(ranges=ranges)
    else: worksheet.clear()