import modules.google_work as google_work

GOOGLE_CATEGORIES_KEY = '1i639nTdBNRp3TyDvA1qPT-QP0RdNaJiwkxBIOPMZoLs'
worksheet = google_work.open_sheet(GOOGLE_CATEGORIES_KEY, 'Категории (тест)')
google_work.clear(worksheet, ['B:ZZ'])