import requests
import json

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjgyOGMzOTJmLWJkMzUtNDRjYi04MDM5LTFjODQ3ZjQ1YmEzNSJ9.5D_uGQ5yt4KsAd_4Og9qMRbzZ6praIYdtQAnWG9IU6Q'

headers = {'Authorization': token}
body = {"id": 1,
        "jsonrpc": "2.0",
        "params": {
        'withError': False,
        'query': {
            "limit": 1000
        }
    }
}
r = requests.post("https://suppliers-api.wildberries.ru/card/list", json=body, headers=headers)
result = json.loads(r.text)
print(result)
# url = 'https://www.wildberries.ru/catalog/47536491/detail.aspx'
# r = requests.get(url)
# print(r.text)
#
# url = 'https://public-feedbacks.wildberries.ru/api/v1/'
# r = requests.get(url)
# print(r.text)
