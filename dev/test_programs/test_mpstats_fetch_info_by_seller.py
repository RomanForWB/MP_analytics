import requests
import modules.info as info

# устаревшие идентификаторы - только для теста
seller_identifiers = {"maryina": "ИП Марьина А А",
                      "tumanyan": "ИП Туманян Арен Арменович",
                      "neweramedia": "ООО НЬЮЭРАМЕДИА",
                      "ahmetov": "ИП Ахметов В Р",
                      "fursov": "ИП Фурсов И Н"}

headers = {'X-Mpstats-TOKEN': info.mpstats_token(),
               'Content-Type': 'application/json'}
supplier = 'maryina'
url = 'https://mpstats.io/api/wb/get/seller'
body = {"startRow": 0, "endRow": 5000}
params = {'path': seller_identifiers[supplier]}
response = requests.post(url, headers=headers, json=body, params=params)
result = response.json()['data']
print(len(result))
for item in result: print(item)