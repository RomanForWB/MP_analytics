
def fetch_simple_category_and_brand(nm_list):
    urls_list = [f'https://wbx-content-v2.wbstatic.net/ru/{nm}.json' for nm in nm_list]
    nm_dict = async_requests.fetch('GET', nm_list, urls_list=urls_list, content_type='text')
    simple_categories_dict = dict()
    for nm, card_info in nm_dict.items():
        card_info = json.loads(card_info)
        simple_categories_dict[nm] = {'category': f"{card_info['subj_root_name']}/{card_info['subj_name']}",
                                      'brand': card_info['selling']['brand_name']}
    return simple_categories_dict

