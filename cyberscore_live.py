# Структура приложения: Анализ пиков + анализ игроков + анализ команды
#можно также попробовать собирать другую статистику такую как продолжительность матча и все такое
#сверха прошлых матчей и прошлых встреч
#Отладка винрейта на старых матчах
#Проверка того что все правильно работает
#ранги неправильно работают

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
import threading

# Флаг состояния выполнения функции
is_running = False

# Мьютекс для блокировки
lock = threading.Lock()

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
    global is_running
    with lock:
        if is_running:
            print("Функция уже выполняется")
            return
    is_running = True
    # Ваш код выполнения функции
    print("Функция выполняется...")
    redflag = 1

    url = 'https://api.cyberscore.live/api/v1/matches/?limit=20&liveOrUpcoming=1'
    response = requests.get(url).text
    json_data = json.loads(response)
    while redflag:
        for match in json_data['rows']:
            if match['status'] in {'online', 'draft'} and match['tournament']['tier'] in {1,2,3}:
                result_dict = {'winner': '', 'player_analyze': '', 'ranks': '', 'dotafix.github': [],
                               'dotatools': '', 'dota2protracker1': '', 'dota2protracker2': ''}
                best_of = match['best_of']
                score = match['best_of_score']
                radiant_team_name = match['team_radiant']['name']
                dire_team_name = match['team_dire']['name']
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
                            # # Ранги
                            # if not radiant_hero['player']['leaderboard_rank']:
                            #     ranks_fail = True
                            # else:
                            #     radiant_team_rangs.append(radiant_hero['player']['leaderboard_rank'])
                            radiant_hero_names.append(radiant_hero['hero']['label'])
                            radiant_hero_ids.append(radiant_hero['hero']['id_steam'])
                        for dire_hero in dire_pick:
                            # # Ранги
                            # if not dire_hero['player']['leaderboard_rank']:
                            #     ranks_fail = True
                            # else:
                            #    dire_team_rangs.append(dire_hero['player']['leaderboard_rank'])
                            dire_hero_names.append(dire_hero['hero']['label'])
                            dire_hero_ids.append(dire_hero['hero']['id_steam'])

                        title = json_map['title']
                        radiant_team_name = \
                        json_map['team_radiant']['name']
                        dire_team_name = json_map['team_dire'][
                            'name']

                        # if  radiant_team_name in {'Universitario Esports', 'Noping VPN'}:
                        # Пики закончились
                        if len(dire_hero_names) == 5 and len(radiant_hero_names) == 5:
                            redflag = 0
                            # if not ranks_fail:
                            #     difference = sum(radiant_team_rangs) - sum(dire_team_rangs)
                            #     if difference > 0:
                            #         send_message(dire_team_name + ' лучше ранги на ' + str(difference))
                            #     elif difference < 0:
                            #         send_message(radiant_team_name + ' лучше ранги на ' + str(difference*-1))
                            #     else:
                            #         send_message('Ранги неизвестны')

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
                            send_message(title +'\n' + 'Играется бест оф ' + str(best_of) + '\n' + 'Текущий счет: ' + str(score) + '\n' + 'Вероятность победы ' + radiant_team_name)
                            # dotapicker
                            radiant = ''.join(['/T_' + element.replace(' ', '_') for element in radiant_hero_names])
                            dire = ''.join(['/E_' + element.replace(' ', '_') for element in dire_hero_names])

                            url_dotapicker = "https://dotapicker.com/herocounter#!" + dire + radiant + "/S_0_matchups"
                            # Download and specify the path to your chromedriver executable
                            driver.get(url_dotapicker)
                            try:
                                select_element = WebDriverWait(driver, 15).until(
                                    EC.element_to_be_clickable((By.NAME, 'component')))
                            except:
                                driver.refresh()
                                select_element = WebDriverWait(driver, 15).until(
                                    EC.element_to_be_clickable((By.NAME, 'component')))
                            select = Select(select_element)
                            select.select_by_index(0)
                            elements = driver.find_elements(By.CSS_SELECTOR, '[align="middle"]')
                            elements = [int(elements[7].text), int(elements[11].text)]
                            driver.find_element(By.XPATH,
                                                '/html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[3]').click()
                            elements_winrate = driver.find_elements(By.CSS_SELECTOR, '[align="middle"]')
                            elements_winrate = [int(elements_winrate[7].text), int(elements_winrate[11].text)]
                            result_dict['dotapicker'] = elements[0], elements[1], elements_winrate[0], elements_winrate[
                                1]
                            # ####dotafix.github
                            radiant = ''.join(['&m=' + element for element in radiant_hero_ids])
                            dire = ''.join(['&e=' + element for element in dire_hero_ids])
                            dire = '?' + dire[1:]
                            url_dotafix = "https://dotafix.github.io/" + dire + radiant
                            # send_message(url_dotafix)
                            driver.get(url_dotafix)
                            time.sleep(5)
                            try:
                                element = WebDriverWait(driver, 30).until(
                                    EC.element_to_be_clickable((By.ID, 'rankData')))
                                select = Select(element)
                                select.select_by_index(9)
                                time.sleep(5)
                                aler_window = WebDriverWait(driver, 30).until(
                                    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'content_copy')]")))
                                # time.sleep(5)
                                aler_window.click()
                                alert = Alert(driver)
                                alert_text = alert.text
                                alert.accept()
                            except:
                                driver.refresh()
                                element = WebDriverWait(driver, 30).until(
                                    EC.element_to_be_clickable((By.ID, 'rankData')))
                                select = Select(element)
                                select.select_by_index(9)
                                time.sleep(5)
                                aler_window = WebDriverWait(driver, 30).until(
                                    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'content_copy')]")))
                                aler_window.click()
                                alert = Alert(driver)
                                alert_text = alert.text
                                alert.accept()
                            datan = re.findall(r'\d+(?:\.\d+)?', alert_text)
                            datan = [int(float(datan_element)) for datan_element in datan]
                            result_dict['dotafix.github'] = datan[0], datan[1], datan[2]
                            # # dotatools:
                            dire = ''.join([str(element) + ',' for element in dire_hero_ids])
                            radiant = [str(element) + ',' for element in radiant_hero_ids]
                            radiant = ''.join(radiant[:1])
                            url_dotatools = 'https://dotatools.ru/api/v1/predict_victory?dire_hero_ids=' + dire + '&radiant_hero_ids=' + radiant + '&rank=immortal'
                            data = requests.get(url_dotatools)
                            data = json.loads(data.text)
                            result_dict['dotatools'] = data['radiantWr'], data['direWr']
                            # '{"direWr":0.47,"radiantWr":0.53}
                            driver.quit()
                            # dota2protracker
                            total = 0
                            for hero in radiant_hero_names:  # 5 циклов
                                wr_dict_with_radiant[hero] = []
                                url_dota2_protracker = f'https://www.dota2protracker.com/hero/{hero}'
                                response = requests.get(url_dota2_protracker)
                                soup = BeautifulSoup(response.text, "lxml")
                                hero_names = soup.find_all('td', class_='td-hero-pic')
                                wr_percentage = soup.find_all('div', class_='perc-wr')
                                percent_iter = iter(wr_percentage)
                                hero_names = [dota2protracker_hero_name.get('data-order') for dota2protracker_hero_name
                                              in hero_names]
                                for dota2protracker_hero_name in hero_names:  # перебор героев дотапротрекера

                                    try:
                                        with_wr = next(percent_iter).text.strip()
                                        against_wr = next(percent_iter).text.strip()
                                        percentage = re.match('[0-9]{1,}\.[0-9]{1,}',
                                                              against_wr).group()  # процент победы с
                                        percentage_with = re.match('[0-9]{1,}\.[0-9]{1,}',
                                                                   with_wr).group()  # процент победы против

                                        # radiant vs dire
                                        for enemy in dire_hero_names:
                                            if enemy == dota2protracker_hero_name:
                                                wr_dict.setdefault(hero, []).append(float(percentage))
                                        for another_hero in radiant_hero_names:
                                            if another_hero != hero and another_hero == dota2protracker_hero_name:
                                                pre = wr_dict_with_radiant[hero]
                                                pre.append(float(percentage_with))
                                                wr_dict_with_radiant[hero] = pre
                                                pre = 0
                                    except:
                                        pass
                            for enemy in dire_hero_names:
                                wr_dict_with_radiant[enemy] = []
                                url_dota2_protracker = f'https://www.dota2protracker.com/hero/{enemy}'
                                response = requests.get(url_dota2_protracker)
                                soup = BeautifulSoup(response.text, "lxml")
                                hero_names = soup.find_all('td', class_='td-hero-pic')
                                wr_percentage = soup.find_all('div', class_='perc-wr')
                                percent_iter = iter(wr_percentage)
                                hero_names = [dota2protracker_hero_name.get('data-order') for
                                              dota2protracker_hero_name
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
                                    except:
                                        pass
                            # #радиант вс пиков даер
                            for ally in wr_dict:
                                total += sum(wr_dict[ally]) / 25
                            result_dict['dota2protracker1'] = total
                            # #Another dota2protracker
                            total_dire = 0
                            total_radiant = 0
                            for dire in wr_dict_with_dire:
                                total_dire += sum(wr_dict_with_dire[dire]) / 4
                            for radiant in wr_dict_with_radiant:
                                total_radiant += sum(wr_dict_with_radiant[radiant]) / 4
                            diff = total_radiant / 5 - total_dire / 5
                            result_dict['dota2protracker2'] = diff
                            #{'dota2protracker1': 48.476, 'dota2protracker2': -2.9150000000000063, 'dotafix.github': (47, 50, 52), 'dotapicker': (10, 7, -37, -46), 'dotatools': (0.4, 0.6), 'player_analyze': '', 'ranks': '', 'winner': ''}
                            print(result_dict)
                            analyze_results(result_dict)
        if redflag:
                print('сплю')
                time.sleep(30)
    is_running = False
    print("Работа завершена")
def analyze_results(result_dict):
    w_r = 0
    l_r = 0
    w_g = 0
    l_g = 0
    w_p = 0
    l_p = 0
    w_t = 0
    l_t = 0
    w_pt = 0
    l_pt = 0
    w_pt2 = 0
    l_pt2 = 0
    w = 0
    c = 0
    dg = 0
    pt2 = 0
    with open('new_matches_results_pro.txt', 'r') as f:
        json_file = json.load(f)
    while l_g == 0 or w_g ==0 or w_p == 0 or l_p == 0 or w_pt == 0 or l_pt == 0 or w_pt2 == 0 or l_pt2 == 0:
        for q in json_file:
            for match in q:
                if match['winner'] == 'radiant':
                    # send_message(match["dotafix.github"])
                    if match["dotafix.github"] != []:
                        if match["dotafix.github"][0] >= result_dict['dotafix.github'][0] - dg  and match["dotafix.github"][
                            0] <= result_dict['dotafix.github'][0] + dg  and match["dotafix.github"][1] >= \
                                result_dict['dotafix.github'][1] - dg and match["dotafix.github"][1] <= \
                                result_dict['dotafix.github'][1] + dg and match["dotafix.github"][2] >= \
                                result_dict['dotafix.github'][2] - dg and match["dotafix.github"][2] <= \
                                result_dict['dotafix.github'][2] + dg:
                            w_g += 1
                    if match["dotatools"][0] == result_dict['dotatools'][0]:
                        w_t += 1 #винрейт дотатулс с 0.4 победой radiant
                    if match["dotapicker"][0] >= result_dict['dotapicker'][0] - w and match["dotapicker"][0] <= \
                            result_dict['dotapicker'][0] + w:
                        w_p += 1
                    if match['dota2protracker1'] >= result_dict['dota2protracker1'] - c and match['dota2protracker1'] <= result_dict['dota2protracker1']+ c:
                        w_pt += 1
                    if match['dota2protracker2'] >= result_dict['dota2protracker2'] - pt2 and match['dota2protracker2'] <= \
                            result_dict['dota2protracker2'] + pt2:
                        w_pt2 += 1
                elif match['winner'] == 'dire':
                    # send_message(match["dotafix.github"])
                    if match["dotafix.github"] != []:
                        if match["dotafix.github"][0] >= result_dict['dotafix.github'][0] - dg and match["dotafix.github"][
                            0] <= result_dict['dotafix.github'][0] + dg and match["dotafix.github"][1] >= \
                                result_dict['dotafix.github'][1] - dg and match["dotafix.github"][1] <= \
                                result_dict['dotafix.github'][1] + dg and match["dotafix.github"][2] >= \
                                result_dict['dotafix.github'][2] - dg and match["dotafix.github"][2] <= \
                                result_dict['dotafix.github'][2] + dg:
                            l_g += 1
                    if match["dotatools"][0] == result_dict['dotatools'][0]:
                        l_t += 1
                    if match["dotapicker"][0] >= result_dict['dotapicker'][0] - w and match["dotapicker"][0] <= \
                            result_dict['dotapicker'][0] + w:
                        l_p += 1
                    if match['dota2protracker1'] >= result_dict['dota2protracker1'] - c and match['dota2protracker1'] <= \
                            result_dict['dota2protracker1'] + c:
                        l_pt += 1
                    if match['dota2protracker2'] >= result_dict['dota2protracker2'] - pt2 and match['dota2protracker2'] <= result_dict['dota2protracker2'] + pt2:
                        l_pt2 += 1
        if l_g == 0 or w_g == 0 or w_p == 0 or l_p == 0 or l_pt == 0 or w_pt == 0 or l_pt2 == 0 or w_pt2 == 0 :
            l_g, w_g, w_p, l_p, l_t, w_t, w_pt, l_pt, w_pt2, l_pt2 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            if l_g == 0 or w_g == 0:
                dg += 1
            if w_p == 0 or l_p == 0:
                w+= 1
            if w_pt == 0 or l_pt == 0:
                c+= 0.1
            if w_pt2 == 0 or l_pt2 == 0:
                pt2 += 0.1
    global_perc = []
    if w_p != 0 and l_p != 0:
        picker_percents = (w_p * 100 / (w_p + l_p))
        global_perc.append(picker_percents)
        if w_t != 0 and l_t != 0:
            tools_percents = (w_t * 100 / (w_t + l_t))
            global_perc.append(tools_percents)
            if w_pt != 0 and l_pt != 0:
                dota2protracker1_percents = (w_pt * 100 / (w_pt + l_pt))
                global_perc.append(dota2protracker1_percents)
                if w_pt2 != 0 and l_pt2 != 0:
                    dota2protracker2_percents = (w_pt2 * 100 / (w_pt2 + l_pt2))
                    global_perc.append(dota2protracker2_percents)
                    if w_g != 0 and l_g != 0:
                        github_percents = (w_g * 100 / (w_g + l_g))
                        global_perc.append(github_percents)
                        send_message(
                            'Github WR: ' + str(github_percents) + '%' + '\n' + str(w_t + l_t) + '\n' + 'Picker WR: ' + str(picker_percents) + '%' + '\n' + str(w_p + l_p) + '\n' + 'Tools WR: ' + str(
                                tools_percents) + '%' + '\n' + str(w_t + l_t) + '\n' + 'Dota2protracker1 WR: ' + str(
                                dota2protracker1_percents) + '%' + '\n' + str(w_pt + l_pt) + '\n' + 'Dota2protracker2 WR: ' + str(dota2protracker2_percents) + '%' + '\n' + str(w_pt2 + l_pt2) + '\n' + 'Общий шанс на победу: ' + str(sum(global_perc) // len(global_perc)))
                    else:
                        send_message('слишком мало матчей для Dotafix')
                else:
                    send_message('слишком мало матчей для Dota2picker2')
            else:
                send_message('слишком мало матчей для Dota2picker1')
        else:
            send_message('слишком мало матчей для Tools')

    else:
        send_message('слишком мало матчей для dotapicker')







@bot.message_handler(commands=['button'])
def button_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Анализировать текущие матчи")
    markup.add(item1)


@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text == "Анализировать текущие матчи":
        live_matches()
bot.infinity_polling()