from datetime import date, datetime, timedelta
import modules.ozon.analytics as ozon_analytics
import modules.ozon.info as ozon_info
import requests
import httpx
import asyncio

category_ids = [17033665, 17033665, 17033665, 17033665]

result = ozon_analytics._fetch_categories_by_ids(category_ids)
print(result)