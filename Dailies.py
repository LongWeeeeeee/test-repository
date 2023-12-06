import asyncio
from openpyxl import load_workbook
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import types
from aiogram import F
from aiogram.filters import Command
import pandas as pd
from aiogram.types import FSInputFile
import json
import os
from openpyxl.workbook import Workbook
import keys

bot = Bot(token=keys.Token)
dp = Dispatcher()
start = True


class ClientState(StatesGroup):
    greet = State()
    new_daily_scores = State()
    steps = State()
    total_sleep = State()
    deep_sleep = State()
    about_day = State()
    personal_rate = State()
    settings = State()
    download = State()
    jobs = State()
    one_time_job_2 = State()
    one_time_job_proceed = State()

@dp.message(Command(commands=["start"]))
async def greetings(message: Message, state: FSMContext):
    global start
    await state.update_data(user_id=message.from_user.id)
    info = await bot.get_me()
    name = info.username
    flag = False

    if os.path.exists('daily_scores.txt'):
        with open('daily_scores.txt', 'r+', encoding='utf-8') as f:
            score_list = json.load(f)
            for line in score_list:
                if message.from_user.id == line['user_id']:
                    flag = True
                    daily_scores = line['daily_scores']
                    await state.update_data(daily_scores=daily_scores)
                    if os.path.exists(f'{message.from_user.username}_Diary.xlsx'):
                        kb = [[types.KeyboardButton(text="Скачать дневник"),
                               types.KeyboardButton(text="Изменить Настройки"),
                               types.KeyboardButton(text="Вывести дневник")]]
                        keyboard = types.ReplyKeyboardMarkup(
                            keyboard=kb,
                            resize_keyboard=True,
                        )
                    else:
                        kb = [
                            [types.KeyboardButton(text="Изменить Настройки")]]
                        keyboard = types.ReplyKeyboardMarkup(
                            keyboard=kb,
                            resize_keyboard=True,
                        )
                    await message.answer(
                        'Расскажи мне как провел вчерашний день?' + '\n' + 'Вот список ежедневных дел:')

                    await message.answer(', '.join(daily_scores.keys()), reply_markup=keyboard)
                    if 'one_time_jobs' in line:
                        await message.answer(
                            'Разовые дела:')
                        await message.answer(', '.join(line['one_time_jobs']))
                    await message.answer(
                        'Впишите ежедневные дела которые вы вчера делали' + '\n'
                        + 'Вы можете изменить списки в любой момент')
                    await state.set_state(ClientState.greet)
    else:
        with open('daily_scores.txt', 'w') as file:
            json.dump([], file, ensure_ascii=False, indent=4)
    if not flag:
        markup = types.ReplyKeyboardRemove()
        await message.answer_sticker('CAACAgIAAxkBAAIsZGVY5wgzBq6lUUSgcSYTt99JnOBbAAIIAAPANk8Tb2wmC94am2kzBA')
        await message.answer(
            f'''Привет, {message.from_user.full_name}! \nДобро пожаловать в {name}!
Он поможет тебе вести отчет о твоих днях и делать выводы почему день был плохим или хорошим
Для начала нужно задать список дел. Какие у вас есть дела в течении дня? Например:''')
        await message.answer('встал в 6:30, лег в 11, зарядка утром, массаж, пп')
        await message.answer(
            'Вы можете воспользоваться предложенным списком или написать свой. Данные могут быть какие угодно',
            reply_markup=markup)
        await state.set_state(ClientState.new_daily_scores)
    if start:
        start = False
        scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
        scheduler.add_job(greetings, 'cron', hour=8, minute=45, args=(message, state))
        scheduler.start()


