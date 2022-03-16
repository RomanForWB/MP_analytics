import modules.wildberries.fetch_data as fetch_data


def realizations_by_size(suppliers_list, weeks):
    fetched_detail_report = fetch_data.detail_report_by_suppliers_list(suppliers_list, weeks)
    realizations_by_size_dict = dict()
    for supplier, values in fetched_detail_report.items():
        for value in values:
            nm = value['nm_id']
            article = value['sa_name']
            category = value['subject_name']
            brand = value['brand']
            size = value['ts_name']
            dict_key = (supplier, nm, article, category, brand, size)
            realizations_by_size_dict.setdefault(dict_key, list())
            realizations_by_size_dict[dict_key].append(value)
    return realizations_by_size_dict


def sales_by_size(suppliers_list, weeks):
    realizations_dict = realizations_by_size(suppliers_list, weeks)
    sales_by_size_dict = dict()
    days_set = set()
    for dict_key, values in realizations_dict.items():
        for value in values: days_set.add(value['rr_dt'].split('T', 1)[0])
    days = sorted(list(days_set))
    for dict_key, values in realizations_dict.items():
        sales_by_size_dict[dict_key] = {day: {'pure_sales': {'quantity': 0, 'value': 0},
                                              'sales': {'quantity': 0, 'value': 0},
                                              'returns': {'quantity': 0, 'value': 0},
                                              'cancels': {'quantity': 0, 'value': 0},
                                              'logistics': {'quantity': 0, 'value': 0},
                                              'update': ''}
                                        for day in days}
        for value in values:
            day = value['rr_dt'].split('T', 1)[0]
            if value['doc_type_name'] == 'Продажа' and value['quantity'] > 0:
                sales_by_size_dict[dict_key][day]['sales']['quantity'] += value['quantity']
                sales_by_size_dict[dict_key][day]['sales']['value'] += value['ppvz_for_pay']
                sales_by_size_dict[dict_key][day]['pure_sales']['quantity'] += value['quantity']
                sales_by_size_dict[dict_key][day]['pure_sales']['value'] += value['ppvz_for_pay']
            elif value['doc_type_name'] == 'Продажа' and value['return_amount'] > 0:
                sales_by_size_dict[dict_key][day]['cancels']['quantity'] += value['return_amount']
            elif value['doc_type_name'] == 'Возврат' and value['quantity'] > 0:
                sales_by_size_dict[dict_key][day]['returns']['value'] += value['ppvz_for_pay']
                sales_by_size_dict[dict_key][day]['returns']['quantity'] += value['quantity']
                sales_by_size_dict[dict_key][day]['pure_sales']['quantity'] -= value['quantity']
                sales_by_size_dict[dict_key][day]['pure_sales']['value'] -= value['ppvz_for_pay']
                sales_by_size_dict[dict_key][day]['pure_sales']['value'] -= value['ppvz_reward']
            if value['delivery_rub'] > 0:
                sales_by_size_dict[dict_key][day]['logistics']['quantity'] += 1
                sales_by_size_dict[dict_key][day]['logistics']['value'] += value['delivery_rub']
            if value['rr_dt'] > sales_by_size_dict[dict_key][day]['logistics']['update']:
                sales_by_size_dict[dict_key][day]['logistics']['update'] = value['rr_dt']
    return sales_by_size_dict


