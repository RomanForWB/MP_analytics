import aiohttp, asyncio

counter = 0


async def _get_fetch(session, url, id,
                     params=None, headers=None, content_type='text'):
    global counter
    while True:
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status < 200 or response.status >= 300:
                    print(f'\rОбработано: {counter}\tСейчас в обработке: {id}', end=' ')
                else:
                    if content_type.lower() == 'json':
                        result = await response.json()
                        result = [id, result]
                    else:
                        result = await response.text()
                        result = [id, result]
                    counter += 1
                    print(f'\rОбработано: {counter}', end=' ')
                    return result
        except asyncio.exceptions.TimeoutError: pass


async def _post_fetch(session, url, id, body,
                      params=None, headers=None, content_type='text'):
    while True:
        try:
            async with session.post(url, params=params, json=body, headers=headers) as response:
                if response.status < 200 or response.status >= 300: pass
                else:
                    if content_type.lower() == 'json':
                        result = await response.json()
                        result = [id, dict(result)]
                    else:
                        result = await response.text()
                        result = [id, result]
                    global counter
                    counter += 1
                    print(f'\rОбработано: {counter}', end=' ')
                    return result
        except asyncio.exceptions.TimeoutError: pass


async def _fetch_all_tasks_by_urls(http_method, session, url_list, ids,
                                   params=None, body=None, headers=None, content_type='text'):
    tasks = list()
    if len(url_list) != len(ids): raise IndexError("Length of urls list must be equal to ids list.")

    if http_method.lower() == 'get':
        for i in range(len(url_list)):
            task = asyncio.create_task(_get_fetch(session, url_list[i], ids[i],
                                                  params=params,
                                                  headers=headers,
                                                  content_type=content_type))
            tasks.append(task)
    elif http_method.lower() == 'post':
        for i in range(len(url_list)):
            task = asyncio.create_task(_post_fetch(session, url_list[i], ids[i], body,
                                                   params=params,
                                                   headers=headers,
                                                   content_type=content_type))
            tasks.append(task)
    else: pass
    results = await asyncio.gather(*tasks)
    return results


async def _fetch_all_tasks_by_params(http_method, session, url, params_list, ids,
                                     body=None, headers=None, content_type='text'):
    tasks = list()
    if len(params_list) != len(ids): raise IndexError("Length of params list must be equal to ids list.")
    if http_method.lower() == 'get':
        for i in range(len(params_list)):
            task = asyncio.create_task(_get_fetch(session, url, ids[i],
                                                  params=params_list[i],
                                                  headers=headers,
                                                  content_type=content_type))
            tasks.append(task)
    elif http_method.lower() == 'post':
        for i in range(len(params_list)):
            task = asyncio.create_task(_post_fetch(session, url, ids[i], body,
                                                   params=params_list[i],
                                                   headers=headers,
                                                   content_type=content_type))
            tasks.append(task)
    else: pass
    results = await asyncio.gather(*tasks)
    return results


async def _fetch_all_tasks_by_headers(http_method, session, url, headers_list, ids,
                                      params=None, body=None, content_type='text'):
    tasks = list()
    if len(headers_list) != len(ids): raise IndexError("Length of headers list must be equal to ids list.")
    if http_method.lower() == 'get':
        for i in range(len(headers_list)):
            task = asyncio.create_task(_get_fetch(session, url, ids[i],
                                                  params=params,
                                                  headers=headers_list[i],
                                                  content_type=content_type))
            tasks.append(task)
    elif http_method.lower() == 'post':
        for i in range(len(headers_list)):
            task = asyncio.create_task(_post_fetch(session, url, ids[i], body,
                                                   params=params,
                                                   headers=headers_list[i],
                                                   content_type=content_type))
            tasks.append(task)
    else: pass
    results = await asyncio.gather(*tasks)
    return results


async def _fetch_all_tasks_by_bodies(http_method, session, url, bodies_list, ids,
                                     params=None, headers=None, content_type='text'):
    tasks = list()
    if len(bodies_list) != len(ids): raise IndexError("Length of headers list must be equal to ids list.")
    if http_method.lower() == 'get':
        for i in range(len(bodies_list)):
            task = asyncio.create_task(_get_fetch(session, url, ids[i],
                                                  params=params,
                                                  headers=headers,
                                                  content_type=content_type))
            tasks.append(task)
    elif http_method.lower() == 'post':
        for i in range(len(bodies_list)):
            task = asyncio.create_task(_post_fetch(session, url, ids[i], bodies_list[i],
                                                   params=params,
                                                   headers=headers,
                                                   content_type=content_type))
            tasks.append(task)
    else: pass
    results = await asyncio.gather(*tasks)
    return results


