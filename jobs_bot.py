from openpyxl import load_workbook
from datetime import datetime, timedelta
import telebot
import requests
import json
bot = telebot.TeleBot(token='6635829285:AAGhpvRdh-6DtnT6DveZEky0tt5U_PejLXs')
def send_message(message):
    BOT_TOKEN = '6635829285:AAGhpvRdh-6DtnT6DveZEky0tt5U_PejLXs'
    CHAT_ID = '1091698279'
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.post(url, json=payload)
    result = json.loads(response.content)
    return result
scores = {'встал в 6:30': 1, 'лег в 11': 1, 'умылся льдом': 1, 'контрастный душ': 1, 'сделал зарядку': 1, 'дрочил': -1}
activities = []
def add_day_to_excel(date, activities):
    # Загрузка существующего файла Excel
    wb = load_workbook('результат.xlsx')

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

    # Вычисление итогового счета
    score = 0
    for activity in activities:
        if activity == "работал":
            score += 0.5
        elif activity == "гулял":
            score += 1
        elif activity == "занимался вокалом":
            score += 2

    # Вставка итогового счета в таблицу
    sheet.cell(row=last_row+1, column=4).value = score

    # Сохранение изменений в файл
    wb.save("результат.xlsx")
def about_day_to_excel(user_message):
    # Загрузка существующего файла Excel
    wb = load_workbook('результат.xlsx')

    # Получение активного листа
    sheet = wb.active

    # Поиск последней заполненной строки в столбце "Дата"
    last_row = sheet.max_row

    # Вставка дел в таблицу
    sheet.cell(row=last_row+1, column=3).value = user_message

    # Вычисление итогового счета
    score = 0
    for activity in activities:
        if activity == "работал":
            score += 0.5
        elif activity == "гулял":
            score += 1
        elif activity == "занимался вокалом":
            score += 2

    # Вставка итогового счета в таблицу
    sheet.cell(row=last_row+1, column=4).value = score

    # Сохранение изменений в файл
    wb.save("результат.xlsx")

send_message('Расскажи мне как провел вчерашний день?' + '\n' + 'Вот возможный список дел:' + '\n' + '\n' +  ', '.join(scores.keys()))
date = datetime.now()
@bot.message_handler(content_types=['text'])
def send_text(message):
    msg = bot.reply_to(message, 'Хочешь рассказать как прошел день? Это поможет отслеживать почему день был хороший или нет')
    user_message=message.text
    for activy in user_message.split(', '):
        activities.append(activy)
    add_day_to_excel(date, activities)
    bot.register_next_step_handler(msg, process_name_step)
def process_name_step(message):
    user_message = message.text
    about_day_to_excel(user_message)




bot.polling()