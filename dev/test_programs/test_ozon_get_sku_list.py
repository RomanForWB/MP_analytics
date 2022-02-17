import requests
import modules.ozon.info as ozon_info

headers = {'Client-Id': ozon_info.client_id('tumanyan'),
           'Api-Key': ozon_info.api_key('tumanyan')}
url = 'https://api-seller.ozon.ru/v1/product/list'
body = {
    "filter": {
        "visibility": "IN_SALE"
    },
    "page": 1,
    "page_size": 5000
}

response = requests.post(url=url, json=body, headers=headers)
result = response.json()
product_ids = [item['product_id'] for item in result['result']['items']]

url = 'https://api-seller.ozon.ru/v2/product/info/list'
body = {'product_id': product_ids}
response = requests.post(url=url, json=body, headers=headers)
result = response.json()

sku_list = list()
for item in result['result']['items']:
    for source in item['sources']:
        if source['source'] == 'fbo': sku_list.append(source['sku'])
print(sku_list)

