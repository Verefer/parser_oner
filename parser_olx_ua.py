import argparse

import adodbapi.adodbapi
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import time
import datetime
from aiogram import types
from config import *
import random
import phonenumbers
import json

kb_cancel_parsing = types.InlineKeyboardMarkup()
kb_cancel_parsing.add(types.InlineKeyboardButton('Остановить парсинг', callback_data='stop_parsing'))


async def parse_category(category):
    async with aiohttp.ClientSession() as session:
        payload = {
            'view': "",
            'min_id': "",
            'q': "",
            'search[city_id]': "",
            'search[region_id]': "",
            'search[district_id]': "0",
            'search[dist]': "0",
            'search[category_id]': category,
            'search[filter_float_price:from]': 0,
            'search[filter_float_price:to]': 1000000,
            'search[photos]': "1",
            'search[order]': "created_at:desc",
            'page': 1,
            'search[private_business]': "private"
        }
        previous_data_ids = set()
        now_data_ids = set()
        proxy_raw = DB.get_proxy()
        proxy = proxy_raw[1]
        count = 0
        DB.add_proxy_to_timeout(proxy, proxy_raw[0])
        while True:
            try:
                announcements = await get_announcements(payload, session, proxy)
            except Exception as ex:
                print(ex)
                announcements = await get_announcements(payload, session, '')
            if announcements:
                for announce in announcements:
                    if len(announce['class']) == 1:
                        data_id = announce.div.table['data-id']
                        if data_id in previous_data_ids:
                            break
                        print(data_id, payload['page'])
                        now_data_ids.add(data_id)
                        data = await parse_page(session, data_id, proxy)
                        if data and type(data) == tuple:
                            url = announce.div.table.tbody.tr.td.a['href']
                            title, price_value, price_currency, description, city, region, create_announce_date, \
                            dt_create_account, photo_url, page_id, amount_delivery, contact_name = data
                            DB.add_announce(title, price_value, price_currency, description, city, region,
                                            create_announce_date, dt_create_account, photo_url, page_id,
                                            amount_delivery, contact_name, category, url)
                        elif data == -1:
                            continue
                        elif data == -403:
                            proxy_raw = DB.get_proxy()
                            while proxy_raw is None:
                                await asyncio.sleep(5)
                                proxy_raw = DB.get_proxy()
                            proxy = proxy_raw[1]
                            DB.add_proxy_to_timeout(proxy, proxy_raw[0])
                            break
                        else:
                            break
                        count += 1
            else:
                await asyncio.sleep(2)
                proxy_raw = DB.get_proxy()
                while proxy_raw is None:
                    await asyncio.sleep(5)
                    proxy_raw = DB.get_proxy()
                proxy = proxy_raw[1]
                DB.add_proxy_to_timeout(proxy, proxy_raw[0])
            payload['page'] += 1
            previous_data_ids = now_data_ids
            print(f"COUNT: {count}")
            if payload['page'] >= 26:
                payload['page'] = 1


async def get_announcements(data, session, proxy: str):
    page_source = await session.post('https://www.olx.ua/ajax/search/list/', data=data, proxy=proxy)
    soup = BeautifulSoup(await page_source.text(), 'lxml')
    announcements = soup.find_all('td', {"class": 'offer'})
    return announcements


async def get_free_proxy(session: aiohttp.ClientSession):
    res = await session.get('https://www.sslproxies.org/')
    soup = BeautifulSoup(await res.text(), 'lxml')
    tbody = soup.find_all('tbody')
    proxies = []
    proxies_local = []
    for i in tbody[0].find_all('td'):
        text = i.text.strip('<td>').strip('</td>').strip()
        if text:
            if text[-1].isdigit() and len(proxies_local) == 1:
                proxies_local.append(text)
                proxies.append(':'.join(proxies_local))
                proxies_local = []
            elif text[-1].isdigit() and not len(proxies_local):
                proxies_local.append(text)
    return 'http://' + random.choice(proxies[:50])


