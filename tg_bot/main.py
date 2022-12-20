import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import requests
import json
import pandas as pd

TOKEN = '<your token>'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Form(StatesGroup):
    query = State()


profs = {
    0: 'Новичок',
    1: 'Мечник',
    2: 'Маг',
    3: 'Лучник',
    4: 'Послушник',
    5: 'Торговец',
    6: 'Вор',
    7: 'Рыцарь',
    8: 'Священник',
    9: 'Волшебник',
    10: 'Кузнец',
    11: 'Охотник',
    12: 'Убийца',
    14: 'Крестоносец',
    15: 'Монах',
    16: 'Мудрец',
    17: 'Разбойник',
    18: 'Алхимик',
    19: 'Бард',
    20: 'Танцовщица',
    23: 'Супер Новичок',
    24: 'Стрелок',
    25: 'Ниндзя',
    4008: 'Командор',
    4009: 'Епископ',
    4010: 'Архимаг',
    4011: 'Оружейник',
    4012: 'Снайпер',
    4013: 'Ассасин',
    4015: 'Паладин',
    4016: 'Мистик',
    4017: 'Профессор',
    4018: 'Сталкер',
    4019: 'Биохимик',
    4020: 'Менестрель',
    4021: 'Цыганка',
    4046: 'Таэквондист',
    4047: 'Гладиатор',
    4049: 'Медиум',
    4060: 'Рунмейстер',
    4061: 'Чародей',
    4062: 'Рейнджер',
    4063: 'Архиепископ',
    4064: 'Механик',
    4065: 'Каратель',
    4073: 'Тамплиер',
    4074: 'Элементалист',
    4075: 'Маэстро',
    4076: 'Муза',
    4077: 'Отшельник',
    4078: 'Генетик',
    4079: 'Преследователь',
    4190: 'Экспертный Новичок',
    4211: 'Кагеро',
    4212: 'Оборо',
    4215: 'Мятежник',
    4218: 'Призыватель',
    4239: 'Звёздный лорд',
    4240: 'Жнец',
    4252: 'Драгонмейстер',
    4253: 'Мейстер',
    4254: 'Сумрачный Каратель',
    4255: 'Чернокнижник',
    4256: 'Кардинал',
    4257: 'Разведчик',
    4258: 'Имперский страж',
    4259: 'Биолог',
    4260: 'Преследователь бездны',
    4261: 'Мастер стихий',
    4262: 'Инквизитор',
    4263: 'Трубадур',
    4264: 'Трувера',
    4302: 'Небесный император',
    4303: 'Духовный аскет',
    4304: 'Шинкиро',
    4305: 'Ширануи',
    4306: 'Дозорный',
    4307: 'Гипер Новичок',
    4308: 'Повелитель духов'
}


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer(
        'You can control me by sending these commands:\n\n/item - случайный предмет\n/store - случайная '
        'лавка\n/player - случайный игрок\n/roll - случайное значение от 1 до 6\n/youtube - поиск видео')


@dp.message_handler(commands=['item'])
async def send_welcome(message: types.Message):
    r = requests.get('https://api.prontera.ru/api/v3/ru_prime/random_store_data/?limit=1')
    info = json.loads(r.content)
    if len(info['results']) == 0:
        await message.answer('`No data available`', parse_mode='markdown')
        return
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
    if len(info['results']) == 0:
        await message.answer('`No data available`', parse_mode='markdown')
        return
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
    if len(info['results']) == 0:
        await message.answer('`No data available`', parse_mode='markdown')
        return
    info = info['results'][0]
    name = info['name']
    base = info['base_level']
    prof = info['profession']
    sep = '-' * 30
    text = f'{sep}\n{name}\n{sep}\nБазовый уровень: {base}\n{sep}\nПрофессия: {profs[prof]}\n{sep}'
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
    await message.answer('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    await state.finish()


executor.start_polling(dp, skip_updates=True)
