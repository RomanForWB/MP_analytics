import requests

counter = 0
failure_counter = None

def ask_stop():
    print("\nПолучение данных задерживается...")
    print("1 - Продолжить попытки")
    print("2 - Остановиться на полученных данных")
    choice = input("Выбор: ")
    if '2' in choice: return True
    else: return False


def _fetch_all(http_method, ids, content_type='text',
               url=None, urls_list=None,
               body=None, bodies_list=None,
               params=None, params_list=None,
               headers=None, headers_list=None,
               timeout=10):
    global counter
    global failure_counter
    failure_counter = 100 + len(ids)
    counter = 0
    if urls_list is not None: print(f"Подключение к {urls_list[0].split('//')[1].split('/')[0]}...")
    else: print(f"Подключение к {url.split('//')[1].split('/')[0]}...")
    print(f"Всего запросов: {len(ids)}")
    session = requests.Session()
    result_dict = dict()
    for i in range(len(ids)):
        if urls_list is not None: r_url = urls_list[i]
        else: r_url = url
        if headers_list is not None: r_headers = headers_list[i]
        else: r_headers = headers
        if params_list is not None: r_params = params_list[i]
        else: r_params = params
        if bodies_list is not None: r_body = bodies_list[i]
        else: r_body = body
        while True:
            try:
                if http_method.lower() == 'get':
                    response = session.get(url=r_url, headers=r_headers, params=r_params, timeout=timeout)
                elif http_method.lower() == 'post':
                    response = session.post(url=r_url, headers=r_headers, params=r_params, json=r_body, timeout=timeout)
                if response.status_code < 200 or response.status_code >= 300:
                    print(f'\rОбработано: {counter}\tСейчас в обработке: {ids[i]}', end=' ')
                    if failure_counter is None: break
                    failure_counter -= 1
                    if failure_counter <= 0:
                        if ask_stop(): failure_counter = None
                        else: failure_counter = 500 + len(ids)
                else:
                    if content_type.lower() == 'json': result = response.json()
                    else: result = response.text
                    counter += 1
                    print(f'\rОбработано: {counter}', end=' ')
                    result_dict[ids[i]] = result
                    break
            except (requests.exceptions.RequestException, requests.exceptions.BaseHTTPError):
                session.close()
                session = requests.Session()
                timeout += 5
    print()
    return result_dict


def fetch(http_method, ids, content_type='text',
          url=None, urls_list=None,
          body=None, bodies_list=None,
          params=None, params_list=None,
          headers=None, headers_list=None,
          timeout=10):
    for iter_list in [bodies_list, params_list, headers_list, urls_list]:
        if iter_list is not None and len(iter_list) != len(ids):
            raise IndexError("Length of iterable list must be equal to ids list.")
    return _fetch_all(http_method, ids, content_type=content_type,
                                  url=url, urls_list=urls_list,
                                  body=body, bodies_list=bodies_list,
                                  params=params, params_list=params_list,
                                  headers=headers, headers_list=headers_list,
                                  timeout=timeout)