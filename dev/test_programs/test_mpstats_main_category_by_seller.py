import requests

MPSTATS_TOKEN = '61f13463acf5c2.3680545125abcc4e82cf45ecd7c2cfa60c39ef32'

headers = {'X-Mpstats-TOKEN': MPSTATS_TOKEN,
           'Content-Type': 'application/json'}
body = {"startRow": 0,
        "endRow": 5000}
# body = {"startRow": 0,
#         "filterModel":
#             {"id":
#                  {"filterType": "number",
#                   "operator": 'OR',
#                   "condition1": {
#                       "filterType": 'number',
#                       "type": 'equals',
#                       "filter": 43407271
#                   },
#                   "condition2": {
#                       "filterType": 'number',
#                       "type": 'equals',
#                       "filter": 43407264
#                   },
#                   }
#              }
#         }

params = {'path': 'ИП Фурсов И Н'}
response = requests.post('https://mpstats.io/api/wb/get/seller', headers=headers, json=body, params=params)
result = response.json()
print(len(result['data']))
# for item in result['data']:
#     print(item)
