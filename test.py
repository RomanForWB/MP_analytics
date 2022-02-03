import requests

import modules.files as files
WILDBERRIES_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjgyOGMzOTJmLWJkMzUtNDRjYi04MDM5LTFjODQ3ZjQ1YmEzNSJ9.5D_uGQ5yt4KsAd_4Og9qMRbzZ6praIYdtQAnWG9IU6Q'

r = requests.get("https://suppliers-api.wildberries.ru/public/api/v1/info", params=params, headers=headers)
print(len(r.json()))
print(r.json())
