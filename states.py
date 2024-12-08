from aiogram.dispatcher.filters.state import StatesGroup, State


class AddToken(StatesGroup):
    add_token = State()


class Parser(StatesGroup):
    amount_announces = State()


class Filters(StatesGroup):
    price = State()
    success_delivery = State()
    amount_days = State()
    interval_create = State()
    auto_text_wa = State()


class TopUpBalance(StatesGroup):
    summa_qiwi = State()
    deposit_banker = State()


class MyCabinet(StatesGroup):
    enter_promo = State()


class Admins(StatesGroup):
    mail_message = State()
