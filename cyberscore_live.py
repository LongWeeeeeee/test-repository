# Структура приложения: Анализ пиков + анализ игроков + анализ команды
# можно также попробовать собирать другую статистику такую как продолжительность матча и все такое
# сверха прошлых матчей и прошлых встреч
# Отладка винрейта на старых матчах
# Проверка того что все правильно работает
# ранги неправильно работают
import sys, os
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
# bad_heroes = {'Monkey King':114, "Nature's Prophet":53, 'Lina':25, 'Bristleback':99, 'Necrophos':36, 'Gyrocopter':72, 'Lycan':77, 'Templar Assasin':46, 'Riki':32, 'Meepo':82, }
good_heroes = {'Phantom Assassin', 'Faceless Void', 'Slark', 'Sven', 'Terrorblade', 'Naga Siren', 'Morphling', 'Bloodseeker', 'Drow Ranger', 'Troll Warlord', 'Ursa', 'Phantom Lancer', 'Wraith King', 'Spectre', 'Juggernaut', 'Luna', 'Anti-Mage', 'Muerta', 'Chaos Knight', 'Medusa', 'Lifestealer'}
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
    while True:
        url = 'https://api.cyberscore.live/api/v1/matches/?limit=20&liveOrUpcoming=1'
        response = requests.get(url).text
        json_data = json.loads(response)
        for match in json_data['rows']:
            if match['status'] in {'online', 'draft'} and match['tournament']['tier'] in {1, 2, 3} and 'ESportsBattle' not in match['tournament']['name'] and 'IESF' not in match['tournament']['name']:
            # if match['status'] in {'online', 'draft'} and match['tournament']['tier'] in {1, 2, 3}:
                map_id = match['id']
                # exe_path = os.path.dirname(sys.executable)
                #
                # # Объединяем путь к исполняемому файлу с относительным путем к файлу
                # file_path = os.path.join(exe_path, 'map_id_check.txt')
                #
                # with open(file_path, 'r+') as f:
                with open('map_id_check.txt', 'r+') as f:
                    ids = json.load(f)
                    if map_id not in ids:
                        match_url = f'https://cyberscore.live/en/matches/{map_id}/'
                        match_data = requests.get(match_url).text
                        soup = BeautifulSoup(match_data, 'lxml')
                        match_soup = soup.find('script', id='__NEXT_DATA__')
                        json_map = json.loads(match_soup.text)['props']['pageProps']['initialState']['matches_item']
                        ranks_radiant = {}
                        ranks_dire = {}
                        pos_rank = {}
                        result_dict = {"winner": [], "dotafix.github": [], "protracker_pos1": [],
                                       "pos1_vs_team": [],
                                       "pos1_vs_cores": []}
                        best_of = match['best_of']
                        score = match['best_of_score']
                        matchups = {'dire_pos1': [], 'dire_pos3': [], 'dire_pos2': [], 'radiant_pos1': [],
                                    'radiant_pos2': [], 'radiant_pos3': []}
                        radiant_team_name = match['team_radiant']['name']
                        dire_team_name = match['team_dire']['name']
                        dire_hero_names, dire_hero_ids, radiant_hero_names, radiant_hero_ids, dire_team_rangs, radiant_team_rangs = [], [], [], [], [], []
                        # # ranks
                        # dltv = requests.get('https://dltv.org/matches').text
                        # soup = BeautifulSoup(dltv, 'lxml')
                        # dltv = soup.find_all('div', class_='live__matches-item')
                        # for match_dltv in dltv:
                        #     id = match_dltv.get('data-series-id')
                        #     map = requests.get(f'https://dltv.org/matches/{id}').text
                        #     map_soup = BeautifulSoup(map, 'lxml')
                        #     teams = map_soup.find_all('div', class_='lineups__team')
                        #     for team in teams:
                        #         name_and_rank = team.find('span', class_='lineups__team-title__name')
                        #         name = name_and_rank.contents[1].text
                        #         if name == radiant_team_name:
                        #             ranks = team.find_all('div', class_='rank')
                        #             players = team.find_all('div', class_='player__name-name')
                        #             for q in range(len(players)):
                        #                 ranks_radiant[players[q].text.strip().lower()] = ranks[q].text.strip()
                        #         elif name == dire_team_name:
                        #             ranks = team.find_all('div', class_='rank')
                        #             players = team.find_all('div', class_='player__name-name')
                        #             for q in range(len(players)):
                        #                 ranks_dire[players[q].text.strip().lower()] = ranks[q].text.strip()
                            # могу парсить ранг глобальный
                        radiant_pick = json_map['picks_team_radiant']
                        dire_pick = json_map['picks_team_dire']
                        # map_winner = json_map['winner']
                        # result_dict['winner'] = map_winner
                        # url_map = f'https://cyberscore.live/_next/data/uc8FSlRmVi4jLOPn5R_t6/en/matches/{map_id}.json?id={map_id}'
                        # map_page = requests.get(url_map)
                        # json_map = json.loads(map_page.text)
                        # radiant_pick = json_map['pageProps']['initialState']['matches_item']['picks_team_radiant']
                        # пики
                        if dire_pick != None:
                            if len(dire_pick) == 5 and len(radiant_pick) == 5 and dire_pick[4]['hero'] != '':
                                for radiant_hero in radiant_pick:
                                    for q in range(5):
                                        try:
                                            radiant_player = json_map['team_radiant']['players_items'][q]
                                            if radiant_player['player']["game_name"].lower() == \
                                                    radiant_hero['player'][
                                                        "game_name"].lower() and radiant_player['player'][
                                                'role'] == 1:
                                                matchups['radiant_pos1'] = radiant_hero['hero']['label']
                                                for guy in ranks_radiant:
                                                    if guy == radiant_player['player']["game_name"].lower():
                                                        if ranks_radiant[guy] != '-':
                                                            pos_rank[1] = [ranks_radiant[guy]]

                                            elif radiant_player['player']["game_name"].lower() == \
                                                    radiant_hero['player'][
                                                        "game_name"].lower() and radiant_player['player'][
                                                'role'] == 2:
                                                matchups['radiant_pos2'] = radiant_hero['hero']['label']
                                                for guy in ranks_radiant:
                                                    if guy == radiant_player['player']["game_name"].lower():
                                                        if ranks_radiant[guy] != '-':
                                                            pos_rank[2] = [ranks_radiant[guy]]

                                            elif radiant_player['player']["game_name"].lower() == \
                                                    radiant_hero['player'][
                                                        "game_name"].lower() and radiant_player['player'][
                                                'role'] == 3:
                                                matchups['radiant_pos3'] = radiant_hero['hero']['label']
                                                for guy in ranks_radiant:
                                                    if guy == radiant_player['player']["game_name"].lower():
                                                        if ranks_radiant[guy] != '-':
                                                            pos_rank[3] = [ranks_radiant[guy]]

                                            elif radiant_player['player']["game_name"].lower() == \
                                                    radiant_hero['player'][
                                                        "game_name"].lower() and radiant_player['player'][
                                                'role'] == 4:
                                                for guy in ranks_radiant:
                                                    if guy == radiant_player['player']["game_name"].lower():
                                                        if ranks_radiant[guy] != '-':
                                                            pos_rank[4] = [ranks_radiant[guy]]

                                            elif radiant_player['player']["game_name"].lower() == \
                                                    radiant_hero['player'][
                                                        "game_name"].lower() and radiant_player['player'][
                                                'role'] == 5:
                                                for guy in ranks_radiant:
                                                    if guy == radiant_player['player']["game_name"].lower():
                                                        if ranks_radiant[guy] != '-':
                                                            pos_rank[5] = [ranks_radiant[guy]]


                                        except:
                                            pass

                                    radiant_hero_names.append(radiant_hero['hero']['label'])
                                    radiant_hero_ids.append(radiant_hero['hero']['id_steam'])
                                for dire_hero in dire_pick:
                                    for q in range(5):
                                        try:
                                            dire_player = json_map['team_dire']['players_items'][q]
                                            if dire_player['player']["game_name"].lower() == dire_hero['player'][
                                                "game_name"].lower() and \
                                                    dire_player['player']['role'] == 1:
                                                matchups['dire_pos1'] = dire_hero['hero']['label']
                                                for guy in ranks_dire:
                                                    if guy == dire_player['player']["game_name"].lower():
                                                        if 1 in pos_rank and ranks_radiant[guy] != '-':
                                                            pos_rank[1].append(ranks_dire[guy])
                                            elif dire_player['player']["game_name"].lower() == dire_hero['player'][
                                                "game_name"].lower() and \
                                                    dire_player['player']['role'] == 2:
                                                matchups['dire_pos2'] = dire_hero['hero']['label']
                                                for guy in ranks_dire:
                                                    if guy == dire_player['player']["game_name"].lower():
                                                        if 2 in pos_rank and ranks_radiant[guy] != '-':
                                                            pos_rank[2].append(ranks_dire[guy])
                                            elif dire_player['player']["game_name"].lower() == dire_hero['player'][
                                                "game_name"].lower() and \
                                                    dire_player['player']['role'] == 3:
                                                matchups['dire_pos3'] = dire_hero['hero']['label']
                                                for guy in ranks_dire:
                                                    if guy == dire_player['player']["game_name"].lower():
                                                        if 3 in pos_rank and ranks_radiant[guy] != '-':
                                                            pos_rank[3].append(ranks_dire[guy])
                                            elif dire_player['player']["game_name"].lower() == dire_hero['player'][
                                                "game_name"].lower() and \
                                                    dire_player['player']['role'] == 4:
                                                for guy in ranks_dire:
                                                    if guy == dire_player['player']["game_name"].lower():
                                                        if 4 in pos_rank and ranks_radiant[guy] != '-':
                                                            pos_rank[4].append(ranks_dire[guy])
                                            elif dire_player['player']["game_name"].lower() == dire_hero['player'][
                                                "game_name"].lower() and \
                                                    dire_player['player']['role'] == 5:
                                                for guy in ranks_dire:
                                                    if guy == dire_player['player']["game_name"].lower():
                                                        if 5 in pos_rank and ranks_radiant[guy] != '-':
                                                            pos_rank[5].append(ranks_dire[guy])
                                        except:
                                            pass
                                    dire_hero_names.append(dire_hero['hero']['label'])
                                    dire_hero_ids.append(dire_hero['hero']['id_steam'])
                                radiant_values = 0
                                dire_values = 0
                                # if len(ranks_dire) != 0 and len(ranks_radiant) != 0:
                                #     for values in ranks_dire.values():
                                #         dire_values += int(values)
                                #     for values in ranks_radiant.values():
                                #         radiant_values += int(values)
                                #
                                #     diff = radiant_values - dire_values
                                #     if diff > 0:
                                #         send_message(dire_team_name + ' Ранги лучше. Разнциа составляет: ' + str(
                                #             radiant_values - dire_values))
                                #     elif diff < 0:
                                #         send_message(radiant_team_name + ' Ранги лучше. Разнциа составляет: ' + str(
                                #             radiant_values - dire_values))
                                title = json_map['title']
                                radiant_team_name = \
                                    json_map['team_radiant']['name']
                                dire_team_name = json_map['team_dire'][
                                    'name']
                                map_winner = json_map['winner']
                                result_dict['winner'] = map_winner
                                options = Options()
                                options.add_argument("--start-maximized")
                                options.add_argument("--no-sandbox")
                                driver = webdriver.Chrome(options=options)
                                ####dotafix.github
                                radiant = ''.join(['&m=' + element for element in radiant_hero_ids])
                                dire = ''.join(['&e=' + element for element in dire_hero_ids])
                                dire = '?' + dire[1:]
                                url_dotafix = "https://dotafix.github.io/" + dire + radiant
                                # send_message(url_dotafix)
                                driver.get(url_dotafix)
                                try:
                                    element = WebDriverWait(driver, 30).until(
                                        EC.element_to_be_clickable((By.ID, 'rankData')))
                                    select = Select(element)
                                    select.select_by_index(9)
                                    time.sleep(10)
                                    aler_window = WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
                                        (By.XPATH, '//mat-icon[text()="content_copy"]')))
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
                                    time.sleep(10)
                                    aler_window = WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
                                        (By.XPATH, '//mat-icon[text()="content_copy"]')))
                                    # time.sleep(5)
                                    aler_window.click()
                                    alert = Alert(driver)
                                    alert_text = alert.text
                                    alert.accept()
                                datan = re.findall(r'\d+(?:\.\d+)?', alert_text)
                                if datan[1] == datan[2] and datan[2] == datan[3]:
                                    try:
                                        driver.refresh()
                                        element = WebDriverWait(driver, 30).until(
                                            EC.element_to_be_clickable((By.ID, 'rankData')))
                                        select = Select(element)
                                        select.select_by_index(9)
                                        time.sleep(10)
                                        aler_window = WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
                                            (By.XPATH, '//mat-icon[text()="content_copy"]')))
                                        # time.sleep(5)
                                        aler_window.click()
                                        alert = Alert(driver)
                                        alert_text = alert.text
                                        alert.accept()
                                    except:
                                        element = WebDriverWait(driver, 30).until(
                                            EC.element_to_be_clickable((By.ID, 'rankData')))
                                        select = Select(element)
                                        select.select_by_index(9)
                                        time.sleep(10)
                                        aler_window = WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
                                            (By.XPATH, '//mat-icon[text()="content_copy"]')))
                                        # time.sleep(5)
                                        aler_window.click()
                                        alert = Alert(driver)
                                        alert_text = alert.text
                                        alert.accept()
                                    datan = re.findall(r'\d+(?:\.\d+)?', alert_text)
                                datan = [float(datan_element) for datan_element in datan]
                                # if (datan[0] >= 54 or datan[0] <= 46) and (datan[1] >= 54 or datan[1] <= 46) and (
                                #         datan[1] >= 54 or datan[0] <= 46):
                                result_dict['dotafix.github'] = [datan[0]] + [datan[1]] + [datan[2]]
                                driver.quit()
                                # protracker
                                if matchups['radiant_pos1'] != [] and matchups['dire_pos1'] != [] and matchups['radiant_pos1'] in good_heroes and matchups['dire_pos1'] in good_heroes:
                                    radiant_pos1_vs_team = 0
                                    dire_pos1_vs_team = 0
                                    radiant_pos1_vs_cores = 0
                                    dire_pos1_vs_cores = 0
                                    radiant_1 = matchups['radiant_pos1'].replace(' ', '%20')
                                    url_dota2_protracker = f'https://www.dota2protracker.com/hero/{radiant_1}'
                                    response = requests.get(url_dota2_protracker)
                                    soup = BeautifulSoup(response.text, "lxml")
                                    hero_names = soup.find_all('td', class_='td-hero-pic')
                                    wr_percentage = soup.find_all('div', class_='perc-wr')
                                    hero_names = [dota2protracker_hero_name.get('data-order') for
                                                  dota2protracker_hero_name
                                                  in hero_names]
                                    percent_iter = iter(wr_percentage)
                                    for dota2protracker_hero_name in hero_names:
                                        try:
                                            with_wr = next(percent_iter).text.strip()
                                            against_wr = next(percent_iter).text.strip()
                                            against_wr = re.match('[0-9]{1,}\.[0-9]{1,}', against_wr).group()
                                            if dota2protracker_hero_name == matchups['dire_pos1']:
                                                # if int(float(against_wr)) > 53 or int(float(against_wr)) < 47:
                                                result_dict['protracker_pos1'] = int(float(against_wr))
                                            if [] not in matchups.values():
                                                if dota2protracker_hero_name in dire_hero_names:
                                                    radiant_pos1_vs_team += int(float(against_wr))
                                                if dota2protracker_hero_name in {matchups['dire_pos1'],
                                                                                 matchups['dire_pos2'],
                                                                                 matchups['dire_pos3']}:
                                                    radiant_pos1_vs_cores += int(float(against_wr))

                                        except:
                                            pass
                                    if [] not in [matchups['dire_pos2'], matchups['dire_pos3'],
                                                  matchups['radiant_pos2'], matchups['radiant_pos3']]:
                                        radiant_1 = matchups['radiant_pos1'].replace(' ', '%20')
                                        dire_1 = matchups['dire_pos1'].replace(' ', '%20')
                                        url_dota2_protracker = f'https://www.dota2protracker.com/hero/{dire_1}'
                                        response = requests.get(url_dota2_protracker)
                                        soup = BeautifulSoup(response.text, "lxml")
                                        hero_names = soup.find_all('td', class_='td-hero-pic')
                                        wr_percentage = soup.find_all('div', class_='perc-wr')
                                        hero_names = [dota2protracker_hero_name.get('data-order') for
                                                      dota2protracker_hero_name
                                                      in hero_names]
                                        percent_iter = iter(wr_percentage)
                                        for dota2protracker_hero_name in hero_names:
                                            try:
                                                with_wr = next(percent_iter).text.strip()
                                                against_wr = next(percent_iter).text.strip()
                                                against_wr = re.match('[0-9]{1,}\.[0-9]{1,}', against_wr).group()
                                                if [] not in matchups.values():
                                                    if dota2protracker_hero_name in radiant_hero_names:
                                                        dire_pos1_vs_team += int(float(against_wr))
                                                if dota2protracker_hero_name in {matchups['radiant_pos1'],
                                                                                 matchups['radiant_pos2'],
                                                                                 matchups['radiant_pos3']}:
                                                    dire_pos1_vs_cores += int(float(against_wr))
                                            except:
                                                pass

                                        # pos1 vs team
                                        diff = radiant_pos1_vs_team / 5 - dire_pos1_vs_team / 5
                                        # if diff > 3 or diff < -3:
                                        result_dict['pos1_vs_team'] = diff
                                        # pos1 vs cores
                                        diff = radiant_pos1_vs_cores / 3 - dire_pos1_vs_cores / 3
                                        # if diff > 1 or diff < -1
                                        result_dict['pos1_vs_cores'] = diff
                                        #
                                ids.append(map_id)
                                f.seek(0)
                                json.dump(ids, f)
                                send_message('ТУРНИК ТИР ' + str(match['tournament'][
                                        'tier']) + '\n' + title + '\n' + 'Играется бест оф: ' + str(
                                    best_of) + '\n' + 'Текущий счет: ' + str(
                                    score) + '\n' + 'Вероятность победы ' + radiant_team_name)
                                send_message(result_dict)
                                if result_dict["dotafix.github"] != [] and result_dict['protracker_pos1'] != []:
                                    if result_dict["dotafix.github"][0] > 50 and result_dict["dotafix.github"][
                                        1] > 50 and result_dict["dotafix.github"][2] > 50 and result_dict['protracker_pos1'] >= 50:
                                        send_message('ТУРНИК ТИР ' + str(
                                            match['tournament'][
                                                'tier']) + '\n' + title + '\n' + 'Играется бест оф: ' + str(
                                            best_of) + '\n' + 'Текущий счет: ' + str(
                                            score) + '\n' + 'Вероятность победы ' + radiant_team_name)
                                        analyze_results(result_dict, dire_team_name, radiant_team_name)
                                        send_message('Пик лучше у ' + radiant_team_name)
                                    if result_dict["pos1_vs_cores"] != [] and result_dict['pos1_vs_team'] != []:
                                        if result_dict["dotafix.github"][0] > 54 and result_dict["dotafix.github"][
                                            1] > 54 and \
                                                result_dict["dotafix.github"][2] > 54 \
                                                and result_dict['protracker_pos1'] > 53 and result_dict[
                                            'pos1_vs_team'] > 3 and result_dict['pos1_vs_cores'] > 1:
                                            send_message('ТУРНИК ТИР ' + str(
                                                match['tournament'][
                                                    'tier']) + '\n' + title + '\n' + 'Играется бест оф: ' + str(
                                                best_of) + '\n' + 'Текущий счет: ' + str(
                                                score) + '\n' + 'Вероятность победы ' + radiant_team_name)
                                            analyze_results(result_dict, dire_team_name, radiant_team_name)
                                            send_message('Победитель: ' + radiant_team_name)

                                    if result_dict["dotafix.github"][0] < 50 and result_dict["dotafix.github"][
                                        1] < 50 and \
                                            result_dict["dotafix.github"][2] < 50 and result_dict['protracker_pos1'] <= 50:
                                        send_message('ТУРНИК ТИР ' + str(
                                            match['tournament'][
                                                'tier']) + '\n' + title + '\n' + 'Играется бест оф: ' + str(
                                            best_of) + '\n' + 'Текущий счет: ' + str(
                                            score) + '\n' + 'Вероятность победы ' + radiant_team_name)
                                        analyze_results(result_dict, dire_team_name, radiant_team_name)
                                        send_message('Пик лучше у ' + dire_team_name)
                                    if result_dict["pos1_vs_cores"] != [] and result_dict['pos1_vs_team'] != []:
                                        if result_dict["dotafix.github"][0] < 46 and result_dict["dotafix.github"][
                                            1] < 46 and \
                                                result_dict["dotafix.github"][2] < 46 \
                                                and result_dict['protracker_pos1'] < 47 and result_dict[
                                            'pos1_vs_team'] < -3 and result_dict['pos1_vs_cores'] < -1:
                                            send_message('ТУРНИК ТИР ' + str(
                                                match['tournament'][
                                                    'tier']) + '\n' + title + '\n' + 'Играется бест оф: ' + str(
                                                best_of) + '\n' + 'Текущий счет: ' + str(
                                                score) + '\n' + 'Вероятность победы ' + radiant_team_name)
                                            analyze_results(result_dict, dire_team_name, radiant_team_name)
                                            send_message('Победитель: ' + dire_team_name)
        print('сплю')
        time.sleep(60)
    is_running = False
    print("Работа завершена")


