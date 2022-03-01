import modules.wildberries.fetch as fetch

result = fetch.orders(supplier='ahmetov')
for item in result: print(item)