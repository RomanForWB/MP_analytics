import requests
import modules.files as files
import json

token = files.get_wb_key('token', 'ИП Марьина А.А.')
headers = {'Authorization': token}
data = {"id": 1,
        "jsonrpc": "2.0",
        "params": {
            'withError' : False,
            'query': { "limit": 1000 }
            }
        }
status_code = 0
while status_code != 200:
    response = requests.post("https://suppliers-api.wildberries.ru/card/list", json=data, headers=headers)
    status_code = response.status_code
    print(status_code)

result = json.loads(response.text)
print(result)
print(len(result['result']['cards']))