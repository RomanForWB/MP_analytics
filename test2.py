import modules.google_work as google_work

GOOGLE_CATEGORIES_KEY = '1i639nTdBNRp3TyDvA1qPT-QP0RdNaJiwkxBIOPMZoLs'
worksheet = google_work.open_sheet(GOOGLE_CATEGORIES_KEY, 'Остатки')
sku_list = [44117798, 16557761, 35663011, 35663012, 16557765, 16557766, 12129508, 16557769, 16557770]
supply_list = [[item] for item in sku_list]
worksheet.update('A1', supply_list)