import asyncio
from openpyxl import load_workbook
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import types
from aiogram import F
from aiogram.types import FSInputFile
import os

from openpyxl.workbook import Workbook

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()
scores = {'встал в 6:30': 1, 'лег в 11': 1, 'умылся льдом': 1, 'контрастный душ': 1, 'сделал зарядку': 1, 'позанимался вокалом' : 1, 'сходил за водой': 1,'правильно питался': 1, 'читал книгу': 1, 'шаги': 1, 'принимал витамины': 1, 'массаж перед сном': 1}


class ClientState(StatesGroup):
    greet = State()
    steps = State()
    total_sleep = State()
    deep_sleep = State()
    about_day = State()
    personal_rate = State()
async def add_day_to_excel(date, activities, user_message, total_sleep, deep_sleep, rate, mysteps, message, user_id):
    # Загрузка существующего файла Excel
    if os.path.exists(f'{user_id}_Diary.xlsx'):
        # If the file exists, load the existing workbook
        wb = load_workbook(f'{user_id}_Diary.xlsx')
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
    sheet.cell(row=last_row+1, column=2).value = ", ".join(activities)
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
    for activity in activities:
        score += scores[activity]

    # Вставка итогового счета в таблицу
    sheet.cell(row=last_row+1, column=8).value = score

    # Сохранение изменений в файл
    wb.save(f'{user_id}_Diary.xlsx')
    await message.answer('Готово! Вы в любой момент можете скачать файл по кнопке ниже')
async def send_message(message) -> None:
    await message.answer('Расскажи мне как провел вчерашний день?' + '\n' + 'Вот возможный список дел:' + '\n' + '\n' +  ', '.join(scores.keys()))

@dp.message(F.text == 'Скачать таблицу')
async def download(message: Message) -> None:
    if os.path.exists(f'{message.from_user.id}_Diary.xlsx'):
        await message.answer_document(
            document=FSInputFile(f'{message.from_user.id}_Diary.xlsx'),
            disable_content_type_detection=True,
        )





    else:
        await message.answer('Сначала заполните данные')
@dp.message(CommandStart())
async def greetings(message: Message, state: FSMContext) -> None:
    kb = [[types.KeyboardButton(text="Скачать таблицу")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await state.update_data(user_id=message.from_user.id)
    info = await bot.get_me()
    name = info.username
    if not os.path.exists(f'{message.from_user.id}_Diary.xlsx'):
        await message.answer_sticker('CAACAgIAAxkBAAIsZGVY5wgzBq6lUUSgcSYTt99JnOBbAAIIAAPANk8Tb2wmC94am2kzBA', reply_markup=keyboard)
        await message.answer('Привет, ' + message.from_user.full_name + '!' + '\n' + 'Добро пожаловать в ' + name + '!' + '\n' + 'Он поможет тебе вести отчет о твоих днях и делать выводы почему день был плохим или хорошим')
        await message.answer('Расскажи мне как провел вчерашний день?' + '\n' + 'Вот возможный список дел:' + '\n' + '\n' +  ', '.join(scores.keys()))
    scheduler = AsyncIOScheduler(timezone = "Europe/Moscow")
    scheduler.add_job(send_message, 'cron', hour=7, minute=10, args=(message,))
    scheduler.start()
    await state.set_state(ClientState.greet)

@dp.message(ClientState.greet)
async def command_start(message: Message, state: FSMContext):
    activities = [activity for activity in message.text.split(', ') if activity in scores]

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
    mysteps = user_states_data['mysteps']
    user_id = user_states_data['user_id']
    await add_day_to_excel(date, activities, user_message, total_sleep, deep_sleep, rate, mysteps, message, user_id)
    await state.set_state(ClientState.greet)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

