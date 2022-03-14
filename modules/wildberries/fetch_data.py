from datetime import date, timedelta, datetime
from copy import deepcopy
import modules.async_requests as async_requests
import modules.session_requests as session_requests
import modules.single_requests as single_requests
import modules.google_work as google_work
import modules.wildberries.info as wb_info
import modules.info as info
import json, re

_cards = dict()
_orders = dict()
_stocks = dict()
_report = dict()
_detail_reports = dict()
_top_nms = None
_buyouts = None
_cost = None
_cookie_token = None

_mpstats_info = dict()
_mpstats_categories_info = dict()
_mpstats_positions = dict()


def _detail_report_by_suppliers_list(suppliers_list, weeks=4):
    url = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/reportDetailByPeriod'
    headers = {'Content-Type': 'application/json'}
    # finding date of last detail report
    last_date = date.today()
    while True:
        last_date -= timedelta(days=1)
        params = {'key': wb_info.api_key('x64', suppliers_list[0]),
                  'dateFrom': str(last_date),
                  'dateTo': str(last_date)}
        first_result = single_requests.fetch('GET', content_type='json', url=url,
                                             params=params, headers=headers)
        if first_result is not None: break
    # fetching
    for supplier in suppliers_list:
        if _detail_reports.get(supplier) is None:
            params_list = [{'key': wb_info.api_key('x64', supplier),
                            'dateFrom': str(last_date - timedelta(days=(7 * i) + 6)),
                            'dateTo': str(last_date - timedelta(days=7 * i))} for i in range(weeks)]
            result_dict = session_requests.fetch('GET', [i for i in range(weeks)], params_list=params_list,
                                                 url=url, headers=headers, content_type='text', timeout=10)
            result = list()
            for key, value in result_dict.items():
                if value == 'null': pass
                else: result += json.loads(value)
            _detail_reports[supplier] = result

    return {supplier: deepcopy(_detail_reports[supplier]) for supplier in suppliers_list}

'''{supplier: 
    [{
    realizationreport_id, Номер отчета
    suppliercontract_code, Договор
    rid, Уникальный идентификатор позиции заказа
    rr_dt, Дата операции
    rrd_id, Номер строки
    gi_id, Номер поставки
    subject_name, Предмет
    nm_id, Артикул
    brand_name, Бренд
    sa_name, Артикул поставщика
    ts_name, Размер
    barcode, Баркод
    doc_type_name, Тип документа
    quantity, Количество
    retail_price, Цена розничная
    retail_amount, Сумма продаж(Возвратов)
    sale_percent, Согласованная скидка
    commission_percent, Процент комиссии
    office_name, Склад
    supplier_oper_name, Обоснование для оплаты
    order_dt, Даты заказа
    sale_dt, Дата продажи
    shk_id, ШК
    retail_price_withdisc_rub, Цена розничная с учетом согласованной скидки
    delivery_amount, Кол-во доставок
    return_amount, Кол-во возвратов
    delivery_rub, Стоимость логистики
    gi_box_type_name, Тип коробов
    product_discount_for_report, Согласованный продуктовый дисконт
    supplier_promo, Промокод
    ppvz_spp_prc, Скидка постоянного Покупателя (СПП)
    ppvz_kvw_prc_base, Размер кВВ без НДС, % Базовый
    ppvz_kvw_prc, Итоговый кВВ без НДС, %
    ppvz_sales_commission, Вознаграждение с продаж до вычета услуг поверенного, без НДС
    ppvz_for_pay, К перечислению Продавцу за реализованный Товар
    ppvz_reward, Возмещение Расходов услуг поверенного
    ppvz_vw, Вознаграждение Вайлдберриз (ВВ), без НДС
    ppvz_vw_nds, НДС с Вознаграждения Вайлдберриз
    ppvz_office_id, Номер офиса
    ppvz_office_name, Наименование офиса доставки
    ppvz_supplier_id, Номер партнера
    ppvz_supplier_name, Партнер
    ppvz_inn ИНН партнера
    }, {...}, ...], supplier : [...], ...}'''
