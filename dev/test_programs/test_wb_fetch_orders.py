import modules.wildberries.analytics as wildberries

result = wildberries.fetch_orders(supplier='ahmetov')
for item in result: print(item)