import requests
import modules.files as files
import json

headers = {'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjgyOGMzOTJmLWJkMzUtNDRjYi04MDM5LTFjODQ3ZjQ1YmEzNSJ9.5D_uGQ5yt4KsAd_4Og9qMRbzZ6praIYdtQAnWG9IU6Q'}
data = {
  "id": 1,
  "jsonrpc": "2.0",
  "params": {
      'withError' : False,
      'query': {
          "limit": 1000
      }
  }
}
status_code = 0
while status_code != 200:
    r = requests.post("https://suppliers-api.wildberries.ru/card/list", json=data, headers=headers)
    status_code = r.status_code
    print(status_code)
result = json.loads(r.text)
print(len(result['result']['cards']))
print(result)
#files.write_json(result, 'files/post.json', codirovka='Windows-1251')