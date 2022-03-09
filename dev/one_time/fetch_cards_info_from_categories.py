import json, re
import modules.files as files
import modules.async_requests as async_requests

except_list = ['', 'в', 'на', 'без', 'с', "и", "для", "не", "как", "по", "из",
               "так", "см", "что", "или", "а", "же", "то", "к", "от", "до", "это", "под", "при"]

def words_analytics(category_path, categories, kind=None):
    for category_name, category in categories.items():
        for counter in range(10):
            files.create_folder(category_path + category_name)
            url = f'https://wbxcatalog-ru.wildberries.ru/{category}/catalog'
            xsubject_list = [i for i in range(counter*1000, (counter+1)*1000)]
            if kind is None: params_list = [{'sort': 'popular',
                                             'xsubject': i,
                                             'page': 1,
                                             'locale': 'ru'} for i in xsubject_list]
            else: params_list = [{'sort': 'popular',
                                          'xsubject': i,
                                          'page': 1,
                                          'locale': 'ru',
                                          'kind': kind} for i in xsubject_list]

            result_dict = async_requests.fetch('GET', ids=xsubject_list, url=url, params_list=params_list,
                                               content_type='text')
            for i in xsubject_list:
                result = json.loads(result_dict[i])['data']['products']
                nm_list = [item['id'] for item in result]
                if len(nm_list) == 0: continue
                urls_list = [f'https://wbx-content-v2.wbstatic.net/ru/{nm}.json' for nm in nm_list]
                result = async_requests.fetch('GET', nm_list, urls_list=urls_list, content_type='text', timeout=7)
                nm_dict = {nm: json.loads(item) for nm, item in result.items()}
                params_dict = dict()
                params_dict['Наименование'] = dict()
                params_dict['Описание'] = dict()
                for value in nm_dict.values():
                    try:
                        imt_name = re.sub(r"[^а-яА-Я]", ' ', value['imt_name'])
                        name_words = re.split(r'\s+', imt_name)
                        for word in name_words:
                            word = word.lower()
                            if word not in except_list:
                                params_dict['Наименование'].setdefault(word, 0)
                                params_dict['Наименование'][word] += 1
                    except KeyError: pass

                    try:
                        description = re.sub(r"[^а-яА-Я]", ' ', value['description'])
                        description_words = re.split(r'\s+', description)
                        for word in description_words:
                            word = word.lower()
                            if word not in except_list:
                                params_dict['Описание'].setdefault(word, 0)
                                params_dict['Описание'][word] += 1
                    except KeyError: pass
                    try:
                        for param in value['options']:
                            param_name = param['name']
                            params_dict.setdefault(param_name, dict())
                            param_value = re.sub(r"[^а-яА-Я]", ' ', param['value'])
                            param_words = re.split(r'\s+', param_value)
                            for word in param_words:
                                word = word.lower()
                                if word not in except_list:
                                    params_dict[param_name].setdefault(word, 0)
                                    params_dict[param_name][word] += 1
                    except KeyError: pass

                subj_name = re.sub(r"[^а-яА-Я]", ' ', nm_dict[nm_list[0]]['subj_name'])
                rows = list()
                for param_name, word_values in params_dict.items():
                    values_list = [param_name] + (sorted([f'{word} - {count}' for word, count in word_values.items()],
                                         key=lambda item: int(item.split(' - ')[1]), reverse=True))[:20] + ['']
                    rows += values_list
                files.write_lines(rows, f'{category_path}{category_name}/{i} - {subj_name}.txt',
                                  encoding='Windows-1251')


if __name__ == '__main__':
    category_path = 'Категории/Женщинам/'
    categories = {"Брюки": 'pants',
                  "Верхняя одежда": 'outwear',
                  "Блузки и рубашки": 'bl_shirts',
                  "Джемперы, водолазки и кардиганы": 'jumpers_cardigans',
                  "Джинсы": 'jeans',
                  "Комбинезоны": 'overalls',
                  "Костюмы": 'costumes',
                  "Лонгсливы": 'sweatshirts_hoodies',
                  "Пиджаки, жилеты и жакеты": 'blazers_wamuses',
                  "Платья и сарафаны": 'dresses',
                  "Футболки и топы": 'tops_tshirts',
                  "Халаты": 'housewear_root',
                  "Шорты": 'shorts',
                  "Юбки": 'skirts',
                  "Белье": 'women_underwear1',
                  "Большие размеры": 'women_bigsize',
                  "Будущие мамы": 'moms',
                  "Для высоких, невысоких": 'short_tall',
                  "Офис": 'office_bigroot',
                  "Пляжная мода": 'beach',
                  "Религиозная": 'religion',
                  "Свадьба": 'wedding',
                  "Спецодежда и СИЗы": 'work_clothes',
                  "Подарки женщинам": 'gift4'}
    words_analytics(category_path, categories, kind=2)
    category_path = 'Категории/'
    categories = {'Мужчинам': 'men_clothes'}
    words_analytics(category_path, categories, kind=1)
    category_path = 'Категории/Обувь/'
    categories = {'Ортопедическая обувь': 'shealth'}
    words_analytics(category_path, categories)
    category_path = 'Категории/Обувь/'
    categories = {'Мужская': 'men_shoes'}
    words_analytics(category_path, categories, kind=1)
    category_path = 'Категории/Обувь/'
    categories = {'Женская': 'women_shoes'}
    words_analytics(category_path, categories, kind=2)
    category_path = 'Категории/Спорт/'
    categories = {'Бег Ходьба': 'sport3'}
    words_analytics(category_path, categories)
    category_path = 'Категории/Спорт/'
    categories = {'Для женщин - Одежда': 'sport6'}
    words_analytics(category_path, categories, kind=2)
    category_path = 'Категории/Спорт/'
    categories = {'Фитнес и тренажеры': 'sport1'}
    words_analytics(category_path, categories, kind=2)
    category_path = 'Категории/Спорт/'
    categories = {'Различные виды спорта': 'sport4'}
    words_analytics(category_path, categories, kind=2)
