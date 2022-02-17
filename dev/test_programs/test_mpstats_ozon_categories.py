import requests
import modules.ozon.info as ozon_info
import modules.ozon.mpstats as ozon_mpstats

result = ozon_mpstats.fetch_positions(nm=298883264)
print(result)