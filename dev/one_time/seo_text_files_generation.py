import modules.files as files

categories_for_item_text = files.open_text('Заполнение/Возможные категории.txt').strip()
categories_for_item_list = categories_for_item_text.split('\n\n')
categories_for_item = dict()
for item_values in categories_for_item_list:
    item_values_lines = item_values.splitlines()
    item = item_values_lines[0].strip()
    categories = [line.strip() for line in item_values_lines[1:]]
    categories_for_item[item] = categories
print(categories_for_item)

keywords_for_category_text = files.open_text('Заполнение/Попадание.txt').strip()
keywords_for_category_list = keywords_for_category_text.split('\n\n')
keywords_for_category = dict()
for category_values in keywords_for_category_list:
    category_values_lines = category_values.splitlines()
    category = category_values_lines[0].strip()
    keywords = [line.strip() for line in category_values_lines[1:]]
    keywords_for_category[category] = keywords
print(keywords_for_category)

wide_lines = list()
for item, categories in categories_for_item.items():
    wide_lines.append(item)
    for category in categories:
        wide_lines.append('[' + category + ']')
        try: wide_lines += keywords_for_category[category]
        except KeyError: wide_lines.append('Нет данных')
    wide_lines.append('')

files.write_lines(wide_lines, 'Заполнение/Развернуто по категориям.txt')

keywords_for_item_summary = dict()
for item, categories in categories_for_item.items():
    keywords_for_item_summary[item] = dict()
    for category in categories:
        try:
            for value in keywords_for_category[category]:
                param = value.split(':')[0].strip()
                keywords = [keyword.strip() for keyword in value.split(':')[1].split('/')]
                keywords_for_item_summary[item].setdefault(param, list())
                for keyword in keywords:
                    if keyword not in keywords_for_item_summary[item][param]:
                        keywords_for_item_summary[item][param].append(keyword)
        except KeyError: pass

summary_lines = list()
for item, params in keywords_for_item_summary.items():
    summary_lines.append(item)
    for param, keywords in params.items():
        summary_lines.append(f'{param}: ' + ' / '.join(keywords))
    summary_lines.append('')

files.write_lines(summary_lines, 'Заполнение/Инструкция к заполнению.txt')