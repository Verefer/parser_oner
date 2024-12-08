from aiogram import types
from config import *
from states import *
from main_keyboards import *
import random
import asyncio
import string
from aiogram.dispatcher import FSMContext
from telethon import TelegramClient
import datetime


@dp.callback_query_handler(lambda c: c.data == 'my_cabinet', state='*')
async def view_my_cabinet_inline_handler(call: types.CallbackQuery):
    user = DB.get_user(call.from_user.id)
    balance = DB.get_balance_user(call.from_user.id)
    if datetime.datetime.now() > user[2]:
        subscription = 'Подписка отсутствует'
    else:
        subscription = f'Действует до {user[2].day}-{user[2].month}-{user[2].year} {user[2].hour}:{user[2].minute}:{user[2].second}'
    text = f"""
💳 Твой баланс: {balance[1]}Р
🎁 Персональная скидка: {balance[3]}
♻️ Активные подписки:
{subscription}   
"""
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton('💰Пополнение', callback_data='top_up_balance_view_methods'))
    kb.row(types.InlineKeyboardButton('🛍Подписка', callback_data='view_subscription'))
    kb.row(types.InlineKeyboardButton('👫 Рефералы', callback_data='view_referal_system'))
    kb.row(types.InlineKeyboardButton('🎁Ввести промокод', callback_data='enter_promocode'))
    kb.row(types.InlineKeyboardButton('⚙️ Очистить список токенов', callback_data='clear_tokens'))
    await bot.send_message(call.from_user.id, text, reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data == 'enter_promocode', state='*')
async def enter_promocode_inline_handler(call: types.CallbackQuery):
    await MyCabinet.enter_promo.set()
    await bot.send_message(call.from_user.id,
                           'Введите промокод. Получить его ты можешь у администраторов своей команды.',
                           reply_markup=kb_return_to_main_keyboard_inline)


@dp.callback_query_handler(lambda c: c.data == 'clear_tokens', state='*')
async def clear_tokens_inline_handler(call: types.CallbackQuery):
    token = DB.get_token(call.from_user.id)
    while token is not None:
        DB.delete_token(token[0])
        token = DB.get_token(call.from_user.id)
    await call.answer('✅ Все токены успешно удалены', show_alert=True)


@dp.message_handler(state=MyCabinet.enter_promo)
async def enter_promo_handler(message: types.Message, state: FSMContext):
    await state.finish()
    promo_codes: tuple = DB.get_all_promo_codes()
    codes_list = list(map(lambda el: el[0], promo_codes))
    if message.text in codes_list:
        index = codes_list.index(message.text)
        DB.set_promo_code_and_discount(message.from_user.id, promo_codes[index][0], promo_codes[index][1])
        await message.answer(f"Промокод на скидку {promo_codes[index][1]}% успешно активирован.",
                             reply_markup=kb_return_to_main_menu)
    else:
        await message.answer('Промокода не существует')


@dp.callback_query_handler(lambda c: c.data == 'view_referal_system', state='*')
async def view_referal_system_inline_handler(call: types.CallbackQuery):
    length_referals = DB.get_amount_refers(call.from_user.id)
    text = f"""
👫 Рефералы

Твои рефералы: {length_referals}
Твоя реф-ссылка: https://t.me/{BOT_USERNAME}?start={call.from_user.id}

• Ты получаешь {REFER_PERCENT}% от всех пополнений пользователей которые зарегистрировались по твоей ссылке.
"""
    await bot.send_message(call.from_user.id, text, reply_markup=kb_return_to_main_keyboard_inline)


