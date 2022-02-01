import requests

WILDBERRIES_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjgyOGMzOTJmLWJkMzUtNDRjYi04MDM5LTFjODQ3ZjQ1YmEzNSJ9.5D_uGQ5yt4KsAd_4Og9qMRbzZ6praIYdtQAnWG9IU6Q'
MPSTATS_TOKEN = '61f13463acf5c2.3680545125abcc4e82cf45ecd7c2cfa60c39ef32'

headers = {'X-Mpstats-TOKEN': MPSTATS_TOKEN,
               'Content-Type': 'application/json'}

# params = {'quantity': '0'}
# r = requests.get("https://suppliers-api.wildberries.ru/public/api/v1/info", params=params, headers=headers)
# print(r.text)
# result = r.json()
# for sub in result:
#     print(str(sub['nmId'])+' '+ str(sub['price']))

# params = {'skip' : '0', 'take' : '1000'}
# r = requests.get("https://suppliers-api.wildberries.ru/api/v2/stocks", params=params, headers=headers)
# result = r.json()
# print(result['total'])
# for sub in result['stocks']:
#     print(sub['name']+' '+ sub['article'] + ' | остаток: ' + str(sub['stock']))

# params = {'skip' : '0', 'take' : '1000', 'date_start' : '2022-01-01T15:00:00.000Z'}
# r = requests.get("https://suppliers-api.wildberries.ru/api/v2/orders", params=params, headers=headers)
# print(r.text)
# result = r.json()
# print(result['total'])

params = {'d1': '2022-01-01', 'd2': '2022-01-31'}
r = requests.get("https://mpstats.io/api/wb/get/item/16598370/orders_by_size",params=params, headers=headers)
result = r.json()
print(result)
print(sorted(result['2022-01-01'].keys()))
prodazh1 = 0
prodazh2 = 0
prodazh3 = 0
for date, sizes in result.items():
    print(date, end='')
    for size, value in sizes.items():
        if value['sales'] == 'NaN': value['sales'] = 0
        if value['balance'] == 'NaN': value['balance'] = 0
        if value['size_name'] == '50-52':

            prodazh1 += value['sales']
            print('\t| ' + size + ' Остаток: ' + str(value['balance']) + ' Продаж: ' + str(value['sales']) , end='')
    print('')
print('Число продаж 1: '+ str(prodazh1))
print('Число продаж 1: '+ str(prodazh2))
print('Число продаж 1: '+ str(prodazh3))

