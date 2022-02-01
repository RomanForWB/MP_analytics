from bs4 import BeautifulSoup

import modules.async_fetch as async_fetch

def get_main_category(sku_list):
    url_list = [f'https://www.wildberries.ru/catalog/{sku}/detail.aspx' for sku in sku_list]
    items_list = async_fetch.by_urls('GET', url_list,
                                     additional_ids=sku_list,
                                     content_type='text')
    counter = 0
    print("\nПарсинг категорий из карточек Wildberries...")
    print(f"Всего карточек: {len(items_list)}")
    for i in range(len(items_list)):
        soup = BeautifulSoup(items_list[i][1], 'html.parser')
        categories_soup = soup.findAll('a', class_="breadcrumbs__link")
        if len(categories_soup) < 2: items_list[i][1] = None
        else:
            header_category = categories_soup[1].text.strip()
            for data in categories_soup[2:-1]:
                header_category += '/' + data.text.strip()
            items_list[i][1] = header_category
        counter += 1
        print(f'\rОбработано: {counter}', end='')
    return items_list

# ================== тестовые запуски ==================
if __name__ == '__main__':
    sku_list = [44117798,16557761,35663011,35663012,16557765,16557766,12129508,16557769,16557770]
    category_list = get_main_category(sku_list)
    print(category_list)