import requests

MPSTATS_TOKEN = '61f13463acf5c2.3680545125abcc4e82cf45ecd7c2cfa60c39ef32'

headers = {'X-Mpstats-TOKEN': MPSTATS_TOKEN,
           'Content-Type': 'application/json'}
body = {"startRow": 0,
        "endRow": 20,
        "filterModel":
            {"id":
                 {"filterType": "number",
                  "type": "equals",
                  "filter": 35934411,
                  "filterTo": None}
            }
    }
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

params = {'path': 'Женщинам/Одежда'}
response = requests.post('https://mpstats.io/api/wb/get/category', headers=headers, json=body, params=params)
result = response.json()
for item in result['data']:
    print(item)