def analyze_results(result_dict, dire_team_name, radiant_team_name):
    g = 0
    p = 0
    t = 0
    c = 0
    pt = 0
    pt2 = 0
    pt3 = 0
    counter = 0
    flag = True
    wins_looses = {"w_g": 0, "l_g": 0, "w_p": 0, "l_p": 0, "w_t": 0, "l_t": 0, "w_pt": 0, "l_pt": 0, "w_pt2": 0,
                   "l_pt2": 0, "w_pt3": 0, "l_pt3": 0}
    counter = 0
    # exe_path = os.path.dirname(sys.executable)
    #
    # # Объединяем путь к исполняемому файлу с относительным путем к файлу
    # file_path = os.path.join(exe_path, 'protrackers.json')
    #
    # with open(file_path, 'r') as f:
    with open('protrackers.json', 'r') as f:
        json_file = json.load(f)  # 912
        while flag:
            counter += 1
            print(counter)
            for match in json_file[1]:
                if match["winner"] == 'radiant':
                    if result_dict['dotafix.github'] != [] and match['dotafix.github'] != []:
                        if match["dotafix.github"][0] >= result_dict['dotafix.github'][0] - g and \
                                match["dotafix.github"][0] <= result_dict['dotafix.github'][0] + g \
                                and match["dotafix.github"][1] >= result_dict['dotafix.github'][1] - g and \
                                match["dotafix.github"][1] <= result_dict['dotafix.github'][1] + g \
                                and match["dotafix.github"][2] >= result_dict['dotafix.github'][2] - g and \
                                match["dotafix.github"][2] <= result_dict['dotafix.github'][2] + g:
                            wins_looses['w_g'] += 1
                    if result_dict['protracker_pos1'] != []:
                        if float(match['protracker_pos1']) >= result_dict['protracker_pos1'] - pt and float(
                                match['protracker_pos1']) <= result_dict['protracker_pos1'] + pt:
                            wins_looses['w_pt'] += 1
                elif match['winner'] == 'dire':
                    if result_dict['dotafix.github'] != [] and match['dotafix.github'] != []:
                        if match["dotafix.github"][0] >= result_dict['dotafix.github'][0] - g and \
                                match["dotafix.github"][0] <= result_dict['dotafix.github'][0] + g \
                                and match["dotafix.github"][1] >= result_dict['dotafix.github'][1] - g and \
                                match["dotafix.github"][1] <= result_dict['dotafix.github'][1] + g \
                                and match["dotafix.github"][2] >= result_dict['dotafix.github'][2] - g and \
                                match["dotafix.github"][2] <= result_dict['dotafix.github'][2] + g:
                            wins_looses['l_g'] += 1
                    if result_dict['protracker_pos1'] != []:
                        if float(match['protracker_pos1']) >= result_dict['protracker_pos1'] - pt and float(
                                match['protracker_pos1']) <= result_dict['protracker_pos1'] + pt:
                            wins_looses['l_pt'] += 1
            flag = False
            if (wins_looses['l_g'] + wins_looses['w_g'] < 20) and result_dict["dotafix.github"] != []:
                g += 1
                flag = True
            if (wins_looses['l_pt'] + wins_looses['w_pt'] < 14) and result_dict["protracker_pos1"] != []:
                pt += 0.1
                flag = True
            if flag:
                for key in wins_looses:
                    wins_looses[key] = 0
        global_perc = []
        if result_dict["dotafix.github"] != []:
            github_percents = (wins_looses['w_g'] * 100 / (wins_looses['w_g'] + wins_looses['l_g']))
            global_perc.append(github_percents)
            print('Github WR: ' + str(github_percents) + '%' + '\n' + str(wins_looses['w_g'] + wins_looses['l_g']))
        if result_dict["protracker_pos1"] != []:
            dota2protracker1_percents = (wins_looses['w_pt'] * 100 / (wins_looses['w_pt'] + wins_looses['l_pt']))
            global_perc.append(dota2protracker1_percents)
            print('Protracker_pos1: ' + str(dota2protracker1_percents) + '%' + '\n' + str(
                wins_looses['w_pt'] + wins_looses['l_pt']))
        total = sum(global_perc) // len(global_perc)
        send_message(result_dict)
        send_message('Общий шанс на победу ' + radiant_team_name + ' ' + str(total) + '%')

live_matches()
# @bot.message_handler(commands=['button'])
# def button_message(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     item1 = types.KeyboardButton("Анализировать текущие матчи")
#     markup.add(item1)
#
#
# @bot.message_handler(content_types='text')
# def message_reply(message):
#     if message.text == "Анализировать текущие матчи":
#         live_matches()
bot.infinity_polling(none_stop=True, timeout=123)