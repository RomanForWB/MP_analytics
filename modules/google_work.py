from gspread import authorize
from oauth2client.service_account import ServiceAccountCredentials
# EMAIL: roman-wb@roman-wb.iam.gserviceaccount.com


def initialize_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('keys/credentials.json', scope)
    gc = authorize(credentials)
    return gc


def open_sheet(google_sheet_key, sheet_name=1):
    print(f'Подключение к https://docs.google.com/spreadsheets/d/{google_sheet_key}...')
    gc = initialize_connection()
    google_sheet = gc.open_by_key(google_sheet_key)
    if sheet_name == 1: worksheet = google_sheet.get_worksheet(0)
    else: worksheet = google_sheet.worksheet(sheet_name)
    return worksheet


def get_columns(worksheet, header_count, *column_numbers):
    max_length = max([len(worksheet.col_values(column)[header_count:]) for column in column_numbers])
    table = list()
    for column in column_numbers:
        cells = worksheet.col_values(column)[header_count:]
        if len(cells) == max_length:
            table.append(cells)
        else:
            end_cells = [''] * (max_length - len(cells))
            table.append(cells + end_cells)

    if len(table) == 1: return table[0]
    else: return table


def clear(worksheet, ranges=None):
    if ranges is not None:
        if type(ranges) == str: ranges = [ranges]
        worksheet.batch_clear(ranges=ranges)
    else: worksheet.clear()


def insert_table(worksheet, table_rows, replace=False,
                 start_column=None, start_row=None, start_cell=None):
    if replace: clear(worksheet)
    if start_column is not None: worksheet.update(start_column+'1', table_rows)
    elif start_row is not None: worksheet.update('A'+str(start_row), table_rows)
    elif start_cell is not None: worksheet.update(start_cell, table_rows)
    else: worksheet.update(table_rows)
    print(f"Таблица \"{worksheet.title}\" успешно обновлена.")
