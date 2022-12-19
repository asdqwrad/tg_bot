import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import requests
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
from lxml import etree
import json
import pandas as pd

import http.server
import socketserver

handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", 1234), handler) as httpd:
    httpd.serve_forever()

TOKEN = '<your token>'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Form(StatesGroup):
    query = State()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer(
        'You can control me by sending these commands:\n\n/item - случайный предмет\n/store - случайная '
        'лавка\n/player - случайный игрок\n/roll - случайное значение от 1 до 6\n/youtube - видео с '
        'наибольшим количеством просмотров')


@dp.message_handler(commands=['item'])
async def send_welcome(message: types.Message):
    r = requests.get('https://api.prontera.ru/api/v3/ru_prime/random_store_data/?limit=1')
    info = json.loads(r.content)
    info = info['results'][0]
    info = info['item']
    name = info['name']
    description = info['description']
    description = description.replace('<ITEM>', '[')
    description = description.replace('</ITEM>', ']')
    description = description.replace('<INFO>', ' ID: ')
    description = description.replace('</INFO>', '')
    median = info['price']['7']['med']
    minimum = info['price']['7']['min']
    maximum = info['price']['7']['max']
    sep = '-' * 30
    text = f'{sep}\n{name}\n{sep}\n{description}\n{sep}\nМедианная цена: {median}\nМинимальная цена: {minimum}\n' \
           f'Максимальная цена: {maximum}\n{sep} '
    await message.answer(f'`{text}`', parse_mode='markdown')


@dp.message_handler(commands=['store'])
async def send_welcome(message: types.Message):
    r = requests.get('https://api.prontera.ru/api/v3/ru_prime/random_store/?limit=1')
    info = json.loads(r.content)
    info = info['results'][0]
    title = info['title']
    x = info['last_x']
    y = info['last_y']
    df = pd.DataFrame.from_dict(info['store_items'], orient='columns')
    df = df[['name', 'amount', 'price']]
    sep = '-' * 30
    text = f'{sep}\nЛавка: {title}\nКоординаты: ({x}, {y})\n{sep}\n'
    for index, row in df.iterrows():
        text += f'{row[0]}\nКоличество: {row[1]}\nЦена: {row[2]}\n{sep}\n'
    await message.answer(f'`{text}`', parse_mode='markdown')


@dp.message_handler(commands=['player'])
async def send_welcome(message: types.Message):
    r = requests.get('https://api.prontera.ru/api/v3/ru_prime/random_player/?limit=1')
    info = json.loads(r.content)
    info = info['results'][0]
    name = info['name']
    base = info['base_level']
    prof = info['profession']
    sep = '-' * 30
    text = f'{sep}\n{name}\n{sep}\nБазовый уровень: {base}\n{sep}\nПрофессиональный уровень: {prof}\n{sep}'
    await message.answer(f'`{text}`', parse_mode='markdown')


@dp.message_handler(commands=['roll'])
async def send_welcome(message: types.Message):
    r = await bot.send_dice(message.chat.id)
    await message.answer(f'Result: {r.dice.value}')


@dp.message_handler(commands=['youtube'])
async def send_welcome(message: types.Message):
    await Form.query.set()
    await message.answer('Введите запрос:')


@dp.message_handler(state=Form.query)
async def process_message(message: types.Message, state: FSMContext):
    session = AsyncHTMLSession()
    r = await session.get('https://www.youtube.com/results?search_query=' + message.text + '&sp=CAMSAhAB')
    await r.html.arender(sleep=1)
    soup = BeautifulSoup(r.html.html, 'html.parser')
    dom = etree.HTML(str(soup))
    elem = dom.xpath('//div[@id="contents"]//a')
    if len(elem) == 0:
        url = 'No results found'
    else:
        url = 'https://www.youtube.com' + elem[0].xpath('@href')[0]
    await message.answer(url)
    await state.finish()


executor.start_polling(dp, skip_updates=True)
