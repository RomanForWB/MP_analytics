import modules.wildberries.fetch as fetch

supplier = 'ahmetov'
result = fetch.cards(supplier=supplier)
# for item in result:
#     print(item)
for key, value in result[0].items():
    print(key,value)