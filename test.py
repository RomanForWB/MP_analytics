from datetime import date, datetime, timedelta
import requests

url = 'https://www.ozon.ru/product/vodolazka-298859747/reviews'
headers = {'Content-Type': 'application/json'}
response = requests.get(url)

print(response.text)