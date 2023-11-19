import asyncio
from openpyxl import load_workbook
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import types
from aiogram import F
import re
from aiogram.types import FSInputFile
import json
import os

from openpyxl.workbook import Workbook

bot = Bot(token='6952815695:AAF3AvrU4_kmja7ba3MorNx0UA_lRJrcCOU')
dp = Dispatcher()



class ClientState(StatesGroup):
    greet = State()
    scores = State()
    steps = State()
    total_sleep = State()
    deep_sleep = State()
    about_day = State()
    personal_rate = State()



async def add_day_to_excel(date, activities, user_message, total_sleep, deep_sleep, rate, mysteps, message, user_id, scores, user_name):
    # Загрузка существующего файла Excel
    if os.path.exists(f'{user_name}_Diary.xlsx'):
        # If the file exists, load the existing workbook
        wb = load_workbook(f'{user_name}_Diary.xlsx')
    else:
        # If the file doesn't exist, create a new workbook
        wb = Workbook()
        sheet = wb.active
        sheet.cell(row=1, column=1).value = 'Дата'
        sheet.cell(row=1, column=2).value = 'Дела за день'
        sheet.cell(row=1, column=3).value = 'Шаги'
        sheet.cell(row=1, column=4).value = 'Total sleep'
        sheet.cell(row=1, column=5).value = 'Deep sleep'
        sheet.cell(row=1, column=6).value = 'О дне'
        sheet.cell(row=1, column=7).value = 'My rate'
        sheet.cell(row=1, column=8).value = 'Total'

    # Получение активного листа
    sheet = wb.active

    # Поиск последней заполненной строки в столбце "Дата"
    last_row = sheet.max_row

    # Получение вчерашней даты
    yesterday = date - timedelta(days=1)

    # Вставка вчерашней даты в следующую за последней заполненной строкой
    sheet.cell(row=last_row+1, column=1).value = yesterday.strftime("%d.%m.%Y")

    # Вставка дел в таблицу
    if type(activities) == list:
        sheet.cell(row=last_row+1, column=2).value = ", ".join(activities)
    else:
        sheet.cell(row=last_row + 1, column=2).value = activities
    # Вставка шаги
    sheet.cell(row=last_row + 1, column=3).value = mysteps
    # Вставка сколько часов спал
    sheet.cell(row=last_row + 1, column=4).value = total_sleep
    # Вставка времени глубокого сна
    sheet.cell(row=last_row + 1, column=5).value = deep_sleep
    # Вставка о дне в таблицу
    sheet.cell(row=last_row + 1, column=6).value = user_message
    # Вставка времени глубокого сна
    sheet.cell(row=last_row + 1, column=7).value = rate

    # Вычисление итогового счета
    score = 0
    if type(activities) == list:
        for activity in activities:
            score += int(scores[activity])
    else:
        score += int(scores[activities])

    # Вставка итогового счета в таблицу
    sheet.cell(row=last_row+1, column=8).value = score

    # Сохранение изменений в файл
    wb.save(f'{user_name}_Diary.xlsx')
    kb = [[types.KeyboardButton(text="Скачать таблицу"), types.KeyboardButton(text="Изменить список дел")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )
    await message.answer('Готово! Вы в любой момент можете скачать дневник по кнопке ниже', reply_markup=keyboard)
async def send_message(message) -> None:
    with open('scores.txt', 'w+') as f:
        for line in f:
            line = json.loads(line.strip())
            if message.from_user.id == line['id']:
                scores = line['scores']

    await message.answer('Расскажи мне как провел вчерашний день?' + '\n' + 'Вот возможный список дел:')
    await message.answer(', '.join(scores.keys()))
@dp.message(F.text == 'Изменить список дел')
async def download(message: Message, state: FSMContext) -> None:
    await message.answer('Введите новый список дел и их "стоимость". Ваш предыдущий список: ')
    user_states_data = await state.get_data()
    scores = user_states_data['scores']
    formatted_string = ""
    for key, value in scores.items():
        formatted_string += f"{key} : {value}, "
    formatted_string = formatted_string[:-2]

    await message.answer(formatted_string)
    await message.answer(
        'Вы можете воспользоваться предложенным списком или написать свой. Данные могут быть какие угодно, очки нужны для отчетности о том насколько продуктивен был день.' + '\n' + 'Соблюдайте формат данных!')
    await state.set_state(ClientState.scores)
@dp.message(F.text == 'Скачать таблицу')
async def download(message: Message) -> None:
    if os.path.exists(f'{message.from_user.username}_Diary.xlsx'):
        await message.answer_document(
            document=FSInputFile(f'{message.from_user.username}_Diary.xlsx'),
            disable_content_type_detection=True,
        )
    else:
        await message.answer('Сначала заполните данные')
@dp.message(CommandStart())
async def greetings(message: Message, state: FSMContext) -> None:
    await state.update_data(user_id=message.from_user.id)
    info = await bot.get_me()
    name = info.username
    flag = False
    if os.path.exists('scores.txt'):
        file =  open('scores.txt', 'r+')
        data = file.read()
        if data != '':
            score_list = json.loads(data)
            for line in score_list:
                if message.from_user.id == line['user_id']:
                    flag = True
                    scores = line['scores']
                    await state.update_data(scores=scores)
                    kb = [[types.KeyboardButton(text="Скачать таблицу"), types.KeyboardButton(text="Изменить список дел")]]
                    keyboard = types.ReplyKeyboardMarkup(
                        keyboard=kb,
                        resize_keyboard=True,
                    )
                    await message.answer(
                        'Расскажи мне как провел вчерашний день?' + '\n' + 'Вот возможный список дел:')

                    await message.answer(', '.join(scores.keys()), reply_markup=keyboard)
                    await message.answer('Впишите дела которые вы вчера делали из предложенного списка через запятую' + '\n' + 'Вы можете изменить список в любой момент')
                    await state.set_state(ClientState.greet)
                    file.close()
    else:
        file = open('scores.txt', 'w')
        json.dump([], file)
        file.close()
    if not flag:
        markup = types.ReplyKeyboardRemove()
        await message.answer_sticker('CAACAgIAAxkBAAIsZGVY5wgzBq6lUUSgcSYTt99JnOBbAAIIAAPANk8Tb2wmC94am2kzBA', reply_markup=markup)
        await message.answer(
            'Привет, ' + message.from_user.full_name + '!' + '\n' + 'Добро пожаловать в ' + name + '!' + '\n' + 'Он поможет тебе вести отчет о твоих днях и делать выводы почему день был плохим или хорошим')
        await message.answer('Для начала нужно задать список дел и их "стоимость". Например:')
        await message.answer('встал в 6:30 : 1, лег в 11 : 1, зарядка утром : 5, массаж : 3, пп : 1')
        await message.answer(
            'Вы можете воспользоваться предложенным списком или написать свой. Данные могут быть какие угодно, очки нужны для отчетности о том насколько продуктивен был день.' + '\n' + 'Соблюдайте формат данных!')
        await state.set_state(ClientState.scores)
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(send_message, 'cron', hour=7, minute=10, args=(message,))
    scheduler.start()

@dp.message(ClientState.scores)
async def command_start(message: Message, state: FSMContext):
    scores = dict()
    user_message = message.text
    str_data = user_message.split(', ')
    flag = False
    for one in str_data:
        one = one.split(' : ')
        if len(one) == 2 and one[1].isdigit():
            scores[one[0]] = one[1]
        else:
            flag = True
    if flag: await message.answer('Неверный формат данных!')

    await state.update_data(scores=scores)
    f = open ('scores.txt', 'r+')
    data = f.read()
    score_list = json.loads(data)
    score_list.append({'scores':scores, 'user_id': message.from_user.id})
    f.seek(0)
    json.dump(score_list, f)
    f.close()
    if os.path.exists(f'{message.from_user.id}_Diary.xlsx'):
        kb = [[types.KeyboardButton(text="Скачать таблицу"), types.KeyboardButton(text="Изменить список дел")]]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
        )
    else:
        kb = [[types.KeyboardButton(text="Изменить список дел")]]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
        )
    await message.answer(
        'Отлично! А теперь расскажи мне как провел вчерашний день?' + '\n' + 'Вот возможный список дел:', reply_markup=keyboard)
    await message.answer(', '.join(scores.keys()))
    await message.answer('Впишите дела которые вы вчера делали из предложенного списка через запятую' + '\n' + 'Вы можете изменить список в любой момент')
    await state.set_state(ClientState.greet)

