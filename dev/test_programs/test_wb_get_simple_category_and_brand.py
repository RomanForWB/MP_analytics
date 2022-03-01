import modules.async_requests as async_requests
import json

def fetch_info(nm_list):
    urls_list = [f'https://wbx-content-v2.wbstatic.net/ru/{nm}.json' for nm in nm_list]
    nm_dict = async_requests.fetch('GET', nm_list, urls_list=urls_list, content_type='text')
    nm_dict = {nm: json.loads(item) for nm, item in nm_dict.items()}
    return nm_dict

print(fetch_info([62089293]))

