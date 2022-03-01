import requests
import modules.ozon.info as ozon_info
import modules.ozon.fetch as fetch

result = fetch.mpstats_positions(nm=298883264)
print(result)