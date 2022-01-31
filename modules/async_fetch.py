import aiohttp, asyncio
from datetime import date, timedelta

counter = 0

async def _get_fetch(session, url, params=None, headers=None, additional_id=None, content_type='text'):
    while (True):
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200: pass
                else:
                    if content_type.lower() == 'json':
                        result = await response.json()
                        if additional_id is not None:
                            result = dict(result)
                            result['id'] = additional_id
                    else:
                        result = await response.text()
                        if additional_id is not None:
                            result = [additional_id, result]
                    global counter
                    counter += 1
                    if additional_id is not None: print(f'\rОбработано: {counter}' , end=' ')
                    else: print(f'\rОбработано: {counter}' , end=' ')
                    return result
        except asyncio.exceptions.TimeoutError: pass

async def _get_fetch_all_by_urls(session, url_list, params=None, headers=None, additional_ids=None, content_type='text'):
    tasks = list()
    if additional_ids is not None:
        if len(url_list) != len(additional_ids): raise IndexError("Length of urls list must be equal to ids list.")
        for i in range(len(url_list)):
            task = asyncio.create_task(_get_fetch(session, url_list[i],
                                                  params=params,
                                                  headers=headers,
                                                  additional_id=additional_ids[i],
                                                  content_type=content_type))
            tasks.append(task)
    else:
        for url in url_list:
            task = asyncio.create_task(_get_fetch(session, url,
                                                  params=params,
                                                  headers=headers,
                                                  content_type=content_type))
            tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

async def _get_fetch_all_by_params(session, url, params_list, headers=None, additional_ids=None, content_type='text'):
    tasks = list()
    if additional_ids is not None:
        if len(params_list) != len(additional_ids): raise IndexError("Length of params list must be equal to ids list.")
        for i in range(len(params_list)):
            task = asyncio.create_task(_get_fetch(session, url,
                                                  params=params_list[i],
                                                  headers=headers,
                                                  additional_id=additional_ids[i],
                                                  content_type=content_type))
            tasks.append(task)
    else:
        for params in params_list:
            task = asyncio.create_task(_get_fetch(session, url,
                                                  params=params,
                                                  headers=headers,
                                                  content_type=content_type))
            tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

async def _fetch_all_by_urls(http_method, url_list, params=None, headers=None, additional_ids=None, content_type='text'):
    global counter
    counter = 0
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        print(f"\nПодключение к {url_list[0].split('//')[1].split('/')[0]}...")
        print(f"Всего запросов: {len(url_list)}")
        if http_method.lower() == 'get':
            result_list = await _get_fetch_all_by_urls(session,
                                                       url_list,
                                                       params=params,
                                                       headers=headers,
                                                       additional_ids=additional_ids,
                                                       content_type=content_type)
        elif http_method.lower() == 'post': pass
        else: pass
        return result_list

async def _fetch_all_by_params(http_method, url, params_list, headers=None, additional_ids=None, content_type='text'):
    global counter
    counter = 0
    async with aiohttp.ClientSession() as session:
        print(f"Подключение к {url.split('//')[1].split('/')[0]}...")
        print(f"Всего запросов: {len(params_list)}")
        if http_method.lower() == 'get':
            result_list = await _get_fetch_all_by_params(session,
                                                         url,
                                                         params_list,
                                                         headers=headers,
                                                         additional_ids=additional_ids,
                                                         content_type=content_type)
        elif http_method.lower() == 'post': pass
        else: pass
        return result_list

def by_urls(http_method, url_list, params=None, headers=None, additional_ids=None, content_type='text'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    while (True):
        try:
            return asyncio.run(_fetch_all_by_urls(http_method,
                                                  url_list,
                                                  params=params,
                                                  headers=headers,
                                                  additional_ids=additional_ids,
                                                  content_type=content_type))
        except aiohttp.ClientConnectorError:
            print(f"Не удалось подключиться к {url_list[0].split('//')[1].split('/')[0]}...")

def by_params(http_method, url, params_list, headers=None, additional_ids=None, content_type='text'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    return asyncio.run(_fetch_all_by_params(http_method,
                                            url,
                                            params_list,
                                            headers=headers,
                                            additional_ids=additional_ids,
                                            content_type=content_type))