async def _fetch_all_by_urls(http_method, url_list, ids,
                             params=None, body=None, headers=None, content_type='text'):
    global counter
    counter = 0
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        print(f"Подключение к {url_list[0].split('//')[1].split('/')[0]}...")
        print(f"Всего запросов: {len(url_list)}")
        result_list = await _fetch_all_tasks_by_urls(http_method, session, url_list, ids,
                                                     params=params,
                                                     body=body,
                                                     headers=headers,
                                                     content_type=content_type)
        result_dict = {item[0]: item[1] for item in result_list}
        print()
        return result_dict


async def _fetch_all_by_params(http_method, url, params_list, ids,
                               body=None, headers=None, content_type='text'):
    global counter
    counter = 0
    async with aiohttp.ClientSession() as session:
        print(f"Подключение к {url.split('//')[1].split('/')[0]}...")
        print(f"Всего запросов: {len(params_list)}")
        result_list = await _fetch_all_tasks_by_params(http_method, session, url, params_list, ids,
                                                       body=body,
                                                       headers=headers,
                                                       content_type=content_type)
        result_dict = {item[0]: item[1] for item in result_list}
        print()
        return result_dict


async def _fetch_all_by_headers(http_method, url, headers_list, ids,
                                params=None, body=None, content_type='text'):
    global counter
    counter = 0
    async with aiohttp.ClientSession() as session:
        print(f"Подключение к {url.split('//')[1].split('/')[0]}...")
        print(f"Всего запросов: {len(headers_list)}")
        result_list = await _fetch_all_tasks_by_headers(http_method, session, url, headers_list, ids,
                                                        params=params,
                                                        body=body,
                                                        content_type=content_type)
        result_dict = {item[0]: item[1] for item in result_list}
        print()
        return result_dict


async def _fetch_all_by_bodies(http_method, url, bodies_list, ids,
                               params=None, headers=None, content_type='text'):
    global counter
    counter = 0
    async with aiohttp.ClientSession() as session:
        print(f"Подключение к {url.split('//')[1].split('/')[0]}...")
        print(f"Всего запросов: {len(bodies_list)}")
        result_list = await _fetch_all_tasks_by_bodies(http_method, session, url, bodies_list, ids,
                                                       params=params,
                                                       headers=headers,
                                                       content_type=content_type)
        result_dict = {item[0]: item[1] for item in result_list}
        print()
        return result_dict


def by_urls(http_method, url_list, ids,
            params=None, body=None, headers=None, content_type='text'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    while True:
        try: return asyncio.run(_fetch_all_by_urls(http_method, url_list, ids,
                                                   body=body,
                                                   params=params,
                                                   headers=headers,
                                                   content_type=content_type))
        except aiohttp.ClientConnectorError:
            print(f"Не удалось подключиться к {url_list[0].split('//')[1].split('/')[0]}...")
        except aiohttp.ClientPayloadError:
            print(f"Не удалось подключиться к {url_list[0].split('//')[1].split('/')[0]}...")


def by_params(http_method, url, params_list, ids,
              body=None, headers=None, content_type='text'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    while True:
        try: return asyncio.run(_fetch_all_by_params(http_method, url, params_list, ids,
                                                     body=body,
                                                     headers=headers,
                                                     content_type=content_type))
        except aiohttp.ClientConnectorError:
            print(f"Не удалось подключиться к {url.split('//')[1].split('/')[0]}...")
        except aiohttp.ClientPayloadError:
            print(f"Не удалось подключиться к {url.split('//')[1].split('/')[0]}...")


def by_headers(http_method, url, headers_list, ids,
               params=None, body=None, content_type='text'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    while True:
        try: return asyncio.run(_fetch_all_by_headers(http_method, url, headers_list, ids,
                                                      params=params,
                                                      body=body,
                                                      content_type=content_type))
        except aiohttp.ClientConnectorError:
            print(f"Не удалось подключиться к {url.split('//')[1].split('/')[0]}...")
        except aiohttp.ClientPayloadError:
            print(f"Не удалось подключиться к {url.split('//')[1].split('/')[0]}...")


def by_bodies(http_method, url, bodies_list, ids,
              params=None, headers=None, content_type='text'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    while True:
        try: return asyncio.run(_fetch_all_by_bodies(http_method, url, bodies_list, ids,
                                                     params=params,
                                                     headers=headers,
                                                     content_type=content_type))
        except aiohttp.ClientConnectorError:
            print(f"Не удалось подключиться к {url.split('//')[1].split('/')[0]}...")
        except aiohttp.ClientPayloadError:
            print(f"Не удалось подключиться к {url.split('//')[1].split('/')[0]}...")
