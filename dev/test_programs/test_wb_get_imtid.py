import requests

response = requests.get('https://wbx-content-v2.wbstatic.net/ru/57288572.json')
result = response.json()
for key, value in result.items():
    print(f"{key} : {value}")