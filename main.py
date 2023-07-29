import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import time
import telebot
import sys

bot = telebot.TeleBot(token='6635829285:AAGhpvRdh-6DtnT6DveZEky0tt5U_PejLXs')
url = "https://dltv.org/matches"


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


def welcome():
    redflag = True
    flag1 = 1
    flag2 = 1
    flag3 = 1
    flag4 = 1
    flag5 = 1
    current_time = datetime.now() + timedelta(minutes=30)
    while redflag == True or datetime.now() < current_time:
        live_matches = []
        answ = []
        response = requests.get(url)
        dire_pick = dict()
        radiant_pick = dict()
        soup = BeautifulSoup(response.text, "lxml")
        page = soup.find_all(class_='live__matches-item__body')
        for i in page:
            for q in i.find_all(class_='match__item-team__name'):
                live_matches.append(q.find('div').text.strip())
        if live_matches != []:
            gen = iter(live_matches)
            for i in range(len(live_matches)):
                try:
                    answ.append([next(gen), next(gen)])
                except:
                    pass
            if flag4:
                flag4 = 0
                send_message('Сейчас играют ' + str(len(answ)) + ' матча')
            # Получаю id матчей
            elements = soup.find_all(attrs={"data-series-id": True})
            data_series_ids = [element["data-series-id"] for element in elements]
            for matches_number in range(len(answ)):
                answ[matches_number] = [','.join(answ[matches_number]) + "," + str((data_series_ids[matches_number]))]
            # получение пиков
            # if len(answ) != 1:
            #     exact_match = input('Введите интересующие матчи через запятую: ')
            #     if exact_match != '':  # 1,2
            #         if len(exact_match.split(',')) > len(answ):
            #             exact_match = input('Вы ввели неправильное число, введите корретные номера матчей')
            #         else:
            #             new_answ = []
            #             exact_match = exact_match.split(',')
            #             if len(exact_match) > 1:
            #                 for i in exact_match:
            #                     new_answ.append(answ[int(i) - 1])
            #             elif len(exact_match) == 1:
            #                 new_answ = [answ[int(''.join(exact_match)) - 1]]
            #             answ = new_answ
            for data in answ:
                dotafix_unsure = False
                dotafix_sure_flag = False
                dotapicker_sure_flag = False
                dotapicker_unsure = False
                dotapicker_risk = False
                dotafix_risk = False
                if flag5:
                    flag5 = 0
                    send_message(data[0].split(',')[0] + " ПРОТИВ " + data[0].split(',')[1])
                match_url = ('https://dltv.org/matches/' + str(''.join(data).split(',')[2]))
                response = requests.get(match_url)
                match_url_soup = BeautifulSoup(response.text, "lxml")
                everything = match_url_soup.find(class_='picks__new-picks')
                if everything is not None:
                    #проверяю начались ли пики
                    radiant_team_name = everything.find(class_='title')
                    if re.search(data[0].split(',')[0], radiant_team_name.text):
                        radiant_team_name = data[0].split(',')[0]
                        dire_team_name = data[0].split(',')[1]
                    else:
                        radiant_team_name = data[0].split(',')[1]
                        dire_team_name = data[0].split(',')[0]
                    radiant_heroes_and_ids_block = everything.find(class_="picks__new-picks__picks radiant")
                    radiant_heroes_and_ids = radiant_heroes_and_ids_block.find_all(class_="pick player")
                    for info in radiant_heroes_and_ids:
                        radiant_pick[info["data-tippy-content"]] = info["data-hero-id"]
                    dire_heroes_and_ids_block = everything.find(class_="picks__new-picks__picks dire")
                    dire_heroes_and_ids = dire_heroes_and_ids_block.find_all(class_="pick player")
                    for info in dire_heroes_and_ids:
                        dire_pick[info["data-tippy-content"]] = info["data-hero-id"]



                    if len(dire_pick) == 5 and len(radiant_pick) == 5:
                        redflag=False
                    # анализ пиков
                        # счет в матче
                        score = match_url_soup.find(class_='score__scores live').find_all('span')
                        score_list = []
                        for i in score:
                            score_list.append(i.text.strip())
                        send_message('Счет ' + score_list[0] + ' - ' + score_list[1])
                        # Продолжительность авераге матчей
                        radiant_match_duration = [i.text for i in
                                                  match_url_soup.find_all(class_="cell text-red text-center")]
                        dire_match_duration = [i.text for i in
                                               match_url_soup.find_all(class_="cell text-gray text-center")]
                        radiant_match_duration = float(radiant_match_duration[1].strip(' min'))
                        dire_match_duration = float(dire_match_duration[1].strip(' min'))
                        ####
                        options = Options()
                        # options.add_argument("window-size=1920,1080")
                        options.add_argument("--start-maximized")
                        options.add_argument("--no-sandbox")
                        driver = webdriver.Chrome(options=options)

                        # dotapicker
                        radiant = ''.join(['/T_' + element.replace(' ', '_') for element in radiant_pick.keys()])
                        dire = ''.join(['/E_' + element.replace(' ', '_') for element in dire_pick.keys()])

                        url_dotapicker = "https://dotapicker.com/herocounter#!" + dire + radiant + "/S_0_matchups"
                        send_message(url_dotapicker)
                        # Download and specify the path to your chromedriver executable
                        driver.get(url_dotapicker)
                        time.sleep(10)
                        select_element = driver.find_element(By.NAME, 'component')
                        select = Select(select_element)
                        select.select_by_index(0)
                        elements = driver.find_elements(By.CSS_SELECTOR, '[align="middle"]')
                        elements = [int(elements[7].text), int(elements[11].text)]
                        driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[3]').click()
                        elements_winrate = driver.find_elements(By.CSS_SELECTOR, '[align="middle"]')
                        elements_winrate = [int(elements_winrate[7].text), int(elements_winrate[11].text)]
                        # print(answ)
                        # РАЗОБРАТЬСЯ С ELEMENTS_WINRATE И ПРОСТО ELEMENTS
                        if elements[0] >= 20 and elements[1] >= 20 and elements_winrate[0] >= 20 and elements_winrate[
                            1] >= 20:
                            send_message('dotapicker.com УВЕРЕН что победит ' + radiant_team_name)
                            dotapicker_winner = radiant_team_name
                            dotapicker_sure_flag = 1

                        elif elements[0] >= 10 and elements[1] >= 10 and elements_winrate[0] > 10 and elements_winrate[
                            1] > 10:
                            send_message('dotapicker.com считает что скорее всего победит ' + radiant_team_name)
                            dotapicker_winner = radiant_team_name
                        elif elements[0] > 0 and elements[1] > 0 and elements_winrate[0] > 0 and elements_winrate[
                            1] > 0:
                            send_message('dotapicker.com РИСКОВО считает что скорее всего победит ' + radiant_team_name)
                            dotapicker_winner = radiant_team_name
                            dotapicker_risk = 1
                        elif elements[0] <= -20 and elements[1] <= -20 and elements_winrate[0] <= -20 and elements_winrate[
                            1] <= -20:
                            send_message('dotapicker.com УВЕРЕН что победит ' + dire_team_name)
                            dotapicker_winner = dire_team_name
                            dotapicker_sure_flag = 1
                        elif elements[0] <= -10 and elements[1] <= -10 and elements_winrate[0] <= -10 and elements_winrate[
                            1] <= -10:
                            send_message('dotapicker.com считает что скорее всего победит ' + dire_team_name)
                            dotapicker_winner = dire_team_name
                        elif elements[0] < 0 and elements[1] < 0 and elements_winrate[0] < 0 and elements_winrate[
                            1] < 0:
                            send_message('dotapicker.com РИСКОВО считает что скорее всего победит ' + dire_team_name)
                            dotapicker_winner = dire_team_name
                            dotapicker_risk = 1
                        #
                        else:
                            dotapicker_unsure = True
                            dotapicker_winner = 'неуверен ' + radiant_team_name + ': Counterpick = ' + str(
                                elements[0]) + ' WR ' + str(
                                elements_winrate[0]) + ' Synergy = ' + str(elements[1]) + ' WR ' + str(elements_winrate[1])
                            send_message('dotapicker.com неуверен в победителе ' + dotapicker_winner)

                        ####dotafix.github

                        radiant = ''.join(['&m=' + element for element in radiant_pick.values()])
                        dire = ''.join(['&e=' + element for element in dire_pick.values()])
                        dire = '?' + dire[1:]
                        url_dotafix = "https://dotafix.github.io/" + dire + radiant
                        driver.get(url_dotafix)

                        try:
                            element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, 'rankData')))
                            select_element = driver.find_element(By.ID, 'rankData')
                            select = Select(select_element)
                            select.select_by_index(9)
                        except:
                            driver.refresh()
                            time.sleep(6)
                            select_element = driver.find_element(By.ID, 'rankData')
                            select = Select(select_element)
                            select.select_by_index(9)
                        driver.find_element(By.CSS_SELECTOR, '[style="font-size: 20px;"]').click()
                        alert = Alert(driver)
                        alert_text = alert.text
                        alert.accept()
                        alert_text_1 = alert_text.split("The following was copied to the clipboard:")[1].strip()
                        datan = re.findall('[0-9]{1,}\.[0-9]{1,}', alert_text_1)
                        if len(datan) != 3:
                            driver.refresh()
                            time.sleep(10)
                            driver.find_element(By.CSS_SELECTOR, '[style="font-size: 20px;"]').click()
                            alert = Alert(driver)
                            alert_text = alert.text
                            alert.accept()
                            alert_text_1 = alert_text.split("The following was copied to the clipboard:")[1].strip()
                            datan = re.findall('[0-9]{1,}\.[0-9]{1,}', alert_text_1)
                        datan = [int(float(datan_element)) for datan_element in datan]
                        if datan[0] <= 40 and datan[1] <= 40 and datan[2] <= 40:
                            send_message('dotafix.github.io УВЕРЕН что победит ' + dire_team_name)
                            dotafix_github_winner = dire_team_name
                            dotafix_sure_flag = True
                        elif datan[0] <= 45 and datan[1] <= 45 and datan[2] <= 45:
                            send_message('dotafix.github.io думает что победит ' + dire_team_name)
                            dotafix_github_winner = dire_team_name
                        elif datan[0] < 50 and datan[1] < 50 and datan[2] < 50:
                            send_message('dotafix.github.io РИСКОВО думает что победит ' + dire_team_name)
                            dotafix_github_winner = dire_team_name
                            dotafix_risk = True

                        elif datan[0] >= 60 and datan[1] >= 60 and datan[2] >= 60:
                            send_message('dotafix.github.io УВЕРЕН что победит ' + radiant_team_name)
                            dotafix_github_winner = radiant_team_name
                            dotafix_sure_flag = True
                        elif datan[0] >= 55 and datan[1] >= 45 and datan[2] >= 55:
                            send_message('dotafix.github.io думает что победит ' + radiant_team_name)
                            dotafix_github_winner = radiant_team_name
                        elif datan[0] > 50 and datan[1] > 50 and datan[2] > 50:
                            send_message('dotafix.github.io РИСКОВО думает что победит ' + radiant_team_name)
                            dotafix_github_winner = radiant_team_name
                            dotafix_risk = True
                        else:
                            dotafix_github_unsure = True
                            dotafix_github_winner = 'НЕУВЕРЕН ' + radiant_team_name + ' Winrate: Early ' + str(
                                datan[0]) + 'Mid ' + str(
                                datan[1]) + 'Late ' + str(datan[2])
                            send_message('dotafix.github.io неуверен в победителе ' + dotafix_github_winner)

                        # dotatools:
                        dire = ''.join([str(element) + ',' for element in dire_pick.values()])
                        radiant = [str(element) + ',' for element in radiant_pick.values()]
                        radiant = ''.join(radiant[:1])
                        url_dotatools = 'https://dotatools.ru/api/v1/predict_victory?dire_hero_ids=' + dire + '&radiant_hero_ids=' + radiant + '&rank=immortal'
                        picks = requests.get(url_dotatools)
                        a = picks.text
                        b = re.findall('[0-9]\.[0-9]', a)
                        if b[0] > b[1]:
                            send_message('dotatools считает что победит ' + dire_team_name)
                            dotatools_dotapicker_winner = dire_team_name
                        elif b[0] < b[1]:
                            send_message('dotatools считает что победит ' + radiant_team_name)
                            dotatools_dotapicker_winner = radiant_team_name

                        else:
                            send_message('dotatools неуверен в победителе')
                            dotatools_dotapicker_winner = 'неуверен в победителе'

                        with open('new_matches_results.txt', 'a') as f:
                            f.write(
                                '================================================================================' + '\n' +
                                'Ссылка ' + match_url + '\n' + '      ' + radiant_team_name + ' ПРОТИВ ' + dire_team_name + '\n' +
                                '           Счет ' + score_list[0] + ' - ' + score_list[1] + '\n' +
                                'dotatools  победитель - ' + dotatools_dotapicker_winner + '\n' +
                                'dotafix.gi победитель - ' + dotafix_github_winner + '\n' +
                                'dotapicker победитель - ' + dotapicker_winner + '\n' +
                                '================================================================================' + '\n')

                        radiant_pick, dire_pick, counter = dict(), dict(), 0
                        if dotafix_github_winner == dotapicker_winner and (dotapicker_sure_flag and dotafix_sure_flag):
                            send_message('            ALL IN BABYYYY')
                        elif dotafix_github_winner == dotapicker_winner and (dotapicker_sure_flag or dotafix_sure_flag):
                            send_message('            Алгоритмы уверены. КРУПНАЯ Ставка РАЗРЕШЕНА')
                        elif dotapicker_winner == dotafix_github_winner and (dotafix_risk or dotapicker_risk):
                            send_message('            Малая РИСКОВАЯ Ставка РАЗРЕШЕНА')
                        elif dotapicker_winner == dotafix_github_winner:
                            send_message('            Ставка РАЗРЕШЕНА')
                        elif dotafix_unsure or dotapicker_unsure:
                            send_message('            Ставка ЗАПРЕЩЕНА')
                            if radiant_match_duration >= 36 and dire_match_duration >= 36:
                                send_message('Ставка на ВРЕМЯ РАЗРЕШЕНА')
                            else:
                                send_message('Ставка на время ТАКЖЕ ЗАПРЕЩЕНА')
                        driver.quit()
                    else:
                        if flag2:
                            send_message('               Пики еще не закончились')
                            flag2 = 0
                        time.sleep(30)
                else:
                    if flag1:
                        send_message('               Пики еще не начались')
                        flag1 = 0
                    time.sleep(30)
            pass
        else:
            if flag3:
                flag3 = 0
                send_message('                    Сейчас нету активных матчей :С')
            time.sleep(30)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет')


@bot.message_handler(commands=['button'])
def button_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Анализировать текущие матчи")
    markup.add(item1)


@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text == "Анализировать текущие матчи":
        welcome()
        bot.send_message(message.chat.id, 'Работа завершена')
        print('Работа завершена')



bot.infinity_polling()
