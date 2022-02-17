import requests
import modules.wildberries.info as info

supplier = 'ahmetov'
params = {'name': 'Куртки'}
headers = {'Authorization': info.api_key('token', supplier)}
url = 'https://suppliers-api.wildberries.ru/api/v1/config/get/object/translated'
response = requests.get(url, params=params, headers=headers)
result = response.json()

for key, value in result['data'].items(): print(key, value)
print()
for item in result['data']['addin']: print(item)
print()
for key, value in result['data']['nomenclature'].items(): print(key, value)