@dp.message(ClientState.greet)
async def command_start(message: Message, state: FSMContext):
    user_states_data = await state.get_data()
    scores = user_states_data['scores']
    if len(scores) > 1:
        activities = [activity for activity in message.text.split(', ') if activity in scores]
    else:
        activities = message.text.strip(',')
    if len(activities) >= 1:
        await state.update_data(activities = activities)
        await message.answer("Сколько сделал шагов?")
        await state.set_state(ClientState.steps)
    else:
        await message.answer(message.text + ' содержит ошибку')

@dp.message(ClientState.steps)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(mysteps=message.text)
    await message.answer('Сколько всего спал?')
    await state.set_state(ClientState.total_sleep)


@dp.message(ClientState.total_sleep)
async def process_dont_like_write_bots(message: Message, state: FSMContext):
    await state.update_data(total_sleep=message.text)
    await message.answer('Сколько из них глубокий сон?')
    await state.set_state(ClientState.deep_sleep)


@dp.message(ClientState.deep_sleep)
async def process_like_write_bots(message: Message, state: FSMContext):
    await state.update_data(deep_sleep=message.text)
    await message.answer('Хочешь рассказать как прошел день? Это поможет отслеживать почему день был хороший или нет')
    await state.set_state(ClientState.about_day)

@dp.message(ClientState.about_day)
async def process_unknown_write_bots(message: Message, state: FSMContext):
    await state.update_data(user_message=message.text)
    await message.answer('Насколько из 10 сам оцениваешь день?')
    await state.set_state(ClientState.personal_rate)

@dp.message(ClientState.personal_rate)
async def process_unknown_write_bots(message: Message, state: FSMContext):
    await state.update_data(rate=message.text)
    date = datetime.now()
    user_states_data = await state.get_data()
    activities = user_states_data['activities']
    user_message = user_states_data['user_message']
    total_sleep = user_states_data['total_sleep']
    deep_sleep = user_states_data['deep_sleep']
    rate = user_states_data['rate']
    scores = user_states_data['scores']
    mysteps = user_states_data['mysteps']
    user_id = user_states_data['user_id']
    user_name = message.from_user.username
    await add_day_to_excel(date, activities, user_message, total_sleep, deep_sleep, rate, mysteps, message, user_id, scores, user_name)
    await state.set_state(ClientState.greet)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

