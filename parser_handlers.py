import asyncio
import json
import string
import re
import datetime
import aiohttp
from aiogram import types
from io import BytesIO

import bot
from config import *
from states import *
from aiogram.dispatcher import FSMContext
import parser_olx_ua
import time
import random
from main_keyboards import *
import requests


@dp.callback_query_handler(lambda c: c.data == 'add_token', state='*')
async def add_token_inline_handler(call: types.CallbackQuery):
    await AddToken.add_token.set()
    await bot.send_message(call.from_user.id, 'Введите токен', reply_markup=kb_cancel)


@dp.message_handler(lambda m: 39 < len(m.text) < 100, state=AddToken.add_token)
async def add_token_handler(message: types.Message, state: FSMContext):
    await state.finish()
    result = DB.add_token(message.from_user.id, message.text)
    if result:
        await message.answer('Токен успешно добавлен.', reply_markup=kb_return_to_main_menu)
    else:
        await message.answer('Этот токен уже кто-то использует.', reply_markup=kb_return_to_main_menu)


@dp.message_handler(lambda m: len(m.text) > 99 or len(m.text) < 40, state=AddToken.add_token)
async def add_token_error_handler(message: types.Message):
    await message.answer('Введите корректный токен или отмените операцию', reply_markup=kb_cancel)


def get_kb_for_category(new_categories):
    kb_category_parsing_inline = types.InlineKeyboardMarkup(row_width=1)
    kb_category_parsing_inline.add(
        types.InlineKeyboardButton(f'{"✅" if "36" in new_categories else "❌"} Детский мир',
                                   callback_data='change_enable_category&36'))
    kb_category_parsing_inline.add(
        types.InlineKeyboardButton(f'{"✅" if "3" in new_categories else "❌"} Запчасти для транспорта',
                                   callback_data='change_enable_category&3'))
    kb_category_parsing_inline.add(types.InlineKeyboardButton(f'{"✅" if "899" in new_categories else "❌"} Дом и сад',
                                                              callback_data='change_enable_category&899'))
    kb_category_parsing_inline.add(types.InlineKeyboardButton(f'{"✅" if "37" in new_categories else "❌"} Электроника',
                                                              callback_data='change_enable_category&37'))
    kb_category_parsing_inline.add(types.InlineKeyboardButton(f'{"✅" if "891" in new_categories else "❌"} Мода и стиль',
                                                              callback_data='change_enable_category&891'))
    kb_category_parsing_inline.add(
        types.InlineKeyboardButton(f'{"✅" if "903" in new_categories else "❌"} Хобби, отдых и спорт',
                                   callback_data='change_enable_category&903'))
    kb_category_parsing_inline.add(types.InlineKeyboardButton('Назад', callback_data='back_to_main_menu'))
    return kb_category_parsing_inline


@dp.callback_query_handler(lambda c: c.data == 'view_parsing_category', state='*')
async def view_parsing_category_inline_handler(call: types.CallbackQuery):
    user = DB.get_user(call.from_user.id)
    kb = get_kb_for_category(user[9].split('&'))
    await bot.send_message(call.from_user.id, '👉🏼 <b>Выбери категорию:</b>', reply_markup=kb,
                           parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(lambda c: c.data.startswith('change_enable_category'), state='*')
async def change_enable_category_inline_handler(call: types.CallbackQuery):
    category = call.data.split('&')[1]
    user = list(DB.get_user(call.from_user.id))
    all_category = list(filter(lambda el: bool(el), user[9].split('&')))
    if category in all_category:
        all_category.remove(category)
    else:
        all_category.append(category)
    new_category = '&'.join(all_category)
    DB.set_new_parse_category(call.from_user.id, new_category)
    kb = get_kb_for_category(all_category)
    await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data == 'parsing_start', state='*')
