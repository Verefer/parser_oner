from aiogram import types
from config import *
import random
from states import *
from main_keyboards import *
import string
from main_keyboard_handlers import *
from aiogram.dispatcher import FSMContext


@dp.message_handler(commands=['add_proxy'])
async def add_proxy(message: types.Message):
    if message.from_user.id in ADMINS:
        lines = message.text.splitlines()[1:]
        DB.add_proxies_olx_ua(lines)
        await message.answer('Прокси успешно добавлены.')
    else:
        await message.answer('Вы не имеете достаточно прав для использования этой команды.')


@dp.message_handler(commands=['promo'])
async def create_promo_handler(message: types.Message):
    line = message.text.split()
    if message.from_user.id in ADMINS:
        if len(line) == 2:
            if line[1].isdigit():
                percent = int(line[1])
                if 0 < percent < 81:
                    promo = ''.join(random.choices(string.ascii_uppercase, k=15))
                    DB.create_promo(promo, percent)
                    await message.answer(f"Промокод на скидку {percent}% создан.\n<code>{promo}</code>",
                                         parse_mode=types.ParseMode.HTML)
                else:
                    await message.answer('Введите корректный процент (1 - 80).')
            else:
                await message.answer('Некорректный процент. Повторите попытку.')
        else:
            await message.answer('Неверный формат команды. Пример:\n<code>/promo 20</code>',
                                 parse_mode=types.ParseMode.HTML)
    else:
        await message.answer('Вы не имеете достаточно прав для использования этой команды.')


@dp.message_handler(commands=['delete_promo'])
async def delete_promo_command_handler(message: types.Message):
    if message.from_user.id in ADMINS:
        line = message.text.split()
        if len(line) == 2:
            promo = line[1]
            if promo in list(map(lambda el: el[0], DB.get_all_promo_codes())):
                DB.delete_promo_and_discounts(promo)
                await message.answer('Промокод успешно удален.')
        else:
            await message.answer('Неверный формат команды. Пример:\n<code>/delete_promo AAAAAAAAAAAAAAA</code>',
                                 parse_mode=types.ParseMode.HTML)
    else:
        await message.answer('Вы не имеете достаточно прав для использования этой команды.')


@dp.message_handler(commands=['add_local_proxy'])
async def add_local_proxy_command_handler(message: types.Message):
    if message.from_user.id in ADMINS:
        DB.add_proxies_olx_ua([''])
        await message.answer('Локальный айпи успешно добавлен.')
    else:
        await message.answer('Вы не имеете достаточно прав для использования этой команды.')


@dp.message_handler(commands=['set_balance'])  # /set_balance 996780194 1500
async def set_balance_command_handler(message: types.Message):
    if message.from_user.id in ADMINS:
        line = message.text.split()
        if len(line) == 3:
            if line[1].isdigit() and line[2].isdigit():
                balance = DB.get_balance_user(line[1])
                if balance:
                    delta = int(line[2]) - balance[1]
                    DB.update_user_balance(line[1], delta)
                    await message.answer(f'Баланс пользователя {line[1]} теперь равен {line[2]}RUB')
    else:
        await message.answer('Вы не имеете достаточно прав для использования этой команды.')


@dp.message_handler(commands=['mail'])
async def mail_command_handler(message: types.Message):
    if message.from_user.id in ADMINS:
        await Admins.mail_message.set()
        await message.answer('Напишите текст рассылки', reply_markup=kb_return_to_main_keyboard_inline)
    else:
        await message.answer('Вы не имеете достаточно прав для использования этой команды.')


@dp.message_handler(state=Admins.mail_message,
                    content_types=types.ContentTypes.PHOTO | types.ContentTypes.TEXT | types.ContentTypes.DOCUMENT | types.ContentTypes.ANIMATION)
async def main_mail_handler(message: types.Message, state: FSMContext):
    await state.finish()
    users = DB.get_all_users()
    count = 1
    new_msg: types.Message = await message.answer('Рассылка запущена')
    for user in users:
        try:
            await bot.copy_message(user[0], message.from_user.id, message.message_id)
        except Exception as ex:
            print(ex)
        await new_msg.edit_text(f"Прогресс: {count}/{len(users)}")
        count += 1
    await new_msg.edit_text('Рассылка закончена')
