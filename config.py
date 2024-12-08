from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import db_io
from coinbase.wallet.client import Client
from pyqiwip2p.AioQiwip2p import AioQiwiP2P

TOKEN = ''
DB_HOST = '5.188.118.120'
DB_USER = 'root'
DB_PASSWORD = 'iIPkc0aMg1ck'
ADMINS = (5010376753,)  # здесь айди админов через запятую
API_APP_ID = 10540691  # айди приложения
API_HASH = '4d8b83c2b9a664b38daab3974259c3ce'
REFER_PERCENT = 15  # реферальный процент
BOT_USERNAME = ''

QIWI_PRIVATE_KEY = "eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6IjRzMWd6by0wMCIsInVzZXJfaWQiOiI3OTkxNDQ1OTEwMiIsInNlY3JldCI6ImJiZGFjNTliMTBhNzZmYjBiYTRlOTdkMzViZWYxMmYxZTQwOTJmOWE1MzAyZWUzZWUxNjAzOTA2OWNjZTU3OWMifX0"

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
DB = db_io.DataBase(DB_HOST, DB_USER, DB_PASSWORD)
p2p = AioQiwiP2P(auth_key=QIWI_PRIVATE_KEY)
coinbase_client = Client('dflsjO2v2UQ0vDox', 'MNQNBe5Z2ayvzXyaLvyP8spNLzersWA5', api_version='2021-12-04')