def detail_report(supplier=None, suppliers_list=None, weeks=4):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch detail_report.")
    elif supplier is not None: return _detail_report_by_suppliers_list([supplier], weeks)
    elif suppliers_list is not None: return _detail_report_by_suppliers_list(suppliers_list, weeks)


def _cards_by_suppliers_list(suppliers_list):
    new_suppliers_list = list()
    for supplier in suppliers_list:
        if _cards.get(supplier) is None: new_suppliers_list.append(supplier)
    if len(new_suppliers_list) > 0:
        url = "https://suppliers-api.wildberries.ru/card/list"
        body = {"id": 1,
                "jsonrpc": "2.0",
                "params": {
                    "withError": False,
                    "query": {
                        "limit": 1000
                    }
                }
                }
        headers_list = [{'Authorization': wb_info.api_key('token', supplier)}
                        for supplier in new_suppliers_list]
        cards_dict = async_requests.fetch('POST', new_suppliers_list, url=url, headers_list=headers_list,
                                          body=body, content_type='json', timeout=60)
        result = {supplier: cards_result['result']['cards'] for supplier, cards_result in cards_dict.items()}
        _cards.update(result)
    return {supplier: deepcopy(_cards[supplier]) for supplier in suppliers_list}

'''{supplier: [[
    addin, Параметры
    countryProduction, Страна-изготовитель товара
    createdAt, Дата создания
    id, Идентификатор карточки
    imtId, Идентификатор карточки
    imtSupplierId, Не используется поставщиком
    nomenclatures, Номенклатуры в карточке
    parent, Родительская категория
    object, Категория товара
    supplierId, Идентификатор поставщика
    supplierVendorCode, Артикул поставщика
    updatedAt, Дата последнего обновления карточки
    uploadID, ID массовой загрузки
    userId, Идентификатор пользователя
], [...] ...], supplier: [...] ...}'''
def cards(supplier=None, suppliers_list=None):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch cards.")
    elif supplier is not None: return _cards_by_suppliers_list([supplier])
    elif suppliers_list is not None: return _cards_by_suppliers_list(suppliers_list)


def _orders_by_suppliers_list(suppliers_list, start_date):
    new_suppliers_list = list()
    for supplier in suppliers_list:
        if _orders.get((supplier, start_date)) is None: new_suppliers_list.append(supplier)
    if len(new_suppliers_list) > 0:
        url = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/orders'
        headers = {'Content-Type': 'application/json'}
        params_list = [{'key': wb_info.api_key('x64', supplier),
                        'dateFrom': str(start_date)} for supplier in new_suppliers_list]
        result_dict = session_requests.fetch('GET', new_suppliers_list, content_type='json',
                                      url=url, headers=headers, params_list=params_list, timeout=20)
        _orders.update({supplier: cards_list for supplier, cards_list in result_dict})
    return {supplier: deepcopy(_orders[(supplier, start_date)]) for supplier in suppliers_list}

'''{supplier: [
[   gNumber, номер заказа
    date, дата заказа
    lastChangeDate, время обновления информации в сервисе
    supplierArticle, ваш артикул
    techSize, размер
    barcode, штрих-код
    quantity, кол-во
    totalPrice, цена до согласованной скидки/промо/спп
    discountPercent, согласованный итоговый дисконт.
    warehouseName, склад отгрузки
    oblast, область
    incomeID, номер поставки
    odid, уникальный идентификатор позиции заказа
    nmid, Код WB
    subject, предмет
    category, категория
    brand, бренд
    is_cancel, Отмена заказа. 1 – заказ отменен до оплаты
], [...] ...], supplier :[...] ...}'''
def orders(supplier=None, suppliers_list=None, start_date=str(date.today()-timedelta(days=6))):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch orders.")
    elif supplier is not None: return _orders_by_suppliers_list([supplier], start_date)
    elif suppliers_list is not None: return _orders_by_suppliers_list(suppliers_list, start_date)