@dp.callback_query_handler(lambda c: c.data == 'view_subscription', state='*')
async def view_subscription_inline_handler(call: types.CallbackQuery):
    user = DB.get_balance_user(call.from_user.id)
    text = f"""
💰 Оплата подписки OLX UA

👉🏼 Твой баланс: {user[1]} RUB

• Выбери тариф. Чем больше длительность подписки, тем выгоднее.
• Если у тебя уже есть подписка на этот сайт, то покупка просто добавит часов.    
"""
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton('90 RUB | 1 день', callback_data='buy_subscription&90&1'))
    kb.row(types.InlineKeyboardButton('250 RUB | 3 дня', callback_data='buy_subscription&250&3'))
    kb.row(types.InlineKeyboardButton('500 RUB | 7 дней', callback_data='buy_subscription&500&7'))
    kb.row(types.InlineKeyboardButton('2000 RUB | 30 дней', callback_data='buy_subscription&2000&30'))
    kb.row(types.InlineKeyboardButton('Назад в главное меню', callback_data='back_to_main_menu'))
    await bot.send_message(call.from_user.id, text, reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith('buy_subscription'), state='*')
async def buy_subscription_inline_handler(call: types.CallbackQuery):
    amount, days = call.data.split('&')[1:]
    balance = DB.get_balance_user(call.from_user.id)
    total_price = int(amount) * (100 - balance[3]) // 100
    if total_price > balance[1]:
        await call.answer('Недостаточно средств для оплаты данного тарифа', show_alert=True)
    else:
        user = DB.get_user(call.from_user.id)
        if datetime.datetime.now() >= user[2]:
            time_subscription = datetime.datetime.now() + datetime.timedelta(days=int(days))
        else:
            time_subscription = user[2] + datetime.timedelta(days=int(days))
        DB.update_user_balance(call.from_user.id, -int(total_price))
        DB.set_new_time_for_subscription(call.from_user.id, time_subscription)
        text = f"""
Подписка на OLX UA на сумму {amount} RUB и длительность {days} дней успешно оформлена.
Применена персональная скидка {balance[3]}%
Сумма списания: {total_price}        
"""
        await bot.send_message(call.from_user.id, text, reply_markup=kb_return_to_main_menu)


@dp.callback_query_handler(lambda c: c.data == 'top_up_balance_view_methods', state='*')
async def top_up_balance_view_methods_inline_handler(call: types.CallbackQuery):
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton('🤖 BANKER', callback_data='top_up_balance_method_banker'))
    kb.row(types.InlineKeyboardButton('🥝 QIWI', callback_data='top_up_balance_method_qiwi'))
    await bot.send_message(call.from_user.id, '💰 Выбери метод оплаты:', reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data == 'top_up_balance_method_banker', state='*')
async def top_up_balance_method_banker_inline_handler(call: types.CallbackQuery):
    text = """
Для пополнения счета с помощью чека:
1. Создайте чек на любую сумму в BTC
2. Отправьте чек прямо в бота
3. Средства будут зачислены автоматически

• Из-за скачков курса рекомендуем отправлять на несколько центов больше, чем требуется
• Чеки должны быть отправлены в виде ссылок, а не QR-кодов или хэшей    
"""
    await TopUpBalance.deposit_banker.set()
    await bot.send_message(call.from_user.id, text, reply_markup=kb_return_to_main_keyboard_inline)


@dp.message_handler(state=TopUpBalance.deposit_banker)
async def top_up_balance_handler_success(message: types.Message, state: FSMContext):
    try:
        if message.text.startswith('https://telegram.me/BTC_CHANGE_BOT?start='):
            check = '/start ' + message.text.split('=')[1]

            await run_process_send_check_banker(check, message.from_user.id)
            await bot.send_message(message.from_user.id, 'Чек успешно активирован.')
        else:
            await bot.send_message(message.from_user.id, 'Некорректный чек.')
        await state.finish()
    except Exception as ex:
        print(ex)
        await bot.send_message(message.from_user.id, 'Произошло что-то не по плану. Повторите попытку.')


