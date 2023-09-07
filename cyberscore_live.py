# Структура приложения: Анализ пиков + анализ игроков + анализ команды
# можно также попробовать собирать другую статистику такую как продолжительность матча и все такое
# сверха прошлых матчей и прошлых встреч
# Отладка винрейта на старых матчах
# Проверка того что все правильно работает
# ранги неправильно работают
#egb live matches
import sys, os
from telebot import types
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert
import re
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import telebot
import requests
from bs4 import BeautifulSoup
import json
import threading
# bad_heroes = {'Monkey King':114, "Nature's Prophet":53, 'Lina':25, 'Bristleback':99, 'Necrophos':36, 'Gyrocopter':72, 'Lycan':77, 'Templar Assasin':46, 'Riki':32, 'Meepo':82, }
good_heroes = {'Phantom Assassin', 'Faceless Void', 'Slark', 'Sven', 'Terrorblade', 'Naga Siren', 'Morphling', 'Bloodseeker', 'Drow Ranger', 'Troll Warlord', 'Ursa', 'Phantom Lancer', 'Wraith King', 'Spectre', 'Juggernaut', 'Luna', 'Anti-Mage', 'Muerta', 'Chaos Knight', 'Medusa', 'Lifestealer', 'Gyrocopter'}
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
        import time
        url = 'https://api.cyberscore.live/api/v1/matches/?limit=20&liveOrUpcoming=1'
        response = requests.get(url).text
        json_data = json.loads(response)
        for match in json_data['rows']:
            if match['tournament']['tier'] in {1, 2, 3} and 'ESportsBattle' not in match['tournament']['name']:
            # if match['tournament']['tier'] in {1, 2, 3, 4} and 'ESportsBattle' not in match['tournament']['name']:
                if match['status'] in {'online', 'draft'}:
                # if match['status'] in {'online', 'draft'} and match['tournament']['tier'] in {1, 2, 3, 4}:
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
                            c = 0
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
                                    for hero in radiant_hero_names:
                                        if hero in good_heroes:
                                            c+=1
                                            matchups['radiant_pos1'] = hero
                                    if c >= 2: send_message('Bad heroes')
                                    c = 0
                                    for hero in dire_hero_names:
                                        if hero in good_heroes:
                                            c+=1
                                            matchups['dire_pos1'] = hero
                                    if c >= 2: send_message('Bad heroes')
                                    # if matchups['dire_pos1'] != [] and matchups['radiant_pos1'] != [] and [] in matchups:

                                    radiant_values = 0
                                    dire_values = 0
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
                                    print('dotafix')
                                    ####dotafix.github
                                    radiant = ''.join(['&m=' + element for element in radiant_hero_ids])
                                    dire = ''.join(['&e=' + element for element in dire_hero_ids])
                                    dire = '?' + dire[1:]
                                    url_dotafix = "https://dotafix.github.io/" + dire + radiant
                                    # send_message(url_dotafix)
                                    driver.get(url_dotafix)
                                    import time
                                    def dotafix():
                                        try:
                                            element = WebDriverWait(driver, 30).until(
                                                EC.element_to_be_clickable((By.ID, 'rankData')))
                                            select = Select(element)
                                            select.select_by_index(9)
                                            import time
                                            time.sleep(10)
                                            aler_window = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(
                                                (By.XPATH, '//mat-icon[text()="content_copy"]')))
                                            # time.sleep(5)
                                            aler_window.click()
                                            alert = Alert(driver)
                                            alert_text = alert.text
                                            alert.accept()
                                            return(alert_text)
                                        except:
                                            send_message('Ошибка dotafix')
                                    try:
                                        alert_text = dotafix()
                                    except:
                                        driver.refresh()
                                        time.sleep(5)
                                        alert_text = dotafix()
                                    datan = re.findall(r'\d+(?:\.\d+)?', alert_text)
                                    if len(datan) == 3:
                                        if datan[0] == datan[1] and datan[1] == datan[2]:
                                            try:
                                                alert_text = dotafix()
                                            except:
                                                driver.refresh()
                                                time.sleep(5)
                                                alert_text = dotafix()
                                        else:
                                            datan = re.findall(r'\d+(?:\.\d+)?', alert_text)
                                            datan = [float(datan_element) for datan_element in datan]
                                            # if (datan[0] >= 54 or datan[0] <= 46) and (datan[1] >= 54 or datan[1] <= 46) and (
                                            #         datan[1] >= 54 or datan[0] <= 46):
                                            result_dict['dotafix.github'] = [datan[0]] + [datan[1]] + [datan[2]]
                                    else:
                                        try:
                                            alert_text = dotafix()
                                            datan = re.findall(r'\d+(?:\.\d+)?', alert_text)
                                            datan = [float(datan_element) for datan_element in datan]
                                            # if (datan[0] >= 54 or datan[0] <= 46) and (datan[1] >= 54 or datan[1] <= 46) and (
                                            #         datan[1] >= 54 or datan[0] <= 46):
                                            result_dict['dotafix.github'] = [datan[0]] + [datan[1]] + [datan[2]]
                                        except:
                                            driver.refresh()
                                            time.sleep(5)
                                            alert_text = dotafix()
                                            datan = re.findall(r'\d+(?:\.\d+)?', alert_text)
                                            datan = [float(datan_element) for datan_element in datan]
                                            # if (datan[0] >= 54 or datan[0] <= 46) and (datan[1] >= 54 or datan[1] <= 46) and (
                                            #         datan[1] >= 54 or datan[0] <= 46):
                                            result_dict['dotafix.github'] = [datan[0]] + [datan[1]] + [datan[2]]
                                    driver.quit()
                                    print('protracker')
                                    # protracker
                                    if matchups['radiant_pos1'] != [] and matchups['dire_pos1'] != []:
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
                                                    result_dict['protracker_pos1'] = float(against_wr)
                                                if [] not in matchups.values():
                                                    if dota2protracker_hero_name in {matchups['dire_pos1'],
                                                                                     matchups['dire_pos2'],
                                                                                     matchups['dire_pos3']}:
                                                        radiant_pos1_vs_cores += int(float(against_wr))
                                                if dota2protracker_hero_name in dire_hero_names:
                                                    radiant_pos1_vs_team += int(float(against_wr))
                                            except:
                                                pass
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
                                                    if dota2protracker_hero_name in {matchups['radiant_pos1'],
                                                                                     matchups['radiant_pos2'],
                                                                                     matchups['radiant_pos3']}:
                                                        dire_pos1_vs_cores += int(float(against_wr))
                                                if dota2protracker_hero_name in radiant_hero_names:
                                                    dire_pos1_vs_team += int(float(against_wr))
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
                                    print('results analyze')
                                    # send_message(result_dict)
                                    if result_dict["dotafix.github"] != [] and result_dict['protracker_pos1'] != []:
                                        if matchups['radiant_pos1'] in good_heroes and matchups['dire_pos1'] in good_heroes:
                                            if (result_dict["dotafix.github"][0] > 50 and result_dict["dotafix.github"][
                                                1] > 50 and result_dict["dotafix.github"][2] > 50 and result_dict[
                                                'protracker_pos1'] > 50) or (result_dict["dotafix.github"][0] < 50 and result_dict["dotafix.github"][
                                                1] < 50 and \
                                                    result_dict["dotafix.github"][2] < 50 and result_dict['protracker_pos1'] < 50):


                                                # duration
                                                game_time_radiant, game_time_dire = {}, {}
                                                for hero_id in radiant_hero_ids:
                                                    radiant_duration = requests.get(
                                                        f'https://api.opendota.com/api/heroes/{hero_id}/durations').text
                                                    radiant_duration_json = json.loads(radiant_duration)
                                                    for moment in radiant_duration_json:
                                                        if int(moment['duration_bin'] / 60) not in game_time_radiant:
                                                            game_time_radiant[int(moment['duration_bin'] / 60)] = [
                                                                moment['wins'] / moment['games_played'] * 100]
                                                        else:
                                                            game_time_radiant[int(moment['duration_bin'] / 60)].append(
                                                                moment['wins'] / moment['games_played'] * 100)
                                                for time in game_time_radiant:
                                                    game_time_radiant[time] = sum(game_time_radiant[time]) / 5
                                                for hero_id in dire_hero_ids:
                                                    dire_duration = requests.get(
                                                        f'https://api.opendota.com/api/heroes/{hero_id}/durations').text
                                                    dire_duration_json = json.loads(dire_duration)
                                                    for moment in dire_duration_json:
                                                        if int(moment['duration_bin'] / 60) not in game_time_dire:
                                                            game_time_dire[int(moment['duration_bin'] / 60)] = [
                                                                moment['wins'] / moment['games_played'] * 100]
                                                        else:
                                                            game_time_dire[int(moment['duration_bin'] / 60)].append(
                                                                moment['wins'] / moment['games_played'] * 100)
                                                for time in game_time_dire:
                                                    game_time_dire[time] = sum(game_time_dire[time]) / 5
                                                final_time = {}
                                                for key in game_time_radiant:
                                                    if key in game_time_dire:
                                                        final_time[key] = game_time_radiant[key] - game_time_dire[key]
                                                final_time = dict(sorted(final_time.items()))



                                            if result_dict["dotafix.github"][0] > 50 and result_dict["dotafix.github"][
                                                1] > 50 and result_dict["dotafix.github"][2] > 50 and result_dict['protracker_pos1'] > 50:

                                                send_message('ТУРНИК ТИР ' + str(
                                                    match['tournament'][
                                                        'tier']) + '\n' + title + '\n' + 'Играется бест оф: ' + str(
                                                    best_of) + '\n' + 'Текущий счет: ' + str(
                                                    score) + '\n' + 'Вероятность победы ' + radiant_team_name)
                                                if match['tournament']['tier'] == 3:
                                                    send_message('Ограничение по ставке 5000р')
                                                # analyze_results(result_dict, dire_team_name, radiant_team_name)
                                                for key in final_time:
                                                    if final_time[key] <= -1:
                                                        send_message('На ' + str(key) + ' минуте ' + radiant_team_name + ' слабее на ' + str(int(final_time[key])*-1) + '%')
                                                # if '-' not in ranks_dire.values() and '-' not in ranks_radiant.values():
                                                #     for values in ranks_dire.values():
                                                #         dire_values += int(values)
                                                #     for values in ranks_radiant.values():
                                                #         radiant_values += int(values)
                                                #
                                                #     diff = radiant_values - dire_values
                                                #     if diff > 0:
                                                #         send_message(
                                                #             dire_team_name + ' Ранги лучше. Разнциа составляет: ' + str(diff))
                                                #     elif diff < 0:
                                                #         send_message(
                                                #             radiant_team_name + ' Ранги лучше. Разнциа составляет: ' + str(
                                                #                 diff * -1))
                                                send_message(result_dict)
                                                send_message('Пик лучше у ' + radiant_team_name)
                                                if result_dict["pos1_vs_cores"] != [] and result_dict['pos1_vs_team'] != []:
                                                    if result_dict["dotafix.github"][0] > 54 and result_dict["dotafix.github"][
                                                        1] > 54 and \
                                                            result_dict["dotafix.github"][2] > 54 \
                                                            and result_dict['protracker_pos1'] > 53 and result_dict[
                                                        'pos1_vs_team'] > 3 and result_dict['pos1_vs_cores'] > 1:
                                                        # analyze_results(result_dict, dire_team_name, radiant_team_name)
                                                        send_message('Победитель: ' + radiant_team_name)
                                            elif result_dict["dotafix.github"][0] < 50 and result_dict["dotafix.github"][
                                                1] < 50 and \
                                                    result_dict["dotafix.github"][2] < 50 and result_dict['protracker_pos1'] < 50:
                                                send_message('ТУРНИК ТИР ' + str(
                                                    match['tournament'][
                                                        'tier']) + '\n' + title + '\n' + 'Играется бест оф: ' + str(
                                                    best_of) + '\n' + 'Текущий счет: ' + str(
                                                    score) + '\n' + 'Вероятность победы ' + radiant_team_name)
                                                if match['tournament']['tier'] == 3:
                                                    send_message('Ограничение по ставке 5000р')
                                                # analyze_results(result_dict, dire_team_name, radiant_team_name)
                                                for key in final_time:
                                                    if final_time[key] >= 1:#сильнее radiant
                                                        send_message('На ' + str(key) + ' минуте ' + dire_team_name + ' слабее на ' + str(int(final_time[key])) + '%')
                                                # if '-' not in ranks_dire.values() and '-' not in ranks_radiant.values():
                                                #     for values in ranks_dire.values():
                                                #         dire_values += int(values)
                                                #     for values in ranks_radiant.values():
                                                #         radiant_values += int(values)
                                                #
                                                #     diff = radiant_values - dire_values
                                                #     if diff > 0:
                                                #         send_message(
                                                #             dire_team_name + ' Ранги лучше. Разнциа составляет: ' + str(diff))
                                                #     elif diff < 0:
                                                #         send_message(
                                                #             radiant_team_name + ' Ранги лучше. Разнциа составляет: ' + str(
                                                #                 diff * -1))
                                                send_message(result_dict)
                                                send_message('Пик лучше у ' + dire_team_name)
                                                if result_dict["pos1_vs_cores"] != [] and result_dict['pos1_vs_team'] != []:
                                                    if result_dict["dotafix.github"][0] < 46 and result_dict["dotafix.github"][
                                                        1] < 46 and \
                                                            result_dict["dotafix.github"][2] < 46 \
                                                            and result_dict['protracker_pos1'] < 47 and result_dict[
                                                        'pos1_vs_team'] < -3 and result_dict['pos1_vs_cores'] < -1:
                                                        # analyze_results(result_dict, dire_team_name, radiant_team_name)
                                                        send_message('Победитель: ' + dire_team_name)
                                            else:
                                                send_message('ТУРНИК ТИР ' + str(match['tournament'][
                                                                                     'tier']) + '\n' + title + '\n' + 'Играется бест оф: ' + str(
                                                    best_of) + '\n' + 'Текущий счет: ' + str(
                                                    score) + '\n' + 'Вероятность победы ' + radiant_team_name)
                                                send_message(result_dict)
                                                send_message('Ставка неудачная')
                                        else:
                                            send_message('ТУРНИК ТИР ' + str(match['tournament'][
                                                                                 'tier']) + '\n' + title + '\n' + 'Играется бест оф: ' + str(
                                                best_of) + '\n' + 'Текущий счет: ' + str(
                                                score) + '\n' + 'Вероятность победы ' + radiant_team_name)
                                            send_message(result_dict)
                                            send_message(matchups)
                                            send_message('Bad heroes')
                                    else:
                                        send_message('ТУРНИК ТИР ' + str(match['tournament'][
                                            'tier']) + '\n' + title + '\n' + 'Играется бест оф: ' + str(
                                        best_of) + '\n' + 'Текущий счет: ' + str(
                                        score) + '\n' + 'Вероятность победы ' + radiant_team_name)
                                        send_message(result_dict)
                                        send_message('Ставка неудачная')
                elif match['status'] == 'pause':
                    print('pause sleep')
                    time.sleep(60)
                elif match['status'] == 'waiting':
                    time_str = match['date_start']
                    datetime_obj = datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                    current_date = datetime.datetime.now()
                    time_difference = datetime_obj - current_date
                    seconds = time_difference.total_seconds()
                    if seconds > 0:
                        print('waiting sleep')
                        time.sleep(seconds)
                    else:
                        print('waiting sleep')
                        time.sleep(120)
        print('draft sleep')
        time.sleep(30)


    is_running = False
    print("Работа завершена")
live_matches()
