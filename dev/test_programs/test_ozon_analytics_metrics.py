import requests
from datetime import date, timedelta, datetime
import modules.ozon.info as ozon_info

url = 'https://api-seller.ozon.ru/v1/analytics/data'

headers = {'Client-Id': ozon_info.client_id(ozon_info.all_suppliers()[0]),
               'Api-Key': ozon_info.api_key(ozon_info.all_suppliers()[0])}

start_date = str(date.today() - timedelta(days=6))
end_date = str(date.today())

body = {'date_from': start_date,
        'date_to': end_date,
        'dimension': ['sku', 'day'],
        'metrics': ['hits_view_search', 'revenue', 'ordered_units', 'position_category'],
        'limit': 1000}
result = requests.post(url, headers=headers, json=body).json()

for item in result['result']['data']: print(item)