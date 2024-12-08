from aiogram import types
from config import *
import time
import json
import datetime
from parser_handlers import get_text_for_announce_in_parser
import requests
from aiogram.dispatcher import FSMContext


@dp.callback_query_handler(lambda c: c.data == 'view_announces', state='*')
async def view_announces_inline_handler(call: types.CallbackQuery):
    filename_row = DB.get_filename_from_last_parse(call.from_user.id)
    if filename_row is None:
        await call.answer('Объявлений еще не было.', show_alert=True)
    else:
        with open(f'data/jsons/{filename_row[1]}.json', encoding='utf-8') as f:
            data = json.load(f)
        user = DB.get_user(call.from_user.id)
        first_announce = data['data'][0]
        length_announces = len(data['data'])
        kb = types.InlineKeyboardMarkup()
        if not first_announce['phone']:
            kb.row(
                types.InlineKeyboardButton('Показать телефон',
                                           callback_data=f'view_phone&{first_announce.get("page_id")}&{filename_row[1]}&0'))
        if length_announces > 1:
            kb.add(types.InlineKeyboardButton('>>', callback_data=f'parser_next_announce&{filename_row[1]}&0'))
        text = get_text_for_announce_in_parser(first_announce, user[7])
        await bot.send_photo(call.from_user.id, requests.get(first_announce.get('photo')).content, caption=text,
                             reply_markup=kb, parse_mode=types.ParseMode.HTML)
