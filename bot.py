from aiogram import types
from config import *
from aiogram.dispatcher import FSMContext
import logging


# logging.basicConfig(level=logging.INFO)


@dp.message_handler(lambda m: m.text in ['Отмена', 'Вернуться в главное меню'], state='*')
@dp.callback_query_handler(lambda c: c.data == 'back_to_main_menu', state='*')
async def cancel_main_keyboard_handler(message: types.Message, state: FSMContext):
    await state.finish()
    if message.from_user.id not in DB.ALL_IDs_FROM_DB:
        DB.add_user(message.from_user.id)
        time.sleep(0.5)
        line = message.text.split()
        if len(line) == 2:
            if line[1].isdigit():
                if int(line[1]) in DB.ALL_IDs_FROM_DB:
                    DB.set_referer_id(message.from_user.id, int(line[1]))
    if isinstance(message, types.CallbackQuery):
        await bot.edit_message_reply_markup(message.from_user.id, message.message.message_id)
    else:
        await message.answer('Вы возвращены в главное меню.', reply_markup=types.ReplyKeyboardRemove())
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.row(types.InlineKeyboardButton('📦Объявления', callback_data="view_announces"))
    kb.row(types.InlineKeyboardButton('♻️Парсить', callback_data="parsing_start"))
    kb.row(types.InlineKeyboardButton('⚙️Фильтры', callback_data=f"view_filters"))
    kb.row(types.InlineKeyboardButton('⚙️Категории парсинга', callback_data=f"view_parsing_category"))
    kb.row(types.InlineKeyboardButton('🔑Добавить токен', callback_data='add_token'))
    kb.row(types.InlineKeyboardButton('💼Кабинет', callback_data='my_cabinet'))
    user = DB.get_user(message.from_user.id)
    balance = DB.get_balance_user(message.from_user.id)
    if datetime.datetime.now() > user[2]:
        subscription = 'Подписка отсутствует'
    else:
        subscription = f'Действует до {user[2].day}-{user[2].month}-{user[2].year} {user[2].hour}:{user[2].minute}:{user[2].second}'
    if user[1]:
        status_parsing = '✅ парсится'
    else:
        status_parsing = '❌ не парсится'
    text = f"""
👤 Профиль
🆔 ID: {message.from_user.id}
💰 Баланс: {balance[1]}
♻️ Статус парсинга: {status_parsing}
⏳ {subscription}
    """
    await bot.send_message(message.from_user.id, text, reply_markup=kb)


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message, state: FSMContext):
    await cancel_main_keyboard_handler(message, state)


@dp.message_handler(commands=['test'])
async def test_command(message: types.Message):
    import asyncio
    new_message = await message.answer('text')
    await asyncio.sleep(2)
    await bot.edit_message_text('text_new', new_message.chat.id, new_message.message_id)

from main_keyboard_handlers import *
from command_handers import *
from aiogram.utils import executor
from parser_handlers import *
from filters_parsing import *
from my_cabinet import *

if __name__ == '__main__':
    executor.start_polling(dp)
