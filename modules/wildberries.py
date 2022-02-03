from bs4 import BeautifulSoup

import modules.async_requests as async_requests

def get_category_and_brand(sku_list):
    url_list = [f'https://www.wildberries.ru/catalog/{sku}/detail.aspx' for sku in sku_list]
    categories_dict = async_requests.by_urls('GET', url_list, sku_list,
                                             content_type='text')
    counter = 0
    print("\nПарсинг категорий из карточек Wildberries...")
    print(f"Всего карточек: {len(categories_dict)}")
    for sku, value in categories_dict.items():
        soup = BeautifulSoup(value, 'html.parser')
        category_soup = soup.findAll('a', class_="breadcrumbs__link")
        if len(category_soup) < 2:
            categories_dict[sku] = {'category': None, 'brand': None}
        else:
            categories_dict[sku] = dict()
            header_category = category_soup[1].text.strip()
            for data in category_soup[2:-1]:
                header_category += '/' + data.text.strip()
            categories_dict[sku]['category'] = header_category
            categories_dict[sku]['brand'] = category_soup[-1].text.strip()
        counter += 1
        print(f'\rОбработано: {counter}', end='')
    return categories_dict

# ================== тестовые запуски ==================
if __name__ == '__main__':
    sku_list = [44117798,16557761,35663011,35663012,16557765,16557766,12129508,16557769,16557770]
    items_dict = get_category_and_brand(sku_list)
    for sku, value in items_dict.items():
        print(sku + value)