async def parsing_start_inline_handler(call: types.CallbackQuery):
    user = DB.get_user(call.from_user.id)
    if datetime.datetime.now() < user[2] or call.from_user.id in ADMINS:
        if not user[1] or call.from_user.id in ADMINS:
            if user[9]:
                price_min, price_max = user[4].split('-')[:2]
                registration_seller = datetime.datetime.now() - datetime.timedelta(days=user[3])
                create_announce = datetime.datetime.now() - datetime.timedelta(minutes=user[6])
                data = DB.selection_of_announces(price_min, price_max, registration_seller, user[5], create_announce,
                                                 user[9].split('&'))
                pack = {'data': []}
                if data and len(data) > 0 and data[0]:
                    for i in data:
                        ids = list(map(lambda el: str(el[0]), data))
                        #DB.save_browsing_announces(ids)

                        local_data = {
                            'title': i[1],
                            'price_value': str(i[2]),
                            'price_currency': i[3],
                            'description': i[4],
                            'city': i[5],
                            'region': i[6],
                            'create_announce': f"{i[7].year}-{i[7].month}-{i[7].day} {i[7].hour}:{i[7].minute}:{i[7].second}",
                            'photo': i[9],
                            'amount_delivery': str(i[11]),
                            'page_id': str(i[10]),
                            'contact_name': i[12],
                            'url': i[14],
                            'phone': str(i[15]),
                            'announce_id': i[0]
                        }
                        pack['data'].append(local_data)
                    filename_id = f"{int(time.time())}_{''.join(random.choices(string.ascii_lowercase, k=5))}"
                    DB.set_new_filename_in_last_parse(call.from_user.id, filename_id)
                    with open(f'data/jsons/{filename_id}.json', 'w', encoding='utf-8') as f:
                        json.dump(pack, f)
                    text = get_text_for_announce_in_parser(pack['data'][0], user[7], data[0][0])
                    kb = types.InlineKeyboardMarkup()
                    if not data[0][15].isdigit():
                        kb.row(types.InlineKeyboardButton('Показать телефон',
                                                          callback_data=f'view_phone&{data[0][10]}&{filename_id}&0'))
                    kb.row(types.InlineKeyboardButton(f"1/{len(data)}", callback_data=f'none'),
                           types.InlineKeyboardButton('>>>', callback_data=f'parser_next_announce&{filename_id}&0'))
                    await bot.send_photo(call.from_user.id, pack['data'][0]['photo'], caption=text, reply_markup=kb,
                                         parse_mode=types.ParseMode.HTML)
            else:
                await call.answer('Выберите категории для парсинга в главном меню', show_alert=True)
        else:
            await call.answer('Дождитесь пока предыдущий парсинг закончится', show_alert=True)
    else:
        await call.answer('Приобретите подписку для использования функций парсера', show_alert=True)


def get_text_for_announce_in_parser(announce: dict, auto_text_template: str, announce_id: int = None) -> str:
    def process_phone(phone: str):
        if phone:
            if phone == 'null':
                phone = 'Продавец скрыл номер'
            elif phone == 'none_active':
                phone = 'Объявление не активно'
            elif phone == 'incorrect':
                phone = 'Телефон, который указал продавец, некорректен'
        else:
            phone = 'Не загружен'
        return phone

    phone = process_phone(announce.get('phone'))
    views = None
    # мб потом добавить {f"Количество просмотров этого объявления: {views}" if views is not None else ''}
    if announce_id is not None:
        announce_db = DB.get_announce(announce_id)
        if announce_db:
            views = announce_db[16]
            if phone == 'Не загружен':
                phone = process_phone(announce_db[15])
    auto_text = auto_text_template.replace('[link]', announce.get('url')).replace('[title]', re.sub('<[^<]+?>', '',
                                                                                                    announce.get(
                                                                                                        'title'))).replace(
        '[name]', announce.get('contact_name')).replace('[price]',
                                                        announce.get('price_value')).replace(' ', '+')
    text = f"""
🧳<b>Товар</b>: {re.sub('<[^<]+?>', '', announce.get('title'))}
💎<b>Цена</b >: {re.sub('<[^<]+?>', '', announce.get('price_value'))} {re.sub('<[^<]+?>', '', announce.get('price_currency'))}
🖨<b>Описание</b>: {re.sub('<[^<]+?>', '', announce.get('description'))}
<b>Дата</b>: {announce.get('create_announce')}
<b>Местоположение</b>: {re.sub('<[^<]+?>', '', announce.get('city'))}, {re.sub('<[^<]+?>', '', announce.get('region'))}
<b>Количество успешных доставок</b>: {announce.get('amount_delivery')} 


📱<b>Номер телефона</b>: {phone}
⚙️<b>Мессенджеры</b>: {f'<a href="https://wa.me/{phone}">WhatsApp</a> / <a href="https://viber.click/{phone}">Viber</a>' if phone.isdigit() else phone}
📃<b>Автотекст</b>: {f'<a href="https://api.whatsapp.com/send?phone={phone}&text={auto_text}">Связаться</a> / <a href="https://web.whatsapp.com/send?phone={phone}&text={auto_text}">Web</a>' if auto_text != '!' and phone.isdigit() else 'Автотекст не настроен'}
⛓<b>Ссылка</b>: <a href="{announce.get('url')}">Перейти</a>       
    """
    return text


