import modules.google_work as google_work
import modules.files as files
import modules.wildberries as wildberries

import requests

worksheet = google_work.open_sheet(files.get_google_key('wb_analytics'), 'Заказы (тест)')
orders_table = wildberries.orders('ahmetov')
google_work.insert_table(worksheet, orders_table, replace=True)