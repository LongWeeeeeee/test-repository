#https://api.cyberscore.live/api/v1/matches/?limit=50&page=1&past=1
# Структура приложения: Анализ пиков + анализ игроков + анализ команды
#можно также попробовать собирать другую статистику такую как продолжительность матча и все такое
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
import threading


bot = telebot.TeleBot(token='6635829285:AAGhpvRdh-6DtnT6DveZEky0tt5U_PejLXs')



# лайв матчи
def live_matches():
    for page in range(500):
        url = f'https://api.cyberscore.live/api/v1/matches/?limit=50&page={page + 1}&past=1'
        response = requests.get(url).text
        json_data = json.loads(response)
        for match in json_data['rows']:
            if match['tournament']['tier'] in {1, 2, 3}:
                for map in match['related_matches']:
                    map_id = map['id']
                    with open('protrackers_copy.json', 'r+') as f:
                        file = json.load(f)
                        print('Записей в базе: ' + str(len(file[1])))
                        if map_id not in file[0]:
                            matchups = {}
                            result_dict = {'winner': '', 'dotafix.github': []}
                            dire_hero_names,  dire_hero_ids, radiant_hero_names, radiant_hero_ids, dire_team_rangs, radiant_team_rangs = [], [], [], [], [], []
                            match_url = f'https://cyberscore.live/en/matches/{map_id}/'
                            match_data = requests.get(match_url).text
                            soup = BeautifulSoup(match_data, 'lxml')
                            match_soup = soup.find('script', id='__NEXT_DATA__')
                            json_map = json.loads(match_soup.text)['props']['pageProps']['initialState']['matches_item']
                            radiant_pick = json_map['picks_team_radiant']
                            dire_pick = json_map['picks_team_dire']
                            # пики
                            result_dict = {"winner": [], "dotafix.github": [], "protracker_pos1": []}
                            best_of = match['best_of']
                            score = match['best_of_score']
                            matchups = {}
                            dire_hero_names, dire_hero_ids, radiant_hero_names, radiant_hero_ids, dire_team_rangs, radiant_team_rangs = [], [], [], [], [], []

                            match_url = f'https://cyberscore.live/en/matches/{map_id}/'
                            match_data = requests.get(match_url).text
                            soup = BeautifulSoup(match_data, 'lxml')
                            match_soup = soup.find('script', id='__NEXT_DATA__')
                            json_map = json.loads(match_soup.text)['props']['pageProps']['initialState']['matches_item']
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
                                            radiant_player = json_map['team_radiant']['players_items'][q]
                                            if radiant_player['player']["game_name"] == radiant_hero['player'][
                                                "game_name"] and radiant_player['player']['role'] == 1:
                                                matchups['radiant_pos1'] = radiant_hero['hero']['label']
                                            elif radiant_player['player']["game_name"] == radiant_hero['player'][
                                                "game_name"] and radiant_player['player']['role'] == 2:
                                                matchups['radiant_pos2'] = radiant_hero['hero']['label']
                                            elif radiant_player['player']["game_name"] == radiant_hero['player'][
                                                "game_name"] and radiant_player['player']['role'] == 3:
                                                matchups['radiant_pos3'] = radiant_hero['hero']['label']
                                        radiant_hero_names.append(radiant_hero['hero']['label'])
                                        radiant_hero_ids.append(radiant_hero['hero']['id_steam'])
                                    for dire_hero in dire_pick:
                                        for q in range(5):
                                            dire_player = json_map['team_dire']['players_items'][q]
                                            if dire_player['player']["game_name"] == dire_hero['player'][
                                                "game_name"] and \
                                                    dire_player['player']['role'] == 1:
                                                matchups['dire_pos1'] = dire_hero['hero']['label']
                                            elif dire_player['player']["game_name"] == dire_hero['player'][
                                                "game_name"] and \
                                                    dire_player['player']['role'] == 2:
                                                matchups['dire_pos2'] = dire_hero['hero']['label']
                                            elif dire_player['player']["game_name"] == dire_hero['player'][
                                                "game_name"] and \
                                                    dire_player['player']['role'] == 3:
                                                matchups['dire_pos3'] = dire_hero['hero']['label']
                                        dire_hero_names.append(dire_hero['hero']['label'])
                                        dire_hero_ids.append(dire_hero['hero']['id_steam'])
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
                                    time.sleep(5)
                                    try:
                                        element = WebDriverWait(driver, 30).until(
                                            EC.element_to_be_clickable((By.ID, 'rankData')))
                                        select = Select(element)
                                        select.select_by_index(9)
                                        time.sleep(5)
                                        aler_window = WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
                                            (By.XPATH, "//*[contains(text(), 'content_copy')]")))
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
                                            EC.element_to_be_clickable(
                                                (By.XPATH, "//*[contains(text(), 'content_copy')]")))
                                        aler_window.click()
                                        alert = Alert(driver)
                                        alert_text = alert.text
                                        alert.accept()
                                    datan = re.findall(r'\d+(?:\.\d+)?', alert_text)
                                    if len(datan) != 3:
                                        print(url_dotafix)
                                    else:
                                        datan = [float(datan_element) for datan_element in datan]
                                        if (datan[0] >= 54 or datan[0] <= 46) and (
                                                datan[1] >= 54 or datan[1] <= 46) and (
                                                datan[1] >= 54 or datan[0] <= 46):
                                            result_dict['dotafix.github'] = [datan[0]] + [datan[1]] + [datan[2]]
                                    driver.quit()
                                    # protracker
                                    if len(matchups) == 6:
                                        radiant_pos1_vs_team = 0
                                        dire_pos1_vs_team = 0
                                        radiant_pos1_vs_cores = 0
                                        dire_pos1_vs_cores = 0
                                        radiant_1 = matchups['radiant_pos1'].replace(' ', '%20')
                                        radiant_2 = matchups['radiant_pos2'].replace(' ', '%20')
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
                                                if dota2protracker_hero_name in dire_hero_names:
                                                    radiant_pos1_vs_team += int(float(against_wr))
                                                if dota2protracker_hero_name in {matchups['dire_pos1'],
                                                                                 matchups['dire_pos2'],
                                                                                 matchups['dire_pos3']}:
                                                    radiant_pos1_vs_cores += int(float(against_wr))

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
                                    result_dict['pos1_vs_team'] = diff
                                    # pos1 vs cores
                                    diff = radiant_pos1_vs_cores / 3 - dire_pos1_vs_cores / 3
                                    result_dict['pos1_vs_cores'] = diff
                                    #
                                    file[0].append(map_id)
                                    file[1].append(result_dict)
                                    f.seek(0)
                                    json.dump(file, f)
                            # else:
                            #     break

live_matches()