def _stocks_by_suppliers_list(suppliers_list):
    new_suppliers_list = list()
    for supplier in suppliers_list:
        if _stocks.get(supplier) is None: new_suppliers_list.append(supplier)
    if len(new_suppliers_list) > 0:
        url = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/stocks'
        params_list = [{'key': wb_info.api_key('x64', supplier),
                        'dateFrom': str(date.today()-timedelta(days=1))}
                       for supplier in new_suppliers_list]
        result_dict = async_requests.fetch('GET', new_suppliers_list, url=url,
                                      params_list=params_list, content_type='json')
        _stocks.update(result_dict)
    return {supplier: deepcopy(_stocks[supplier]) for supplier in suppliers_list}

'''{supplier: [[
    lastChangeDate, дата и время обновления информации в сервисе
    supplierArticle, ваш артикул
    techSize, размер
    Barcode, штрих-код
    Quantity, кол-во доступное для продажи
    isSupply, договор поставки
    isRealization, договор реализации
    quantityFull, кол-во полное
    quantityNotInOrders, кол-во не в заказе
    warehouseName, название склада
    inWayToClient, в пути к клиенту (штук)
    inWayFromClient, в пути от клиента (штук)
    nmid, код WB
    subject, предмет
    category, категория
    DaysOnSite, кол-во дней на сайте
    brand, бренд
    SCCode, код контракта
], [...] ...], supplier: [...] ...}'''
def stocks(supplier=None, suppliers_list=None):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch stocks.")
    elif supplier is not None: return _stocks_by_suppliers_list([supplier])
    elif suppliers_list is not None: return _stocks_by_suppliers_list(suppliers_list)


def _report_by_suppliers_list(suppliers_list):
    new_suppliers_list = list()
    for supplier in suppliers_list:
        if _report.get(supplier) is None: new_suppliers_list.append(supplier)
    if len(new_suppliers_list) > 0:
        url = 'https://seller.wildberries.ru/ns/consolidated/analytics-back/api/v1/consolidated-table'
        params = {'isCommussion': 2}
        headers_list = [{'Cookie': f"WBToken={cookie_token(supplier)}; x-supplier-id={wb_info.api_key('cookie_id', supplier)}"}
                        for supplier in new_suppliers_list]
        report_dict = async_requests.fetch('GET', new_suppliers_list, content_type='json',
                                           url=url, params=params, headers_list=headers_list)
        _report.update({supplier: report_list['data'] for supplier, report_list in report_dict.items()})
    return {supplier: deepcopy(_report[supplier]) for supplier in suppliers_list}


def report(supplier=None, suppliers_list=None):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch report.")
    elif supplier is not None: return _report_by_suppliers_list([supplier])
    elif suppliers_list is not None: return _report_by_suppliers_list(suppliers_list)


def feedbacks(imt_list, count=200):
    url = 'https://public-feedbacks.wildberries.ru/api/v1/summary/full'
    bodies_list = [{"imtId": imt,
                    "skip": 0,
                    "take": count} for imt in imt_list]
    feedbacks_dict = async_requests.fetch('POST', imt_list, url=url,
                                          bodies_list=bodies_list, content_type='json')
    feedbacks_dict = {imt: feedbacks_info['feedbacks']
                      for imt, feedbacks_info in feedbacks_dict.items()}
    return feedbacks_dict

