import requests
import modules.wildberries.info as info

supplier = 'ahmetov'
params = {'pattern': 'Ботинки', 'lang': 'RU'}
headers = {'Authorization': info.api_key('token', supplier)}
url = 'https://suppliers-api.wildberries.ru/api/v1/config/get/object/list'
response = requests.get(url, params=params, headers=headers)
result = response.json()

for key, value in result.items():
    print(key, value)