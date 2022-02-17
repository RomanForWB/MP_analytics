import requests
import modules.ozon.info as ozon_info

headers = {'Client-Id': ozon_info.client_id('tumanyan'),
           'Api-Key': ozon_info.api_key('tumanyan')}
url = 'https://api-seller.ozon.ru/v2/product/info'
body = {"product_id": 298883264}

response = requests.post(url=url, json=body, headers=headers)
result = response.json()
for key, value in result['result'].items():
    print(key, value)