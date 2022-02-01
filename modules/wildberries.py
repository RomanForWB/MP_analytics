from bs4 import BeautifulSoup

import modules.async_fetch as async_fetch

def get_category_and_brand(sku_list):
    url_list = [f'https://www.wildberries.ru/catalog/{sku}/detail.aspx' for sku in sku_list]
    items_dict = async_fetch.by_urls('GET', url_list, sku_list,
                                     content_type='text')
    counter = 0
    print("\nПарсинг категорий из карточек Wildberries...")
    print(f"Всего карточек: {len(items_dict)}")
    for sku, value in items_dict.items():
        soup = BeautifulSoup(value, 'html.parser')
        category_soup = soup.findAll('a', class_="breadcrumbs__link")
        if len(category_soup) < 2:
            items_dict[sku] = None
        else:
            header_category = category_soup[1].text.strip()
            for data in category_soup[2:]:
                header_category += '/' + data.text.strip()
            items_dict[sku] = header_category
        counter += 1
        print(f'\rОбработано: {counter}', end='')
    return items_dict

def get_category(sku_list):
    items_dict = get_category_and_brand(sku_list)
    return {sku: value.rsplit('/', 1)[0] for sku, value in items_dict.items()}

def get_brand(sku_list):
    items_dict = get_category_and_brand(sku_list)
    return {sku: value.rsplit('/', 1)[1] for sku, value in items_dict.items()}

# ================== тестовые запуски ==================
if __name__ == '__main__':
    sku_list = [44117798,16557761,35663011,35663012,16557765,16557766,12129508,16557769,16557770]
    items_dict = get_category_and_brand(sku_list)
    for sku, value in items_dict.items():
        print(sku)
        print(value)