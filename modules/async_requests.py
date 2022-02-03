import aiohttp, asyncio

counter = 0

async def _get_fetch(session, url, id, params=None, headers=None, content_type='text'):
    while (True):
        try:
            async with session.get(url, params=params, headers=headers) as response:
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
                    print(f'\rОбработано: {counter}' , end=' ')
                    return result
        except asyncio.exceptions.TimeoutError: pass

async def _get_fetch_all_by_urls(session, url_list, ids, params=None, headers=None, content_type='text'):
    tasks = list()
    if len(url_list) != len(ids): raise IndexError("Length of urls list must be equal to ids list.")
    for i in range(len(url_list)):
        task = asyncio.create_task(_get_fetch(session, url_list[i], id=ids[i],
                                              params=params,
                                              headers=headers,
                                              content_type=content_type))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

async def _get_fetch_all_by_params(session, url, params_list, ids, headers=None, content_type='text'):
    tasks = list()
    if len(params_list) != len(ids): raise IndexError("Length of params list must be equal to ids list.")
    for i in range(len(params_list)):
        task = asyncio.create_task(_get_fetch(session, url,
                                              params=params_list[i], id=ids[i],
                                              headers=headers,
                                              content_type=content_type))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

async def _fetch_all_by_urls(http_method, url_list, ids, params=None, headers=None, content_type='text'):
    global counter
    counter = 0
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        print(f"\nПодключение к {url_list[0].split('//')[1].split('/')[0]}...")
        print(f"Всего запросов: {len(url_list)}")
        if http_method.lower() == 'get':
            result_list = await _get_fetch_all_by_urls(session, url_list, ids,
                                                       params=params,
                                                       headers=headers,
                                                       content_type=content_type)
        elif http_method.lower() == 'post': pass
        else: pass
        result_dict = {item[0] : item[1] for item in result_list}
        return result_dict

async def _fetch_all_by_params(http_method, url, params_list, ids, headers=None, content_type='text'):
    global counter
    counter = 0
    async with aiohttp.ClientSession() as session:
        print(f"Подключение к {url.split('//')[1].split('/')[0]}...")
        print(f"Всего запросов: {len(params_list)}")
        if http_method.lower() == 'get':
            result_list = await _get_fetch_all_by_params(session, url, params_list, ids,
                                                         headers=headers,
                                                         content_type=content_type)
        elif http_method.lower() == 'post': pass
        else: pass
        result_dict = {item[0]: item[1] for item in result_list}
        return result_dict

def by_urls(http_method, url_list, ids, params=None, headers=None, content_type='text'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    while (True):
        try:
            return asyncio.run(_fetch_all_by_urls(http_method, url_list, ids,
                                                  params=params,
                                                  headers=headers,
                                                  content_type=content_type))
        except aiohttp.ClientConnectorError:
            print(f"Не удалось подключиться к {url_list[0].split('//')[1].split('/')[0]}...")

def by_params(http_method, url, params_list, ids, headers=None, content_type='text'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    return asyncio.run(_fetch_all_by_params(http_method, url, params_list, ids,
                                            headers=headers,
                                            content_type=content_type))
