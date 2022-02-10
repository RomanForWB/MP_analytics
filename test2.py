import requests

nm = 50387174

response = requests.get(f'https://wbx-content-v2.wbstatic.net/ru/{nm}.json')
result = response.json()
for key, value in result.items():
    print(f"{key} : {value}")