'''{
category: 
    {
        subcategory: [nm, nm, nm, ...]
        subcategory: [...]
    },
category: {...}
}'''
def top_nms():
    global _top_nms
    if _top_nms is None:
        category_ids = wb_info.wbxcatalog_ids()
        wbx_list = list()
        for category, sub_categories in category_ids.items():
            for sub_category, values in sub_categories.items():
                params = {'sort': 'popular', 'page': 1, 'locale': 'ru', 'kind': 2}
                if values.get('kind') is not None: params['kind'] = values['kind']
                if values.get('xsubject') is not None: params['xsubject'] = values['xsubject']
                wbx_list.append([category, sub_category,
                                f"https://wbxcatalog-ru.wildberries.ru/{values['id']}/catalog", params])
        products_dict = async_requests.fetch('GET', ids=[(item[0], item[1]) for item in wbx_list],
                                             urls_list=[item[2] for item in wbx_list],
                                             params_list=[item[3] for item in wbx_list],
                                             content_type='text')
        result = dict()
        for category, sub_categories in category_ids.items():
            result[category] = dict()
            for sub_category in sub_categories.keys():
                result[category][sub_category] = [item['id'] for item in json.loads(products_dict[(category, sub_category)])['data']['products']]
        _top_nms = result
    return deepcopy(_top_nms)

'''{
nm: {
    'buyouts':
        [date, count, price],
        [date, count, price],...
    }
nm : {...}
}'''
def buyouts():
    global _buyouts
    if _buyouts is None:
        ws = google_work.open_sheet(info.google_key('wb_day_reports'), 'выкупы')
        buyout_columns = google_work.get_columns(ws, 1, 1, 2, 3, 4)
        buyout_rows = [[buyout_columns[0][i], buyout_columns[1][i], buyout_columns[2][i], buyout_columns[3][i],]
                        for i in range(len(buyout_columns[0]))]
        result = dict()
        for item in buyout_rows:
            try:
                buyout_date = datetime.strptime(item[0], '%d.%m.%Y').strftime('%d.%m')
                nm = int(re.sub(r"[^0-9]", '', item[1]))
                count = int(re.sub(r"[^0-9]", '', item[2]))
                price = int(re.sub(r"[^0-9]", '', item[3]))
                result.setdefault(nm, {'buyouts': []})
                result[nm]['buyouts'].append([buyout_date, count, price])
            except ValueError: pass
        _buyouts = result
    return deepcopy(_buyouts)

'''{'nm':
    {
        nm: price,
        nm: price,...
    },
    'article':
    {
        article: price,
        article: price,...
    }
   }'''
def cost():
    global _cost
    if _cost is None:
        ws = google_work.open_sheet(info.google_key('wb_week_reports'), 'закуп')
        cost_columns = google_work.get_columns(ws, 1, 1, 2, 3)
        result = {'nm': {int(cost_columns[1][i]): int(cost_columns[2][i])
                         for i in range(len(cost_columns[0]))},
                  'article': {cost_columns[0][i].split('/')[0]+'/': int(cost_columns[2][i])
                              for i in range(len(cost_columns[0]))}}
        _cost = result
    return deepcopy(_cost)


def cookie_token(supplier) -> str:
    global _cookie_token
    if _cookie_token is None:
        url = 'https://seller.wildberries.ru/passport/api/v2/auth/login'
        body = {"country": "RU",
                "device": "test",
                "token": wb_info.api_key('main_token', supplier)}
        single_requests.fetch('POST', content_type='json', url=url, body=body)
        result = single_requests.session.cookies.get_dict()['WBToken']
        _cookie_token = result
    return deepcopy(_cookie_token)


# ==============================================


def _mpstats_positions_by_nm_list(nm_list, start_date):
    new_nm_list = list()
    for nm in nm_list:
        if _mpstats_positions.get((nm, start_date)) is None: new_nm_list.append(nm)
    if len(new_nm_list) > 0:
        headers = {'X-Mpstats-TOKEN': info.mpstats_token(),
                   'Content-Type': 'application/json'}
        urls_list = [f'https://mpstats.io/api/wb/get/item/{nm}/by_category' for nm in new_nm_list]
        params = {'d1': str(start_date), 'd2': str(date.today())}
        result_dict = async_requests.fetch('GET', new_nm_list, urls_list=urls_list, params=params,
                                           headers=headers, content_type='json')
        _mpstats_positions.update({(nm, start_date): values for nm, values in result_dict})
    return {nm: deepcopy(_mpstats_positions[(nm, start_date)]) for nm in nm_list}

