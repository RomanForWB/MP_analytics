from datetime import date, datetime, timedelta
import modules.ozon.analytics as ozon_analytics
import modules.ozon.info as ozon_info
import requests
import httpx
import asyncio

url = 'https://api-seller.ozon.ru/v2/category/tree'
headers = {'Client-Id': ozon_info.client_id(ozon_info.all_suppliers()[0]),
           'Api-Key': ozon_info.api_key(ozon_info.all_suppliers()[0]),
           'Content-Type': 'application/json'}
categories_ids = [17033665, 93726157, 17033665, 93726157, 17033665, 93726157, 17033665, 93726157, 17033665, 93726157, 17033665, 93726157, 17033665, 93726157, 17033665, 93726157, 17033665, 93726157, 17033665, 93726157, 17033665, 93726157, 17033665]

# url = 'https://www.wildberries.ru/'


async def fetch3(session, body):
    print(body)
    response = await session.post(url, headers=headers, json=body)
    result = response.json()
    return result


async def fetch2(session):
    tasks = list()
    bodies_list = [{'category_id': category_id} for category_id in categories_ids]
    for i in range(len(bodies_list)):
        task = asyncio.create_task(fetch3(session, bodies_list[i]))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results



async def fetch1():
    async with httpx.AsyncClient() as session:
        result_list = await fetch2(session)
    return result_list

def trying():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    return asyncio.run(fetch1())


if __name__ == '__main__':
    print(trying())