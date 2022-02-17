import modules.wildberries.analytics as wildberries

supplier = 'ahmetov'
result = wildberries.fetch_cards(supplier=supplier)
# for item in result:
#     print(item)
for key, value in result[0].items():
    print(key,value)