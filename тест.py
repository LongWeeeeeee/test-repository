# шторм клок тайд монки диз

# шторм + клок шторм + тайд шторм + монки шторм + диз
# клок + шторм клок + тайд клок + монки клок + диз
# тайд + шторм тайд + клок тайд + монки тайд + диз
# монки + шторм
#сверха прошлых матчей и прошлых встреч
#Отладка винрейта на старых матчах
#Проверка того что все правильно работает

from telebot import types
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
import requests
from bs4 import BeautifulSoup
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


# лайв матчи
def live_matches():
    redflag = 1

    url = 'https://api.cyberscore.live/api/v1/matches/?limit=20&liveOrUpcoming=1'
    response = requests.get(url).text
    json_data = json.loads(response)
    while redflag:
        for match in json_data['rows']:
            # if match['status'] in {'online', 'draft'} and match['tournament']['tier'] in {1, 2, 3}:
            if match['status'] in {'online', 'draft'}:
                best_of = match['best_of']
                score = match['best_of_score']
                # radiant_team_name = match['team_radiant']['name']
                # dire_team_name = match['team_dire']['name']
                dire_hero_names, dire_hero_ids, radiant_hero_names, radiant_hero_ids, dire_team_rangs, radiant_team_rangs = [], [], [], [], [], []
                map_id = match['id']
                match_url = f'https://cyberscore.live/en/matches/{map_id}/'
                match_data = requests.get(match_url).text
                soup = BeautifulSoup(match_data, 'lxml')
                match_soup = soup.find('script', id='__NEXT_DATA__')
                json_map = json.loads(match_soup.text)['props']['pageProps']['initialState']['matches_item']
                radiant_pick = json_map['picks_team_radiant']
                dire_pick = json_map['picks_team_dire']
                # url_map = f'https://cyberscore.live/_next/data/uc8FSlRmVi4jLOPn5R_t6/en/matches/{map_id}.json?id={map_id}'
                # map_page = requests.get(url_map)
                # json_map = json.loads(map_page.text)
                # radiant_pick = json_map['pageProps']['initialState']['matches_item']['picks_team_radiant']
                # пики
                if dire_pick != None:
                    if len(dire_pick) == 5 and dire_pick[4]['hero'] != '':
                        ranks_fail = 0
                        for radiant_hero in radiant_pick:
                            # Ранги
                            if not radiant_hero['player']['leaderboard_rank']:
                                ranks_fail = True
                            else:
                                radiant_team_rangs.append(radiant_hero['player']['leaderboard_rank'])
                            radiant_hero_names.append(radiant_hero['hero']['label'])
                            radiant_hero_ids.append(radiant_hero['hero']['id_steam'])
                        for dire_hero in dire_pick:
                            # Ранги
                            if not dire_hero['player']['leaderboard_rank']:
                                ranks_fail = True
                            else:
                               dire_team_rangs.append(dire_hero['player']['leaderboard_rank'])
                            dire_hero_names.append(dire_hero['hero']['label'])
                            dire_hero_ids.append(dire_hero['hero']['id_steam'])

                        title = json_map['title']
                        radiant_team_name = \
                        json_map['team_radiant']['name']
                        dire_team_name = json_map['team_dire'][
                            'name']

                        # if  radiant_team_name in {'Army Geniuses', 'IHC Esports'}:
                        # Пики закончились
                        if len(dire_hero_names) == 5 and len(radiant_hero_names) == 5:
                            if not ranks_fail:
                                difference = sum(radiant_team_rangs) - sum(dire_team_rangs)
                                if difference > 0:
                                    send_message(radiant_team_name + ' лучше ранги на ' + str(difference))
                                elif difference < 0:
                                    send_message(dire_team_name + ' лучше ранги на ' + str(difference))
                            send_message(title)
                            redflag = 0
                            send_message(best_of)
                            send_message(score)
                            wr_dict = {}
                            wr_dict_with_radiant = {}
                            wr_dict_with_dire = {}
                            dotafix_unsure = False
                            dotafix_sure_flag = False
                            dotapicker_sure_flag = False
                            dotapicker_unsure = False
                            dotapicker_risk = False
                            dotafix_risk = False
                            redflag = False
                            options = Options()
                            options.add_argument("--start-maximized")
                            options.add_argument("--no-sandbox")
                            driver = webdriver.Chrome(options=options)

                            # dotapicker
                            radiant = ''.join(['/T_' + element.replace(' ', '_') for element in radiant_hero_names])
                            dire = ''.join(['/E_' + element.replace(' ', '_') for element in dire_hero_names])

                            url_dotapicker = "https://dotapicker.com/herocounter#!" + dire + radiant + "/S_0_matchups"
                            send_message(url_dotapicker)
                            # Download and specify the path to your chromedriver executable
                            driver.get(url_dotapicker)
                            select_element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.NAME, 'component')))
                            select = Select(select_element)
                            select.select_by_index(0)
                            elements = driver.find_elements(By.CSS_SELECTOR, '[align="middle"]')
                            elements = [int(elements[7].text), int(elements[11].text)]
                            driver.find_element(By.XPATH,
                                                '/html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[3]').click()
                            elements_winrate = driver.find_elements(By.CSS_SELECTOR, '[align="middle"]')
                            elements_winrate = [int(elements_winrate[7].text), int(elements_winrate[11].text)]
                            # print(answ)
                            # РАЗОБРАТЬСЯ С ELEMENTS_WINRATE И ПРОСТО ELEMENTS
                            if elements[0] >= 20 and elements[1] >= 20 and elements_winrate[0] >= 20 and \
                                    elements_winrate[
                                        1] >= 20:
                                send_message('dotapicker.com УВЕРЕН что победит ' + radiant_team_name)
                                dotapicker_winner = radiant_team_name
                                dotapicker_sure_flag = 1

                            elif elements[0] >= 10 and elements[1] >= 10 and elements_winrate[0] > 10 and \
                                    elements_winrate[
                                        1] > 10:
                                send_message('dotapicker.com считает что скорее всего победит ' + radiant_team_name)
                                dotapicker_winner = radiant_team_name
                            elif elements[0] > 0 and elements[1] > 0 and elements_winrate[0] > 0 and elements_winrate[
                                1] > 0:
                                send_message(
                                    'dotapicker.com РИСКОВО считает что скорее всего победит ' + radiant_team_name)
                                dotapicker_winner = radiant_team_name
                                dotapicker_risk = 1
                            elif elements[0] <= -20 and elements[1] <= -20 and elements_winrate[0] <= -20 and \
                                    elements_winrate[
                                        1] <= -20:
                                send_message('dotapicker.com УВЕРЕН что победит ' + dire_team_name)
                                dotapicker_winner = dire_team_name
                                dotapicker_sure_flag = 1
                            elif elements[0] <= -10 and elements[1] <= -10 and elements_winrate[0] <= -10 and \
                                    elements_winrate[
                                        1] <= -10:
                                send_message('dotapicker.com считает что скорее всего победит ' + dire_team_name)
                                dotapicker_winner = dire_team_name
                            elif elements[0] < 0 and elements[1] < 0 and elements_winrate[0] < 0 and elements_winrate[
                                1] < 0:
                                send_message(
                                    'dotapicker.com РИСКОВО считает что скорее всего победит ' + dire_team_name)
                                dotapicker_winner = dire_team_name
                                dotapicker_risk = 1
                            #
                            else:
                                dotapicker_unsure = True
                                dotapicker_winner = 'неуверен ' + radiant_team_name + ': Counterpick = ' + str(
                                    elements[0]) + ' WR ' + str(
                                    elements_winrate[0]) + ' Synergy = ' + str(elements[1]) + ' WR ' + str(
                                    elements_winrate[1])
                                send_message('dotapicker.com неуверен в победителе ' + dotapicker_winner)

                            ####dotafix.github

                            radiant = ''.join(['&m=' + element for element in radiant_hero_ids])
                            dire = ''.join(['&e=' + element for element in dire_hero_ids])
                            dire = '?' + dire[1:]
                            url_dotafix = "https://dotafix.github.io/" + dire + radiant
                            send_message(url_dotafix)
                            driver.get(url_dotafix)
                            element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, 'rankData')))
                            select = Select(element)
                            select.select_by_index(8)
                            try:
                                aler_window = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[style="font-size: 20px;"]')))
                                aler_window.click()
                            except:
                                driver.refresh()
                                aler_window = WebDriverWait(driver, 15).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[style="font-size: 20px;"]')))
                                aler_window.click()
                            alert = Alert(driver)
                            alert_text = alert.text
                            alert.accept()
                            alert_text_1 = alert_text.split("The following was copied to the clipboard:")[1].strip()
                            datan = re.findall('[0-9]{1,}\.[0-9]{1,}', alert_text_1)
                            if len(datan) != 3:
                                driver.refresh()
                                aler_window = WebDriverWait(driver, 15).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[style="font-size: 20px;"]')))
                                aler_window.click()
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
                            dire = ''.join([str(element) + ',' for element in dire_hero_ids])
                            radiant = [str(element) + ',' for element in radiant_hero_ids]
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

                            radiant_pick, dire_pick, counter = dict(), dict(), 0
                            if dotafix_github_winner == dotapicker_winner and (
                                    dotapicker_sure_flag and dotafix_sure_flag):
                                send_message('            ALL IN BABYYYY')
                            elif dotafix_github_winner == dotapicker_winner and (
                                    dotapicker_sure_flag or dotafix_sure_flag):
                                send_message('            Алгоритмы уверены. КРУПНАЯ Ставка РАЗРЕШЕНА')
                            elif dotapicker_winner == dotafix_github_winner and (dotafix_risk or dotapicker_risk):
                                send_message('            Малая РИСКОВАЯ Ставка РАЗРЕШЕНА')
                            elif dotapicker_winner == dotafix_github_winner:
                                send_message('            Ставка РАЗРЕШЕНА')
                            elif dotafix_unsure or dotapicker_unsure:
                                send_message('            Ставка ЗАПРЕЩЕНА')
                                # if radiant_match_duration >= 36 and dire_match_duration >= 36:
                                #     send_message('Ставка на ВРЕМЯ РАЗРЕШЕНА')
                                # else:
                                #     send_message('Ставка на время ТАКЖЕ ЗАПРЕЩЕНА')
                            driver.quit()
                            dota2protracker
                            total = 0
                            for hero in radiant_hero_names:
                                wr_dict[hero] = []
                                wr_dict_with_radiant[hero] = []

                                url_dota2_protracker = f'https://www.dota2protracker.com/hero/{hero}'
                                response = requests.get(url_dota2_protracker)
                                soup = BeautifulSoup(response.text, "lxml")
                                hero_names = soup.find_all('td', class_='td-hero-pic')
                                wr_percentage = soup.find_all('div', class_='perc-wr')
                                percent_iter = iter(wr_percentage)
                                hero_names = [dota2protracker_hero_name.get('data-order') for dota2protracker_hero_name in hero_names]
                                for dota2protracker_hero_name in hero_names:
                                    try:
                                        with_wr = next(percent_iter).text.strip()
                                        against_wr = next(percent_iter).text.strip()
                                        percentage = re.match('[0-9]{1,}\.[0-9]{1,}', against_wr).group()
                                        percentage_with = re.match('[0-9]{1,}\.[0-9]{1,}', with_wr).group()
                                        for another_hero in radiant_hero_names:
                                            if another_hero != hero and another_hero == dota2protracker_hero_name:
                                                pre = wr_dict_with_radiant[hero]
                                                pre.append(float(percentage_with))
                                                wr_dict_with_radiant[hero] = pre
                                                pre = 0

                                        for enemy in dire_hero_names:
                                            if enemy == dota2protracker_hero_name:
                                                pre = wr_dict[hero]
                                                pre.append(float(percentage))
                                                wr_dict[hero] = pre
                                                pre = 0
                                    except:
                                        pass

                            for enemy in dire_hero_names:
                                wr_dict[hero] = []
                                wr_dict_with_radiant[hero] = []

                                url_dota2_protracker = f'https://www.dota2protracker.com/hero/{hero}'
                                response = requests.get(url_dota2_protracker)
                                soup = BeautifulSoup(response.text, "lxml")
                                hero_names = soup.find_all('td', class_='td-hero-pic')
                                wr_percentage = soup.find_all('div', class_='perc-wr')
                                percent_iter = iter(wr_percentage)
                                hero_names = [dota2protracker_hero_name.get('data-order') for dota2protracker_hero_name
                                              in hero_names]

                                if enemy not in wr_dict_with_dire:
                                    wr_dict_with_dire[enemy] = []
                                for dota2protracker_hero_name in hero_names:
                                    try:
                                        with_wr = next(percent_iter).text.strip()
                                        against_wr = next(percent_iter).text.strip()
                                        percentage_with = re.match('[0-9]{1,}\.[0-9]{1,}', with_wr).group()
                                        if dota2protracker_hero_name in dire_hero_names and dota2protracker_hero_name != enemy:
                                            pre = wr_dict_with_dire[enemy]
                                            pre.append(float(percentage_with))
                                            wr_dict_with_dire[enemy] = pre
                                            pre = 0
                                    except: pass



                            for i in wr_dict:
                                # total_hero = 0
                                if len(wr_dict[i]) == 5:
                                    total += sum(wr_dict[i])/5
                                else:
                                    send_message('Dota2protracker ERROR')
                            total = total/5
                            if total >= 50:
                                send_message(radiant_team_name + ' dota2protracker Winrate: ' + str(total))
                            else:
                                send_message(dire_team_name + ' dota2protracker Winrate: ' + str(100-total))
                            #Another dota2protracker
                            total_dire = 0
                            total_radiant = 0
                            for dire in wr_dict_with_dire:
                                total_dire += sum(wr_dict_with_dire[dire])/4
                            for radiant in wr_dict_with_radiant:
                                total_radiant += sum(wr_dict_with_radiant[radiant])/4
                            diff = total_radiant/5 - total_dire/5
                            if diff > 0:
                                send_message('Dota2protracker ВТОРОЙ метод: ' + radiant_team_name + ' ' + str(diff) )
                            elif diff < 0:
                                send_message('Dota2protracker ВТОРОЙ метод: ' + dire_team_name + ' ' + str(diff*-1) )
                            # Анализ игроков
                            dire_players = json_map['team_radiant']['players_items']
                            radiant_players = json_map['team_dire']['players_items']
                            if radiant_players[1]['player']['gpm'] != 0 and radiant_players[1]['player']['xpm'] and radiant_players[0]['player']['gpm'] != 0 and radiant_players[0]['player']['xpm'] != 0 and radiant_players[3]['player']['gpm'] != 0 and radiant_players[3]['player']['xpm'] != 0 and dire_players[1]['player']['gpm'] != 0 and dire_players[1]['player']['xpm'] and dire_players[0]['player']['gpm'] != 0 and dire_players[0]['player']['xpm'] != 0 and dire_players[3]['player']['gpm'] != 0 and dire_players[3]['player']['xpm'] != 0:
                                    if (float(radiant_players[1]['player']['gpm']) - float(
                                            dire_players[1]['player']['gpm']) > 20) and (
                                            float(radiant_players[1]['player']['xpm']) - float(
                                        dire_players[1]['player']['xpm']) > 20):
                                        # мидер сильнее редиант
                                        if (float(radiant_players[0]['player']['gpm']) - float(
                                                dire_players[0]['player']['gpm']) > 20) and (
                                                float(radiant_players[0]['player']['xpm']) - float(
                                            dire_players[0]['player']['xpm']) > 20):
                                            # кор и мидер сильнее. Тима сильнее
                                            team_analyze_winner = radiant_team_name
                                        elif (float(radiant_players[0]['player']['gpm']) - float(
                                                dire_players[0]['player']['gpm']) < 20) and (
                                                float(radiant_players[0]['player']['xpm']) - float(
                                            dire_players[0]['player']['xpm']) < 20):
                                            # мидер сильнее кор слабее
                                            team_analyze_winner = 0
                                        else:
                                            # мидер сильнее коры паритет
                                            if (float(radiant_players[3]['player']['gpm']) - float(
                                                    dire_players[3]['player']['gpm']) < 20) and (
                                                    float(radiant_players[3]['player']['xpm']) - float(
                                                dire_players[3]['player']['xpm']) < 20):
                                                # dire хард слабее
                                                team_analyze_winner = 0
                                            elif (float(radiant_players[3]['player']['gpm']) - float(
                                                    dire_players[3]['player']['gpm']) > 20) and (
                                                    float(radiant_players[3]['player']['xpm']) - float(
                                                dire_players[3]['player']['xpm']) > 20):
                                                # dire хард сильнее
                                                team_analyze_winner = radiant_team_name
                                            else:
                                                team_analyze_winner = radiant_team_name

                                    elif (float(radiant_players[1]['player']['gpm']) - float(
                                            dire_players[1]['player']['gpm']) < 20) and (
                                            float(radiant_players[3]['player']['xpm']) - float(
                                        dire_players[3]['player']['xpm']) < 20):
                                        # мидер сильнее dire
                                        if (float(radiant_players[0]['player']['gpm']) - float(
                                                dire_players[0]['player']['gpm']) > 20) and (
                                                float(radiant_players[0]['player']['xpm']) - float(
                                            dire_players[0]['player']['xpm']) > 20):
                                            # мид даер сильнее кор слабее
                                            team_analyze_winner = 0
                                        elif (float(radiant_players[0]['player']['gpm']) - float(
                                                dire_players[0]['player']['gpm']) < 20) and (
                                                float(radiant_players[0]['player']['xpm']) - float(
                                            dire_players[0]['player']['xpm']) < 20):
                                            # мидер сильнее кор сильнее
                                            team_analyze_winner = dire_team_name
                                        else:
                                            # мидер сильнее коры паритет
                                            if (float(radiant_players[3]['player']['gpm']) - float(
                                                    dire_players[3]['player']['gpm']) < 20) and (
                                                    float(radiant_players[3]['player']['xpm']) - float(
                                                dire_players[3]['player']['xpm']) < 20):
                                                # dire хард сильнее
                                                team_analyze_winner = dire_team_name
                                            elif (float(radiant_players[3]['player']['gpm']) - float(
                                                    dire_players[3]['player']['gpm']) > 20) and (
                                                    float(radiant_players[3]['player']['xpm']) - float(
                                                dire_players[3]['player']['xpm']) > 20):
                                                # dire хард слабее
                                                team_analyze_winner = 0
                                            else:
                                                team_analyze_winner = dire_team_name
                                    else:
                                        # мидеры паритет
                                        team_analyze_winner = 0
                                    if team_analyze_winner == 0:
                                        send_message('Команды равны по статам')
                                    else:
                                        send_message('По результатам сверки команд сильнее оказалась: ' + team_analyze_winner)
                            else:
                                send_message('Сверка невозможна, cyberscore.live тупит :/')
        if redflag:
            print('сплю')
            time.sleep(60)


@bot.message_handler(commands=['button'])
def button_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Анализировать текущие матчи")
    markup.add(item1)


@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text == "Анализировать текущие матчи":
        live_matches()
        bot.send_message(message.chat.id, 'Работа завершена')
        print('Работа завершена')


bot.infinity_polling()