async def get_phone(session: aiohttp.ClientSession, page_id, token):
    headers = {
        'Authorization': f"Bearer {token}"
    }
    data = await session.get(f'https://www.olx.ua/api/v1/offers/{page_id}/limited-phones/', headers=headers)
    headers_authenticate = data.headers.get('WWW-Authenticate')
    if headers_authenticate is not None:
        error_description = headers_authenticate.split('error_description=')[1]
        error = error_description.strip('"')
        if error == 'The access token provided is invalid':
            return 'token invalid'
    try:
        data_json: dict = await data.json()
        print(data_json)
    except Exception as ex:
        print(ex)
        return ''
    try:
        phone = data_json.get('data')
        if phone is not None:
            if len(phone['phones']) == 0:
                return 'null'
            else:
                phone = phone['phones'][0].replace(' ', '')
                phone = phonenumbers.format_number(phonenumbers.parse(phone, 'UA'),
                                                   phonenumbers.PhoneNumberFormat.E164)
                phone = phone.replace('+', '')
                if len(phone) > 15:
                    phone = 'incorrect'
        else:
            error = data_json.get('error').get('detail')
            if error == 'Ad is not active':
                return 'none_active'
            return ''
    except Exception as ex:
        print(ex)
        phone = ''
    return phone


async def get_amount_delivery(session: aiohttp.ClientSession, user_id, proxy):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0',
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Origin': "https://www.olx.ua",
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
    }
    r = await session.get(f'https://khonor.prd.01.eu-west-1.eu.olx.org/api/olx/ua/user/{user_id}/badge/delivery',
                          headers=headers, proxy=proxy)
    try:
        data = await r.json()
        amount = data.get('body')[0].get('data').get('amount')
        return int(amount)
    except Exception as ex:
        print(ex)
        return 0


async def parse_page(session: aiohttp.ClientSession, page_id, proxy):
    try:
        data = await session.get(f"https://www.olx.ua/api/v1/offers/{page_id}", proxy=proxy, timeout=3)
        if data.status != 403:
            data = await data.json()
        else:
            return -403  # fraud error, change proxy
    except Exception as ex:
        print(ex)
        return -100  # kill process,
    try:
        contact_have_phone = data['data']['contact']['phone']
        if contact_have_phone is False or contact_have_phone == 'false':
            return -1
        create_account_date = data['data']['user']['created']
        dt_create_account = datetime.datetime.strptime(create_account_date, '%Y-%m-%dT%H:%M:%S%z').astimezone()
        user_id = data['data']['user']['id']
        create_announce_date = datetime.datetime.strptime(data['data']['last_refresh_time'],
                                                          '%Y-%m-%dT%H:%M:%S%z').astimezone()
        amount_delivery = await get_amount_delivery(session, user_id, proxy)
        print(user_id)
        title = data['data']['title']
        price_value = data['data']['params'][0]['value']['value']
        price_currency = data['data']['params'][0]['value']['currency']
        description = data['data']['description'].split('<br />')[0][:100]
        photo_url = data['data']['photos'][0]['link'].replace('{width}', '600').replace('{height}', '600')
        location = data['data']['location']
        city = location['city']['name']
        region = location['region']['name']
        contact_name = data['data']['contact']['name']
        return title, price_value, price_currency, description, city, region, create_announce_date, \
               dt_create_account, photo_url, page_id, amount_delivery, contact_name
    except Exception as ex:
        print(ex)
        return -1


async def start_parsing():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str, help='command to execute [parse, schedules]')
    # parse - парсит объявления по категории
    # schedules - включает по расписаниям функции
    parser.add_argument('--category', default=0, type=int)
    args = parser.parse_args()
    if args.command == 'parse':
        print(f'Парсер по категории {args.category} запущен.')
        await parse_category(args.category)
    elif args.command == 'schedules':
        scheduler = AsyncIOScheduler()
        scheduler.add_job(DB.delete_olds_announces, 'interval', args=(300,), seconds=10)
        scheduler.add_job(DB.revive_proxies, 'interval', args=(3,), seconds=4)
        scheduler.start()
        while True:
            print('schedules работают')
            await asyncio.sleep(5)
    else:
        print('Unexpected command')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_parsing())
    # loop.run_until_complete(parse_category(0))

# with open('data/jsons/test.json', encoding='utf-8') as f:
#     print(json.load(f))