@dp.callback_query_handler(lambda c: c.data.startswith('parser_next_announce'), state='*')
async def parser_next_announce_inline_handler(call: types.CallbackQuery, step=1, is_previous=False):
    filename_id, old_index_announce = call.data.split('&')[1:]
    user = DB.get_user(call.from_user.id)
    with open(f'data/jsons/{filename_id}.json', encoding='utf-8') as f:
        announces = json.load(f)
    new_index_announce = int(old_index_announce) + step
    announce = announces['data'][new_index_announce]
    text = get_text_for_announce_in_parser(announce, user[7], announce['announce_id'])
    kb = types.InlineKeyboardMarkup()
    buttons = []
    announce_db = DB.get_announce(announce['announce_id'])
    if not announce.get('phone'):
        if not announce_db or not announce_db[15].isdigit():
            kb.row(types.InlineKeyboardButton('Показать телефон',
                                              callback_data=f'view_phone&{announce.get("page_id")}&{filename_id}&{new_index_announce}'))
    if not is_previous or new_index_announce != 0:
        buttons.append(
            types.InlineKeyboardButton('<<',
                                       callback_data=f'parser_previous_announce&{filename_id}&{new_index_announce}'))
    buttons.append(
        types.InlineKeyboardButton(f"{new_index_announce + 1} / {len(announces['data'])}", callback_data='nothing'))
    if new_index_announce < len(announces['data']) - 1 or is_previous:
        buttons.append(
            types.InlineKeyboardButton('>>', callback_data=f'parser_next_announce&{filename_id}&{new_index_announce}'))
    kb.add(*buttons)
    photo = types.InputFile(BytesIO(requests.get(announce.get('photo')).content))
    await bot.edit_message_media(
        types.InputMediaPhoto(media=photo, type='photo', caption=text, parse_mode=types.ParseMode.HTML),
        call.from_user.id, call.message.message_id, reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith('parser_previous_announce'), state='*')
async def parser_previous_announce_inline_handler(call: types.CallbackQuery):
    await parser_next_announce_inline_handler(call, is_previous=True, step=-1)


@dp.callback_query_handler(lambda c: c.data.startswith('view_phone'), state='*')
async def view_phone_inline_handler(call: types.CallbackQuery):
    page_id, filename_id, index_announce = call.data.split('&')[1:]
    user = DB.get_user(call.from_user.id)
    with open(f'data/jsons/{filename_id}.json', encoding='utf-8') as f:
        announces = json.load(f)
    index_announce = int(index_announce)
    announce = announces['data'][index_announce]
    async with aiohttp.ClientSession() as session:
        token = DB.get_token(call.from_user.id)
        if token:
            phone = await parser_olx_ua.get_phone(session, page_id, token[2])
            if phone == 'token invalid':
                await bot.send_message(call.from_user.id, f"Токен {token[2]} больше не работает.")
                DB.delete_token(token[0])
            elif not phone:
                await bot.send_message(call.from_user.id, f"Токен {token[2]} больше не работает.")
                DB.delete_token(token[0])
            else:
                announce['phone'] = phone
                text = get_text_for_announce_in_parser(announce, user[7], announce['announce_id'])
                kb = types.InlineKeyboardMarkup()
                buttons = []
                if index_announce != 0:
                    buttons.append(types.InlineKeyboardButton('<<',
                                                              callback_data=f'parser_previous_announce&{filename_id}&{index_announce}'))
                buttons.append(types.InlineKeyboardButton(f'{index_announce + 1} / {len(announces["data"])}',
                                                          callback_data='nothing'))
                if index_announce < len(announces['data']) - 1:
                    buttons.append(
                        types.InlineKeyboardButton('>>',
                                                   callback_data=f'parser_next_announce&{filename_id}&{index_announce}'))
                kb.add(*buttons)
                await bot.edit_message_caption(call.from_user.id, call.message.message_id, caption=text,
                                               parse_mode=types.ParseMode.HTML, reply_markup=kb)
                announces['data'][index_announce] = announce
                announce_db = DB.get_announce(announce['announce_id'])
                if announce_db:
                    DB.update_phone_in_announce(phone, announce['announce_id'])
                with open(f'data/jsons/{filename_id}.json', 'w', encoding='utf-8') as f:
                    json.dump(announces, f)
        else:
            await call.answer('Добавьте токен в бота для просмотра номера телефона.', show_alert=True)