'''
{
    'balance': [count, count, ...] Остатки по дням
    'categories': Позиции по категориям
    {
        category: [position, position, ...],
        category: [position, position, ...], ...
    }
    'days': ["14.07", "15.07", ...] Дни в периоде
    'final_price': [498, 498, ...] Итоговые цены (со скидкой)
    'sales': [144, 160, ...] Продажи по дням
}
'''
def mpstats_positions(nm=None, nm_list=None, start_date=str(date.today()-timedelta(days=7))):
    if nm_list is None and nm is None: raise AttributeError("No input data to fetch positions.")
    elif nm is not None: return _mpstats_positions_by_nm_list([nm], start_date)
    elif nm_list is not None: return _mpstats_positions_by_nm_list(nm_list, start_date)


def _mpstats_info_by_suppliers_list(suppliers_list):
    new_suppliers_list = list()
    for supplier in new_suppliers_list:
        if _mpstats_info.get(supplier) is None: new_suppliers_list.append(supplier)
    if len(new_suppliers_list) > 0:
        headers = {'X-Mpstats-TOKEN': info.mpstats_token(),
                   'Content-Type': 'application/json'}
        url = 'https://mpstats.io/api/wb/get/seller'
        body = {"startRow": 0, "endRow": 5000}
        for supplier in new_suppliers_list:
            result = list()
            for identifier in wb_info.seller_identifiers(supplier):
                params = {'path': identifier}
                result += single_requests.fetch('POST', content_type='json', url=url,
                                                body=body, params=params, headers=headers)['data']
            _mpstats_info[supplier] = result
    return {supplier: deepcopy(_mpstats_info[supplier]) for supplier in suppliers_list}


def mpstats_info(supplier=None, suppliers_list=None):
    if supplier is None and suppliers_list is None: raise AttributeError("No input data to fetch info.")
    elif supplier is not None: return _mpstats_info_by_suppliers_list([supplier])
    elif suppliers_list is not None: return _mpstats_info_by_suppliers_list(suppliers_list)

'''
[
    {
        period: Дата
        items: Число товаров в рейтинге
        brands:	Кол-во брендов
        sellers: Кол-во продавцов
        sales: Продано единиц товаров
        revenue: Выручка
        avg_price: Средняя цена товара в категории (все товары, среднее арифметическое)
        avg_sale_price: Средняя цена состоявшейся продажи (деление выручки на число продаж)
        comments: Среднее число комментариев на товар
        rating: Средний рейтинг
    },
    {...}, ... ]'''
def mpstats_categories_info(categories_list, start_date=str(date.today()-timedelta(days=7)),
                            end_date=str(date.today()-timedelta(days=1))):
    result = _mpstats_categories_info.get(tuple([tuple(categories_list), start_date, end_date]))
    if result is None:
        headers = {'X-Mpstats-TOKEN': info.mpstats_token(),
                   'Content-Type': 'application/json'}
        url = 'https://mpstats.io/api/wb/get/category/by_date'
        params_list = [{'path': category.strip(), 'groupBy': 'day',
                       'd1': str(start_date), 'd2': str(end_date)}
                       for category in categories_list]
        result_dict = async_requests.fetch("GET", categories_list, content_type='json', url=url,
                                           params_list=params_list, headers=headers)
        result = {category: {item['period']: item for item in day_values}
                  for category, day_values in result_dict.items()}
        _mpstats_categories_info[tuple([tuple(categories_list), start_date, end_date])] = result
    return deepcopy(result)