@dp.message(F.text == 'Вывести дневник')
async def settings(message: Message, state: FSMContext):
    user_name = message.from_user.username
    # Получение активного листа
    data = pd.read_excel(f'{user_name}_Diary.xlsx')

    async def format_message(row):
        message = "{} | {} | {} | {} | {} | {} | {} | {}".format(row["Дата"], row["Дела за день"], row["Шаги"],
                                                                 row["Total sleep"], row['Deep sleep'], row['О дне'],
                                                                 row['My rate'], row['Total'])
        return message

    await message.answer(
        "{} | {} | {} | {} | {} | {} | {} | {}".format("Дата", "Дела за день", "Шаги", "Total sleep", 'Deep sleep',
                                                       'О дне', 'My rate', 'Total'))
    for index, row in data.iterrows():
        message_sheet = await format_message(row)

        # разделение длинного сообщения на части
        message_parts = [message_sheet[i:i + 4096] for i in range(0, len(message_sheet), 4096)]

        for part in message_parts:
            await message.answer(part)
    await state.set_state(ClientState.greet)
    # Вывод данных в консоль


@dp.message(F.text == 'Изменить Настройки')
async def settings(message: Message, state: FSMContext):
    kb = [[types.KeyboardButton(text="Изменить Дела"),
           types.KeyboardButton(text='''Что такое "стоимость"?'''), types.KeyboardButton(text="Изменить Стоимость"),
           types.KeyboardButton(text="Заполнить дневник")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )
    await message.answer(text='Здесь вы можете изменить свои настройки', reply_markup=keyboard)
    await state.set_state(ClientState.settings)


@dp.message(F.text == 'Заполнить дневник', ClientState.settings)
async def fill_diary(message: Message, state: FSMContext) -> None:
    await greetings(message, state)


@dp.message(F.text == 'Изменить Стоимость', ClientState.settings)
async def download(message: Message, state: FSMContext = None) -> None:
    markup = types.ReplyKeyboardRemove()
    await message.answer(
        'Ниже представлен ваш ежедневный список дел и его стоимость в формате "дело: оценка" '
        'Скопируйте список и отправьте его с обновленными оценками', reply_markup=markup)
    file = open('daily_scores.txt', 'r+', encoding='utf-8')
    data = file.read()
    if data != '':
        score_list = json.loads(data)
        for line in score_list:
            if message.from_user.id == line['user_id']:
                daily_scores = line['daily_scores']
                formatted_string = ''
                for key, value in daily_scores.items():
                    formatted_string += f"{key} : {value}, "
                await message.answer(formatted_string[:-2])
                await state.set_state(ClientState.new_daily_scores)


@dp.message(F.text == '''Что такое "стоимость"?''', ClientState.settings)
async def download(message: Message) -> None:
    await message.answer(
        '''Стоимость нужна для подсчета очков за ваш день. Изначально стоимость любого дела равна 1,
но вы можете переназначить собственное значение. Нужны они для того составить обьективную картину.\n
Представим ситуацию, у вас был тяжелый день, и вы чувтсвуете себя совершенно разбитым
под конец дня и ставите этому дню оценку 0, однако за этот же день вы делали что-то из
списка своих дел, например правильно питались, учили новые языки или еще что-то, и день
уже не кажется таким плохим, потому что вы сделали свою рутину. Очки это обьективная оценка
дня, тогда как ваша персональная оценка это субьективная оценка и может быть не до конца точной''')


@dp.message(F.text == 'Изменить Дела', ClientState.settings)
async def jobs_change(message: Message, state: FSMContext = None) -> None:
    kb = [[types.KeyboardButton(text="Ежедневные дела"),
           types.KeyboardButton(text="Разовые дела"),
           types.KeyboardButton(text='В определенную дату')]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )
    await message.answer(text='Вывожу список...', reply_markup=keyboard)
    await state.set_state(ClientState.jobs)


@dp.message(F.text == 'В определенную дату', ClientState.jobs)
async def date_job(message: Message, state: FSMContext) -> None:
    pass


@dp.message(F.text == 'Разовые дела', ClientState.jobs)
async def one_time_job(message: Message, state: FSMContext) -> None:
    with open('daily_scores.txt', 'r+', encoding='utf-8') as f:
        line = json.load(f)
        markup = types.ReplyKeyboardRemove()
        for user in line:
            if message.from_user.id == user['user_id']:
                if 'one_time_jobs' in user:
                    one_time_jobs = user['one_time_jobs']
                    await message.answer(
                        'Введите новый список разовых дел через запятую. Ваш предыдущий список:', reply_markup=markup)

                    await message.answer(', '.join(one_time_jobs))
                else:
                    await message.answer('Введите новый список разовых дел через запятую', reply_markup=markup)
                await state.set_state(ClientState.one_time_job_2)


@dp.message(ClientState.one_time_job_2)
async def one_time_job(message: Message, state: FSMContext) -> None:
    one_time_job_str = message.text.lower().split(', ')
    with open('daily_scores.txt', 'r+', encoding='utf-8') as f:
        data = json.load(f)
        for user in data:
            if message.from_user.id == user['user_id']:
                user['one_time_jobs'] = one_time_job_str

        f.truncate()  # Обрезать файл после чтения данных
        f.seek(0)  # Переставить указатель на начало файла
        json.dump(data, f, ensure_ascii=False, indent=4)
        await message.answer('Отлично, теперь ваш список разовых дел выглядит так:')
        await message.answer(', '.join(one_time_job_str))
        await state.set_state(ClientState.settings)
        await settings(message, state)

@dp.message(F.text == 'Ежедневные дела', ClientState.jobs)
async def daily_jobs(message: Message, state: FSMContext) -> None:
    markup = types.ReplyKeyboardRemove()
    await message.answer('Введите новый список ежедневных. Ваш предыдущий список: ', reply_markup=markup)
    with open('daily_scores.txt', 'r+', encoding='utf-8') as f:
        score_list = json.load(f)
        for line in score_list:
            if message.from_user.id == line['user_id']:
                daily_scores = line['daily_scores']
                formatted_string = ""
                for key, value in daily_scores.items():
                    formatted_string += f"{key}, "

                await message.answer(formatted_string[:-2])
                await message.answer(
                    'Вы можете воспользоваться предложенным списком или написать свой. Данные могут быть какие '
                    'угодно, очки нужны для отчетности о том насколько продуктивен был день.\nСоблюдайте формат '
                    'данных!')
                await state.set_state(ClientState.new_daily_scores)


@dp.message(F.text == 'Скачать дневник')
async def download(message: Message) -> None:
    if os.path.exists(f'{message.from_user.username}_Diary.xlsx'):
        await message.answer_document(
            document=FSInputFile(f'{message.from_user.username}_Diary.xlsx'),
            disable_content_type_detection=True,
        )
    else:
        await message.answer('Сначала заполните данные')


@dp.message(ClientState.new_daily_scores)
async def command_start(message: Message, state: FSMContext):
    job_value = False
    daily_scores = dict()
    user_message = message.text
    str_data = user_message.split(', ')
    for one_job in str_data:
        one_job = one_job.split(' : ')
        if len(one_job) == 1:
            daily_scores[one_job[0].lower().replace('ё', 'е')] = 1
        else:
            job_value = True
            daily_scores[one_job[0].lower().replace('ё', 'е')] = one_job[1]
    if job_value:
        string = ''
        for key, value in daily_scores.items():
            string += f'{key} : {value}, '
        await message.answer('Стоимость изменена. Теперь она выглядит так: \n' + string[:-1])
    await state.update_data(daily_scores=daily_scores)
    with open('daily_scores.txt', 'r+', encoding='utf-8') as f:
        score_list = json.load(f)
        found = False
        if score_list:
            for user in score_list:
                if message.from_user.id == user['user_id']:
                    found = True
                    if not job_value:
                        for old_job in user['daily_scores']:
                            if old_job in daily_scores:
                                daily_scores[old_job] = user['daily_scores'][old_job]
                        user['daily_scores'] = daily_scores
                        f.truncate(0)
                        f.seek(0)
                        json.dump(score_list, f, ensure_ascii=False, indent=4)
                    else:
                        user['daily_scores'] = daily_scores
                        f.truncate(0)
                        f.seek(0)
                        json.dump(score_list, f, ensure_ascii=False, indent=4)
            if not found:
                score_list.append({'daily_scores': daily_scores, 'user_id': message.from_user.id})
                f.truncate(0)
                f.seek(0)
                json.dump(score_list, f, ensure_ascii=False, indent=4)
        else:
            score_list.append({'daily_scores': daily_scores, 'user_id': message.from_user.id})
            f.truncate(0)
            f.seek(0)
            json.dump(score_list, f, ensure_ascii=False, indent=4)
        await state.set_state(ClientState.settings)
        await settings(message, state)


@dp.message(ClientState.greet)
async def my_steps(message: Message, state: FSMContext):
    error = False
    with open('daily_scores.txt', 'r+', encoding='utf-8') as f:
        line = json.load(f)
        for user in line:
            if message.from_user.id == user['user_id']:
                daily_scores = user['daily_scores']
                # обработка ежедневных дел
                if len(daily_scores) > 1:
                    activities = []
                    for activity in message.text.split(', '):
                        activity = activity.lower().replace('ё', 'е')
                        if activity in daily_scores:
                            activities.append(activity)
                        else:
                            await message.answer(f"{activity} нету в списке!")
                            error = True
                    if error:
                        await message.answer(message.text + ' содержит ошибку')
                else:
                    activities = message.text.strip(',')
                if len(activities) >= 1 and not error:
                    await state.update_data(activities=activities)
                    if 'one_time_jobs' in user:
                        one_time_jobs = user['one_time_jobs']
                        await message.answer('Введите разовые дела, которые выполнили. Список разовых дел:')
                        await message.answer(', '.join(one_time_jobs))
                        await state.set_state(ClientState.one_time_job_proceed)
                    else:
                        await message.answer("Сколько сделал шагов?")
                        await state.set_state(ClientState.steps)


@dp.message(ClientState.one_time_job_proceed)
async def process_one_time(message: Message, state: FSMContext):
    text = message.text.split(', ')
    error = False
    exit = False
    with open('daily_scores.txt', 'r+', encoding='utf-8') as f:
        data = json.load(f)
        for user in data:
            if message.from_user.id == user['user_id']:
                if 'one_time_jobs' in user:
                    one_time_jobs = user['one_time_jobs']
                    for job in text:
                        if job.lower().replace('ё', 'е') in one_time_jobs:
                            one_time_jobs.remove(job.lower().replace('ё', 'е'))
                        else:
                            if job.lower().replace('ё', 'е') in ['не', 'нет', '-', 'pass', 'пасс', 'не хочу', 'скип',
                                                                 'пососи', 'пошел нахуй', 'неа', 'не-а', 0]:
                                exit = True
                                await message.answer("Сколько сделал шагов?")
                                await state.set_state(ClientState.steps)
                                break
                            else:
                                error = True
                                await message.answer(f'{job} нету в списке разовых дел!')
                    if one_time_jobs != [] and not exit:
                        if not error:
                            await message.answer('Отлично, теперь ваш список разовых дел выглядит так:')
                            await message.answer(', '.join(one_time_jobs))
                    elif not exit:
                        await message.answer('Поздравляю! Вы выполнили все разовые дела, так держать')
                        del user['one_time_jobs']

        if not error and not exit:
            # Move the file pointer to the beginning of the file
            f.seek(0)
            # Write the modified data back to the file
            json.dump(data, f, ensure_ascii=False, indent=4)
            # Truncate any remaining content in the file (in case the new data is shorter)
            f.truncate()
            await message.answer("Сколько сделал шагов?")
            await state.set_state(ClientState.steps)


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
    with open('daily_scores.txt', 'r+', encoding='utf-8') as f:
        line = json.load(f)
        for user in line:
            if message.from_user.id == user['user_id']:
                daily_scores = user['daily_scores']
    date = datetime.now()
    user_states_data = await state.get_data()
    activities = user_states_data['activities']
    user_message = user_states_data['user_message']
    total_sleep = user_states_data['total_sleep']
    deep_sleep = user_states_data['deep_sleep']
    rate = user_states_data['rate']
    mysteps = user_states_data['mysteps']
    user_name = message.from_user.username
    await add_day_to_excel(date, activities, user_message, total_sleep, deep_sleep, rate, mysteps, message,
                           daily_scores,
                           user_name)
    await state.set_state(ClientState.greet)


async def add_day_to_excel(date, activities, user_message, total_sleep, deep_sleep, rate, mysteps, message,
                           daily_scores,
                           user_name):
    # Загрузка существующего файла Excel
    with open('daily_scores.txt', 'r+', encoding='utf-8') as f:
        line = json.load(f)
        for user in line:
            if message.from_user.id == user['user_id']:
                daily_scores = user['daily_scores']
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
    sheet.cell(row=last_row + 1, column=1).value = yesterday.strftime("%d.%m.%Y")

    # Вставка дел в таблицу
    if type(activities) == list:
        sheet.cell(row=last_row + 1, column=2).value = ", ".join(activities)
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
            score += int(daily_scores[activity])
    else:
        score += int(daily_scores[activities])

    # Вставка итогового счета в таблицу
    sheet.cell(row=last_row + 1, column=8).value = score

    # Сохранение изменений в файл
    wb.save(f'{user_name}_Diary.xlsx')
    kb = [[types.KeyboardButton(text="Скачать дневник"), types.KeyboardButton(text="Изменить Настройки"),
           types.KeyboardButton(text="Вывести дневник")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )

    async def counter_negavite(current_word):
        data = pd.read_excel(f'{user_name}_Diary.xlsx')

        # Выбор нужной колонки
        column = data['Дела за день']

        # Переменные для подсчета повторений
        count = 0
        # Проход по каждой строке колонки в обратном порядке
        for words in column.iloc[-1::-1]:
            flag = False
            for word in words.split(', '):
                if word == current_word:
                    # Если текущее слово совпадает с предыдущим,
                    # увеличиваем счетчик повторений
                    flag = True
            if not flag:
                count += 1
            if flag:
                return count
        return count

    async def counter_positive(current_word):
        data = pd.read_excel(f'{user_name}_Diary.xlsx')

        # Выбор нужной колонки
        column = data['Дела за день']

        # Переменные для подсчета повторений
        count = 0
        # Проход по каждой строке колонки в обратном порядке
        for words in column.iloc[-1::-1]:
            flag = False
            for word in words.split(', '):
                if word == current_word:
                    # Если текущее слово совпадает с предыдущим,
                    # увеличиваем счетчик повторений
                    count += 1
                    flag = True
            if not flag:
                if not count and count >= 2:
                    return count
                break
        if count >= 2:
            return count

    total_days = dict()
    for current_word in daily_scores:
        counter_days = await counter_negavite(current_word)
        if counter_days is not None and counter_days >= 3:
            if counter_days in [2, 3, 4]:
                total_days[current_word] = str(counter_days) + ' дня'
            else:
                total_days[current_word] = str(counter_days) + ' дней'
    output = ['{}: {}'.format(key, value) for key, value in total_days.items()]
    result = '\n'.join(output)
    if result != '':
        await message.answer(
            'Вы не делали эти дела уже столько дней: ' + '\n' + result + '\n Может стоит дать им еще один шанс?')
    total_days = dict()
    for current_word in activities:
        counter_days = await counter_positive(current_word)
        if counter_days in [2, 3, 4] and counter_days is not None:
            total_days[current_word] = str(counter_days) + ' дня'
        elif counter_days is not None:
            total_days[current_word] = str(counter_days) + ' дней'
    output = ['{}: {}'.format(key, value) for key, value in total_days.items()]
    result = '\n'.join(output)
    if result != '':
        await message.answer('Поздравляю! Вы соблюдаете эти дела уже столько дней: ' + '\n' + result,
                             reply_markup=keyboard)
    else:
        await message.answer('Дневник заполнен!', reply_markup=keyboard)






async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
