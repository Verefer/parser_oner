from config import *
from aiogram import types
from states import *
from aiogram.dispatcher import FSMContext
from main_keyboards import *


@dp.callback_query_handler(lambda c: c.data == 'view_filters', state='*')
async def view_filters_inline_handler(call: types.CallbackQuery):
    user = DB.get_user(call.from_user.id)
    text = f"""
⚙️<b>Ваши фильтры:</b>:

💎<b>Фильтр цены</b>: {user[4]}
🚚<b>Фильтр количества успешных доставок</b>: {user[5]}
🕑<b>Макс. количество дней со дня регистрации продавца</b>: {user[3]}
⏳<b>Интервал создания обьявы (минуты)</b>: {user[6]}  
"""
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton('Фильтр цены', callback_data='change_filter_price'))
    kb.add(types.InlineKeyboardButton('Фильтр доставок', callback_data='change_filter_success_delivery'))
    kb.add(types.InlineKeyboardButton('Фильтр количества дней', callback_data='change_filter_amount_days'))
    kb.add(types.InlineKeyboardButton('Фильтр интервала создания', callback_data='change_filter_interval_create'))
    kb.add(types.InlineKeyboardButton('Автотекст WA', callback_data='change_auto_text_wa'))
    kb.add(types.InlineKeyboardButton('Назад', callback_data='back_to_main_menu'))
    await bot.send_message(call.from_user.id, text, reply_markup=kb, parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(lambda c: c.data == 'change_auto_text_wa', state='*')
async def change_auto_text_wa_inline_handler(call: types.CallbackQuery):
    user = DB.get_user(call.from_user.id)
    await Filters.auto_text_wa.set()
    text = f"""
Текущий автотекст:
{user[7]}

Автотекст будет отображаться ссылкой при обзоре объявлений
Автотекст поддерживает переменные в квадратных скобках, а именно [link], [title], [name] и [price]
Переменная link вставляет в текст ссылку на объявление, title - название, name - ник продавца, price - цену
Для того чтобы отключить отображение автотекста, пришли ! (восклицательный знак)    
"""
    await bot.send_message(call.from_user.id, text, reply_markup=kb_cancel)


@dp.message_handler(state=Filters.auto_text_wa)
async def auto_text_wa_handler(message: types.Message, state: FSMContext):
    await state.finish()
    DB.set_filter_auto_text_wa(message.from_user.id, message.text)
    await message.answer('Автотекст успешно установлен.', reply_markup=kb_return_to_main_menu)


@dp.callback_query_handler(lambda c: c.data == 'change_filter_interval_create', state='*')
async def change_filter_interval_create_inline_handler(call: types.CallbackQuery):
    await Filters.interval_create.set()
    await bot.send_message(call.from_user.id,
                           'Введите максимальное количество минут с момента создания объявления (15+)',
                           reply_markup=kb_cancel)


@dp.message_handler(lambda m: m.text.isdigit() and int(m.text) > 15, state=Filters.interval_create)
async def filter_interval_create_handler(message: types.Message, state: FSMContext):
    await state.finish()
    DB.set_filter_interval_create(message.from_user.id, message.text)
    await message.answer('Фильтр интервала создания успешно обновлен.', reply_markup=kb_return_to_main_menu)


@dp.message_handler(lambda m: not m.text.isdigit() or int(m.text) <= 15, state=Filters.interval_create)
async def filter_interval_create_announce_error_handler(message: types.Message):
    await message.answer('Введите корректное значение (от 15) или отмените операцию', reply_markup=kb_cancel)


@dp.callback_query_handler(lambda c: c.data == 'change_filter_amount_days')
async def change_filter_amount_days_inline_handler(call: types.CallbackQuery):
    await Filters.amount_days.set()
    await bot.send_message(call.from_user.id, 'Введите максимальное количество дней со дня регистрации продавца',
                           reply_markup=kb_cancel)


@dp.message_handler(lambda m: m.text.isdigit() and int(m.text) > 40, state=Filters.amount_days)
async def filter_amount_days_handler(message: types.Message, state: FSMContext):
    await state.finish()
    DB.set_filter_amount_days(message.from_user.id, int(message.text))
    await message.answer('Фильтр количества дней со дня регистрации продавца обновлен',
                         reply_markup=kb_return_to_main_menu)


@dp.message_handler(lambda m: not m.text.isdigit() or int(m.text) <= 40, state=Filters.amount_days)
async def filter_amount_days_error_handler(message: types.Message):
    await message.answer("Введите корректное значение (40+ дней) или отмените операцию", reply_markup=kb_cancel)


@dp.callback_query_handler(lambda c: c.data == 'change_filter_success_delivery', state='*')
async def change_filter_success_delivery_inline_handler(call: types.CallbackQuery):
    await Filters.success_delivery.set()
    await bot.send_message(call.from_user.id, 'Введите максимальное количество успешных доставок продавца',
                           reply_markup=kb_cancel)


@dp.message_handler(lambda m: m.text.isdigit() and int(m.text) > -1, state=Filters.success_delivery)
async def filter_success_delivery_handler(message: types.Message, state: FSMContext):
    await state.finish()
    DB.set_filter_success_deliveries(message.from_user.id, int(message.text))
    await message.answer('Фильтр количества успешных доставок обновлен.', reply_markup=kb_return_to_main_menu)


@dp.message_handler(lambda m: not m.text.isdigit() or int(m.text) <= -1, state=Filters.success_delivery)
async def filter_success_delivery_error_handler(message: types.Message):
    await message.answer('Введите корректное значение или отмените операцию', reply_markup=kb_cancel)


@dp.callback_query_handler(lambda c: c.data == 'change_filter_price', state='*')
async def change_filter_price_inline_handler(call: types.CallbackQuery):
    await Filters.price.set()
    await bot.send_message(call.from_user.id, f"Введи границы цен через черточку, например так:\n<code>50-4800</code>",
                           parse_mode=types.ParseMode.HTML, reply_markup=kb_cancel)


@dp.message_handler(lambda m: '-' in m.text and all(map(str.isdigit, m.text.split('-'))), state=Filters.price)
async def filter_change_price_handler(message: types.Message, state: FSMContext):
    if len(message.text.split('-')) == 2:
        await state.finish()
        DB.set_filter_price(message.from_user.id, message.text)
        await message.answer('Фильтр цены успешно обновлен.', reply_markup=kb_return_to_main_menu)
    else:
        await filter_change_price_error_handler(message)


@dp.message_handler(lambda m: '-' not in m.text or not all(map(str.isdigit, m.text.split('-'))), state=Filters.price)
async def filter_change_price_error_handler(message: types.Message):
    await message.answer('Введите корректное значение или отмените операцию', reply_markup=kb_cancel)