async def run_process_send_check_banker(check, user_id):
    async with TelegramClient('session', API_APP_ID, API_HASH) as client:
        await client.send_message('BTC_CHANGE_BOT', check)
        try:

            await asyncio.sleep(1)

            entity = await client.get_entity('BTC_CHANGE_BOT')
            message = await client.get_messages(entity, limit=2)

            fmes = message[0].message.split()

            if 'Вы' not in fmes:
                message = message[1].message.split()
            else:
                message = fmes

            print(message)
            amount_btc = float(message[2])
            money = int(float(coinbase_client.get_spot_price(currency_pair='BTC-RUB')['amount']) * amount_btc)

            print(money)
            user = DB.get_user(user_id)
            DB.update_user_balance(user_id, money)
            await bot.send_message(ADMINS[0], f'Пользователь с ID {user_id} пополнил баланс на {money}RUB')
            if user[8]:
                percent = money * REFER_PERCENT // 100
                if percent > 1:
                    DB.update_user_balance(user[8], percent)
                    await bot.send_message(user[8], f"Вы получили {percent} RUB вознаграждения от реферала 🤝")
            await bot.send_message(user_id, f'На ваш баланс зачислено {money} RUB', reply_markup=kb_return_to_main_menu)
        except Exception as ex:
            print(ex)
            await bot.send_message(user_id, 'Произошла ошибка. Попробуйте еще раз.')


@dp.callback_query_handler(lambda c: c.data == 'top_up_balance_method_qiwi', state='*')
async def top_up_balance_method_qiwi_inline_handler(call: types.CallbackQuery):
    await TopUpBalance.summa_qiwi.set()
    await bot.send_message(call.from_user.id, 'Введите сумму, на которую хотите пополнить баланс (10 - 25000)',
                           reply_markup=kb_cancel)


@dp.message_handler(lambda m: m.text.isdigit() and 0 < int(m.text) < 25001, state=TopUpBalance.summa_qiwi)
async def top_up_balance_create_bill_qiwi_handler(message: types.Message, state: FSMContext):
    await state.finish()
    bill = await p2p.bill(''.join(random.choices(string.digits + string.ascii_uppercase, k=12)),
                          amount=int(message.text), comment='', lifetime=15)

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton('Перейти к оплате', url=bill.pay_url))
    kb.add(types.InlineKeyboardButton('Проверить оплату 💵', callback_data=f"check_payment&{bill.bill_id}"))
    text = f"""
♻️ Оплата QIWI/банковской картой: <a href="{bill.pay_url}"><b>ОПЛАТА</b></a> 
Сумма: {message.text}₽
Ссылка действительна в течение 15 минут.
        """

    await message.answer(text, parse_mode=types.ParseMode.HTML, reply_markup=kb)
    await message.answer('После оплаты проверьте поступление средств на счет, нажав на кнопку выше.',
                         reply_markup=kb_return_to_main_menu)


@dp.message_handler(lambda m: not m.text.isdigit() or int(m.text) > 25000 or int(m.text) < 10,
                    state=TopUpBalance.summa_qiwi)
async def top_up_balance_create_bill_qiwi_error_handler(message: types.Message):
    await message.answer('Введите корректное значение (10 - 25000) или отмените операцию', reply_markup=kb_cancel)


@dp.callback_query_handler(lambda c: c.data.startswith('check_payment'), state='*')
async def check_payment_inline_handler(call: types.CallbackQuery):
    bill_id = call.data.split('&')[1]
    obj = await p2p.check(bill_id=bill_id)
    print(obj.status)
    if obj.status == 'PAID':
        DB.update_user_balance(call.from_user.id, int(float(obj.amount)))

        await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id, f'Ваш баланс успешно пополнен на сумму {obj.amount}')
        await bot.send_message(ADMINS[0], f'Пользователь с ID {call.from_user.id} пополнил баланс на {obj.amount}RUB')
        user = DB.get_user(call.from_user.id)
        if user[8]:
            percent = int(float(obj.amount)) * REFER_PERCENT // 100
            if percent > 1:
                DB.update_user_balance(user[8], percent)
                await bot.send_message(user[8], f"Вы получили {percent} RUB вознаграждения от реферала 🤝")
    elif obj.status == 'WAITING':
        await call.answer('Счет не оплачен.', show_alert=True)
