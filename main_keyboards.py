from aiogram import types

kb_cancel = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('Отмена'))
kb_return_to_main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
    types.KeyboardButton('Вернуться в главное меню'))
kb_return_to_main_keyboard_inline = types.InlineKeyboardMarkup().add(
    types.InlineKeyboardButton('Вернуться в главное меню', callback_data='back_to_main_menu'))




