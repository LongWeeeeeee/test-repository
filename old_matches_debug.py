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

bot = telebot.TeleBot(token='6635829285:AAGhpvRdh-6DtnT6DveZEky0tt5U_PejLXs')



# лайв матчи
def live_matches():
    matches = []
    # result_dict = {'total': 0, 'player_analyze': [], 'ranks': {'radiant':[], 'dire':[]}, 'dotapicker + dota2protracker2': [], 'dotafix.github': {'radiant':[], 'dire':[]}, 'dotatools': {'radiant':[], 'dire':[]}, 'dota2protracker1': {'radiant':[], 'dire':[]}, 'dota2protracker2': {'radiant':[], 'dire':[]}}


    for page in range(500):
        url = f'https://api.cyberscore.live/api/v1/matches/?limit=50&page={page + 1}&past=1'
        response = requests.get(url).text
        json_data = json.loads(response)
        for match in json_data['rows']:
            if match['tournament']['tier'] in {1, 2, 3}:
                for map in match['related_matches']:
                    result_dict = {'winner': '', 'player_analyze': '', 'ranks': '', 'dotafix.github': [],
                                   'dotatools': '', 'dota2protracker1': '', 'dota2protracker2': ''}
                    print(len(matches) + 1)
                    map_id = map['id']
                    dire_hero_names, dire_hero_ids, radiant_hero_names, radiant_hero_ids, dire_team_rangs, radiant_team_rangs = [], [], [], [], [], []
                    match_url = f'https://cyberscore.live/en/matches/{map_id}/'
                    match_data = requests.get(match_url).text
                    soup = BeautifulSoup(match_data, 'lxml')
                    match_soup = soup.find('script', id='__NEXT_DATA__')
                    json_map = json.loads(match_soup.text)['props']['pageProps']['initialState']['matches_item']
                    radiant_pick = json_map['picks_team_radiant']
                    dire_pick = json_map['picks_team_dire']
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
                            with open('new_matches_results_pro.txt', 'r+') as f:
                                redflag = 0
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
                                map_winner = json_map['winner']
                                result_dict['winner'] = map_winner
                                if not ranks_fail:
                                    difference = sum(radiant_team_rangs) - sum(dire_team_rangs)
                                    result_dict['ranks'] = difference
                                options = Options()
                                options.add_argument("--start-maximized")
                                options.add_argument("--no-sandbox")
                                driver = webdriver.Chrome(options=options)
                                # # dotapicker
                                # radiant = ''.join(['/T_' + element.replace(' ', '_') for element in radiant_hero_names])
                                # dire = ''.join(['/E_' + element.replace(' ', '_') for element in dire_hero_names])
                                #
                                # url_dotapicker = "https://dotapicker.com/herocounter#!" + dire + radiant + "/S_0_matchups"
                                # # Download and specify the path to your chromedriver executable
                                # driver.get(url_dotapicker)
                                # try:
                                #     select_element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.NAME, 'component')))
                                # except:
                                #     driver.refresh()
                                #     select_element = WebDriverWait(driver, 15).until(
                                #         EC.element_to_be_clickable((By.NAME, 'component')))
                                # select = Select(select_element)
                                # select.select_by_index(0)
                                # elements = driver.find_elements(By.CSS_SELECTOR, '[align="middle"]')
                                # elements = [int(elements[7].text), int(elements[11].text)]
                                # driver.find_element(By.XPATH,
                                #                     '/html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[3]').click()
                                # elements_winrate = driver.find_elements(By.CSS_SELECTOR, '[align="middle"]')
                                # elements_winrate = [int(elements_winrate[7].text), int(elements_winrate[11].text)]
                                # result_dict['dotapicker'] = elements[0], elements[1], elements_winrate[0], elements_winrate[1]
                                # # ####dotafix.github
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
                                    aler_window = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'content_copy')]")))
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
                                if len(datan) != 3:
                                    print(url_dotafix)
                                else:
                                    datan = [int(float(datan_element)) for datan_element in datan]
                                    if datan[0] == 50 and datan[1] == 50 and datan[2] == 50:
                                        print('увеличить задержку')
                                    else:
                                        result_dict['dotafix.github'] = datan[0], datan[1], datan[2]

                                # dotatools:
                                dire = ''.join([str(element) + ',' for element in dire_hero_ids])
                                radiant = [str(element) + ',' for element in radiant_hero_ids]
                                radiant = ''.join(radiant[:1])
                                url_dotatools = 'https://dotatools.ru/api/v1/predict_victory?dire_hero_ids=' + dire + '&radiant_hero_ids=' + radiant + '&rank=immortal'
                                data = requests.get(url_dotatools)
                                data = json.loads(data.text)
                                result_dict['dotatools'] = data['direWr'], data['radiantWr']
                                # '{"direWr":0.47,"radiantWr":0.53}
                                driver.quit()
                                # dota2protracker
                                total = 0

                                for hero in radiant_hero_names: # 5 циклов
                                    wr_dict_with_radiant[hero] = []
                                    url_dota2_protracker = f'https://www.dota2protracker.com/hero/{hero}'
                                    response = requests.get(url_dota2_protracker)
                                    soup = BeautifulSoup(response.text, "lxml")
                                    hero_names = soup.find_all('td', class_='td-hero-pic')
                                    wr_percentage = soup.find_all('div', class_='perc-wr')
                                    percent_iter = iter(wr_percentage)
                                    hero_names = [dota2protracker_hero_name.get('data-order') for dota2protracker_hero_name in hero_names]
                                    for dota2protracker_hero_name in hero_names: # перебор героев дотапротрекера

                                        try:
                                            with_wr = next(percent_iter).text.strip()
                                            against_wr = next(percent_iter).text.strip()
                                            percentage = re.match('[0-9]{1,}\.[0-9]{1,}', against_wr).group() #процент победы с
                                            percentage_with = re.match('[0-9]{1,}\.[0-9]{1,}', with_wr).group() #процент победы против

                                            #radiant vs dire
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
                                    total += sum(wr_dict[ally])/25
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

                               # Анализ игроков Почему-то radiant почти никогда не побеждает
                               #  dire_players = json_map['team_radiant']['players_items']
                               #  radiant_players = json_map['team_dire']['players_items']
                               #  if radiant_players[1]['player']['gpm'] != 0 and radiant_players[1]['player'][
                               #      'xpm'] and radiant_players[0]['player']['gpm'] != 0 and \
                               #          radiant_players[0]['player']['xpm'] != 0 and \
                               #          radiant_players[3]['player']['gpm'] != 0 and \
                               #          radiant_players[3]['player']['xpm'] != 0 and dire_players[1]['player'][
                               #      'gpm'] != 0 and dire_players[1]['player']['xpm'] and \
                               #          dire_players[0]['player']['gpm'] != 0 and dire_players[0]['player'][
                               #      'xpm'] != 0 and dire_players[3]['player']['gpm'] != 0 and \
                               #          dire_players[3]['player']['xpm'] != 0:
                               #
                               #      if (float(radiant_players[1]['player']['gpm']) - float(
                               #              dire_players[1]['player']['gpm']) > 20) and (
                               #              float(radiant_players[1]['player']['xpm']) - float(
                               #          dire_players[1]['player']['xpm']) > 20):
                               #          # мидер сильнее редиант
                               #          if (float(radiant_players[0]['player']['gpm']) - float(
                               #                  dire_players[0]['player']['gpm']) > 20) and (
                               #                  float(radiant_players[0]['player']['xpm']) - float(
                               #              dire_players[0]['player']['xpm']) > 20):
                               #              # кор и мидер сильнее. Тима сильнее
                               #              team_analyze_winner = radiant_team_name
                               #          elif (float(radiant_players[0]['player']['gpm']) - float(
                               #                  dire_players[0]['player']['gpm']) < 20) and (
                               #                  float(radiant_players[0]['player']['xpm']) - float(
                               #              dire_players[0]['player']['xpm']) < 20):
                               #              # мидер сильнее кор слабее
                               #              team_analyze_winner = 0
                               #          else:
                               #              # мидер сильнее редиант коры паритет
                               #              if (float(radiant_players[3]['player']['gpm']) - float(
                               #                      dire_players[3]['player']['gpm']) < 20) and (
                               #                      float(radiant_players[3]['player']['xpm']) - float(
                               #                  dire_players[3]['player']['xpm']) < 20):
                               #                  # мидер сильнее редиант коры паритет dire хард сильнее
                               #                  team_analyze_winner = 0
                               #              elif (float(radiant_players[3]['player']['gpm']) - float(
                               #                      dire_players[3]['player']['gpm']) > 20) and (
                               #                      float(radiant_players[3]['player']['xpm']) - float(
                               #                  dire_players[3]['player']['xpm']) > 20):
                               #                  # dire хард сильнее
                               #                  team_analyze_winner = radiant_team_name
                               #              else:
                               #                  team_analyze_winner = radiant_team_name
                               #
                               #      elif (float(radiant_players[1]['player']['gpm']) - float(
                               #              dire_players[1]['player']['gpm']) < 20) and (
                               #              float(radiant_players[3]['player']['xpm']) - float(
                               #          dire_players[3]['player']['xpm']) < 20):
                               #          # мидер сильнее dire
                               #          if (float(radiant_players[0]['player']['gpm']) - float(
                               #                  dire_players[0]['player']['gpm']) > 20) and (
                               #                  float(radiant_players[0]['player']['xpm']) - float(
                               #              dire_players[0]['player']['xpm']) > 20):
                               #              # мид даер сильнее кор слабее
                               #              team_analyze_winner = 0
                               #          elif (float(radiant_players[0]['player']['gpm']) - float(
                               #                  dire_players[0]['player']['gpm']) < 20) and (
                               #                  float(radiant_players[0]['player']['xpm']) - float(
                               #              dire_players[0]['player']['xpm']) < 20):
                               #              # мидер сильнее кор сильнее
                               #              team_analyze_winner = dire_team_name
                               #          else:
                               #              # мидер сильнее коры паритет
                               #              if (float(radiant_players[3]['player']['gpm']) - float(
                               #                      dire_players[3]['player']['gpm']) < 20) and (
                               #                      float(radiant_players[3]['player']['xpm']) - float(
                               #                  dire_players[3]['player']['xpm']) < 20):
                               #                  # dire хард сильнее
                               #                  team_analyze_winner = dire_team_name
                               #              elif (float(radiant_players[3]['player']['gpm']) - float(
                               #                      dire_players[3]['player']['gpm']) > 20) and (
                               #                      float(radiant_players[3]['player']['xpm']) - float(
                               #                  dire_players[3]['player']['xpm']) > 20):
                               #                  # dire хард слабее
                               #                  team_analyze_winner = 0
                               #              else:
                               #                  team_analyze_winner = dire_team_name
                               #      else:
                               #          # мидеры паритет
                               #          team_analyze_winner = 0
                               #      if team_analyze_winner == 0:
                               #          pass
                               #      else:
                               #          if team_analyze_winner == radiant_team_name:
                               #              if map_winner == 'radiant':
                               #                  pre = result_dict['player_analyze']
                               #                  pre.append(1)
                               #                  result_dict['player_analyze'] = pre
                               #              elif map_winner == 'dire':
                               #                  pre = result_dict['player_analyze']
                               #                  pre.append(0)
                               #                  result_dict['player_analyze'] = pre
                               #          elif team_analyze_winner == dire_team_name:
                               #              if map_winner == 'radiant':
                               #                  pre = result_dict['player_analyze']
                               #                  pre.append(0)
                               #                  result_dict['player_analyze'] = pre
                               #              elif map_winner == 'dire':
                               #                  pre = result_dict['player_analyze']
                               #                  pre.append(1)
                               #                  result_dict['player_analyze'] = pre
                                matches.append([result_dict])

                                json.dump(matches, f)

live_matches()