import aiohttp, asyncio, httpx

counter = 0

async def _get_fetch(session, id, content_type, lib, url, params, headers):
    global counter
    individual_session = False
    if lib == 'httpx':
        while True:
            try:
                response = await session.get(url, params=params, headers=headers)
                if response.status_code < 200 or response.status_code >= 300:
                    print(f'\rОбработано: {counter}\tСейчас в обработке: {id}', end=' ')
                else:
                    if content_type.lower() == 'json': result = response.json()
                    else: result = response.text
                    counter += 1
                    print(f'\rОбработано: {counter}', end=' ')
                    if individual_session: session.close()
                    return [id, result]
            except httpx.TimeoutException: pass
            except (httpx.NetworkError, RuntimeError):
                print(f"\rПереподключение к {url.split('//')[1].split('/')[0]}...", end=' ')
                if individual_session: session.close()
                timeout = httpx.Timeout(timeout=20.0)
                session = httpx.AsyncClient(timeout=timeout)
                individual_session = True
    else:
        while True:
            try:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status < 200 or response.status >= 300:
                        print(f'\rОбработано: {counter}\tСейчас в обработке: {id}', end=' ')
                    else:
                        if content_type.lower() == 'json': result = await response.json()
                        else: result = await response.text()
                        counter += 1
                        print(f'\rОбработано: {counter}', end=' ')
                        if individual_session: await session.close()
                        return [id, result]
            except asyncio.exceptions.TimeoutError: pass
            except (aiohttp.ClientError, RuntimeError):
                print(f"\rПереподключение к {url.split('//')[1].split('/')[0]}...", end=' ')
                if individual_session: await session.close()
                timeout = aiohttp.ClientTimeout(total=20)
                session = aiohttp.ClientSession(timeout=timeout)
                individual_session = True



async def _post_fetch(session, id, body, content_type, lib, url, params, headers):
    global counter
    individual_session = False
    if lib == 'httpx':
        while True:
            try:
                response = await session.post(url, params=params, json=body, headers=headers)
                if response.status_code < 200 or response.status_code >= 300:
                    print(f'\rОбработано: {counter}\tСейчас в обработке: {id}', end=' ')
                else:
                    if content_type.lower() == 'json': result = response.json()
                    else: result = response.text
                    counter += 1
                    print(f'\rОбработано: {counter}', end=' ')
                    if individual_session: session.close()
                    return [id, result]
            except httpx.TimeoutException: pass
            except httpx.NetworkError:
                print(f"\rПереподключение к {url.split('//')[1].split('/')[0]}...", end=' ')
                if individual_session: session.close()
                timeout = httpx.Timeout(timeout=20.0)
                session = httpx.AsyncClient(timeout=timeout)
                individual_session = True
    else:
        while True:
            try:
                async with session.post(url, params=params, json=body, headers=headers) as response:
                    if response.status < 200 or response.status >= 300: pass
                    else:
                        if content_type.lower() == 'json': result = await response.json()
                        else: result = await response.text()
                        counter += 1
                        print(f'\rОбработано: {counter}', end=' ')
                        if individual_session: await session.close()
                        return [id, result]
            except asyncio.exceptions.TimeoutError: pass
            except (aiohttp.ClientError, RuntimeError):
                print(f"\rПереподключение к {url.split('//')[1].split('/')[0]}...", end=' ')
                if individual_session: await session.close()
                timeout = aiohttp.ClientTimeout(total=20)
                session = aiohttp.ClientSession(timeout=timeout)
                individual_session = True


async def _fetch_all_tasks(http_method, session, ids,
                           content_type='text', lib='aiohttp',
                           url=None, urls_list=None,
                           body=None, bodies_list=None,
                           params=None, params_list=None,
                           headers=None, headers_list=None):
    if urls_list is not None: print(f"Подключение к {urls_list[0].split('//')[1].split('/')[0]}...")
    else: print(f"Подключение к {url.split('//')[1].split('/')[0]}...")
    print(f"Всего запросов: {len(ids)}")
    tasks = list()
    for i in range(len(ids)):
        if urls_list is not None: task_url = urls_list[i]
        else: task_url = url
        if headers_list is not None: task_headers = headers_list[i]
        else: task_headers = headers
        if params_list is not None: task_params = params_list[i]
        else: task_params = params
        if bodies_list is not None: task_body = bodies_list[i]
        else: task_body = body
        if http_method.lower() == 'get':
            tasks.append(asyncio.create_task(_get_fetch(session, ids[i],
                                     content_type=content_type, lib=lib,
                                     url=task_url, params=task_params, headers=task_headers)))
        elif http_method.lower() == 'post':
            tasks.append(asyncio.create_task(_post_fetch(session, ids[i],
                                      body=task_body, content_type=content_type, lib=lib,
                                      url=task_url, params=task_params, headers=task_headers)))
    results = await asyncio.gather(*tasks)
    print()
    return results


async def _fetch_all(http_method, ids, content_type='text', lib='aiohttp',
                     url=None, urls_list=None,
                     body=None, bodies_list=None,
                     params=None, params_list=None,
                     headers=None, headers_list=None):
    global counter
    counter = 0
    if lib == 'httpx':
        timeout = httpx.Timeout(timeout=20.0)
        async with httpx.AsyncClient(timeout=timeout) as session:
            result_list = await _fetch_all_tasks(http_method, session, ids,
                                                 url=url, urls_list=urls_list,
                                                 content_type=content_type, lib=lib,
                                                 body=body, bodies_list=bodies_list,
                                                 params=params, params_list=params_list,
                                                 headers=headers, headers_list=headers_list)
    else:
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            result_list = await _fetch_all_tasks(http_method, session, ids,
                                                 url=url, urls_list=urls_list,
                                                 content_type=content_type, lib=lib,
                                                 body=body, bodies_list=bodies_list,
                                                 params=params, params_list=params_list,
                                                 headers=headers, headers_list=headers_list)
    return {item[0]: item[1] for item in result_list}


def fetch(http_method, ids, content_type='text', lib='aiohttp',
          url=None, urls_list=None,
          body=None, bodies_list=None,
          params=None, params_list=None,
          headers=None, headers_list=None):
    for iter_list in [bodies_list, params_list, headers_list, urls_list]:
        if iter_list is not None and len(iter_list) != len(ids):
            raise IndexError("Length of iterable list must be equal to ids list.")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    return asyncio.run(_fetch_all(http_method, ids, content_type=content_type, lib=lib,
                                  url=url, urls_list=urls_list,
                                  body=body, bodies_list=bodies_list,
                                  params=params, params_list=params_list,
                                  headers=headers, headers_list=headers_list))