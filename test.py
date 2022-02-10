import modules.wildberries as wildberries
import modules.google_work as google_work
import modules.files as files
from main import supplier_names
import requests

nm_list = [49405387,
           49405718,
           43391708,
           13235377,
           14812895,
           16804479,
           17586658]

worksheet = google_work.open_sheet(files.get_google_key('wb_analytics'), 'Отзывы (тест)')
feedbacks_table = wildberries.feedbacks(nm_list)
google_work.clear(worksheet)
worksheet.update(feedbacks_table)
