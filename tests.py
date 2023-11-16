import requests, json
from queue import Queue
import time
from threading import Thread
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.alert import Alert
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import requests
import telebot
from bs4 import BeautifulSoup
import json

api_key = '81D7C24338E1682DA8CB5131098471D0'
steam_id = '76561198411095988'
good_heroes = {'Phantom Assassin', 'Faceless Void', 'Slark', 'Sven', 'Terrorblade', 'Naga Siren', 'Morphling',
               'Bloodseeker', 'Drow Ranger', 'Troll Warlord', 'Ursa', 'Phantom Lancer', 'Wraith King', 'Spectre',
               'Juggernaut', 'Luna', 'Anti-Mage', 'Muerta', 'Chaos Knight', 'Medusa', 'Lifestealer', 'Gyrocopter'}
hero_n_ids = {1: 'Anti-Mage', 2: 'Axe', 3: 'Bane', 4: 'Bloodseeker', 5: 'Crystal Maiden', 6: 'Drow Ranger', 7: 'Earthshaker', 8: 'Juggernaut', 9: 'Mirana', 10: 'Morphling', 11: 'Shadow Fiend', 12: 'Phantom Lancer', 13: 'Puck', 14: 'Pudge', 15: 'Razor', 16: 'Sand King', 17: 'Storm Spirit', 18: 'Sven', 19: 'Tiny', 20: 'Vengeful Spirit', 21: 'Windranger', 22: 'Zeus', 23: 'Kunkka', 25: 'Lina', 26: 'Lion', 27: 'Shadow Shaman', 28: 'Slardar', 29: 'Tidehunter', 30: 'Witch Doctor', 31: 'Lich', 32: 'Riki', 33: 'Enigma', 34: 'Tinker', 35: 'Sniper', 36: 'Necrophos', 37: 'Warlock', 38: 'Beastmaster', 39: 'Queen of Pain', 40: 'Venomancer', 41: 'Faceless Void', 42: 'Wraith King', 43: 'Death Prophet', 44: 'Phantom Assassin', 45: 'Pugna', 46: 'Templar Assassin', 47: 'Viper', 48: 'Luna', 49: 'Dragon Knight', 50: 'Dazzle', 51: 'Clockwerk', 52: 'Leshrac', 53: "Nature's Prophet", 54: 'Lifestealer', 55: 'Dark Seer', 56: 'Clinkz', 57: 'Omniknight', 58: 'Enchantress', 59: 'Huskar', 60: 'Night Stalker', 61: 'Broodmother', 62: 'Bounty Hunter', 63: 'Weaver', 64: 'Jakiro', 65: 'Batrider', 66: 'Chen', 67: 'Spectre', 68: 'Ancient Apparition', 69: 'Doom', 70: 'Ursa', 71: 'Spirit Breaker', 72: 'Gyrocopter', 73: 'Alchemist', 74: 'Invoker', 75: 'Silencer', 76: 'Outworld Destroyer', 77: 'Lycan', 78: 'Brewmaster', 79: 'Shadow Demon', 80: 'Lone Druid', 81: 'Chaos Knight', 82: 'Meepo', 83: 'Treant Protector', 84: 'Ogre Magi', 85: 'Undying', 86: 'Rubick', 87: 'Disruptor', 88: 'Nyx Assassin', 89: 'Naga Siren', 90: 'Keeper of the Light', 91: 'Io', 92: 'Visage', 93: 'Slark', 94: 'Medusa', 95: 'Troll Warlord', 96: 'Centaur Warrunner', 97: 'Magnus', 98: 'Timbersaw', 99: 'Bristleback', 100: 'Tusk', 101: 'Skywrath Mage', 102: 'Abaddon', 103: 'Elder Titan', 104: 'Legion Commander', 105: 'Techies', 106: 'Ember Spirit', 107: 'Earth Spirit', 108: 'Underlord', 109: 'Terrorblade', 110: 'Phoenix', 111: 'Oracle', 112: 'Winter Wyvern', 113: 'Arc Warden', 114: 'Monkey King', 119: 'Dark Willow', 120: 'Pangolier', 121: 'Grimstroke', 123: 'Hoodwink', 126: 'Void Spirit', 128: 'Snapfire', 129: 'Mars', 135: 'Dawnbreaker', 136: 'Marci', 137: 'Primal Beast', 138: 'Muerta'}
radiant_pick, dire_pick = [], []



# вывод результатов

def get_current_matches(api_key, steam_id):
    flag = True
    game = False
    error = False
    go = False
    while flag:
        url = f'https://api.steampowered.com/IDOTA2Match_570/GetLiveLeagueGames/v1/?key={api_key}&partner=0&format=json'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            matches = data['result']['games']
            for match in matches:
                if 'radiant_team' in match and 'dire_team' in match:# 14914, 14783, 15728, 15904, 15716, 15101, 14915, 15680, 15101, 15820, 15830]
                    game = True
                    if 'scoreboard' in match:
                        if match['scoreboard']['radiant']['players'][0]['hero_id'] != 0 or match['scoreboard']['radiant']['players'][1]['hero_id'] != 0:
                            start_time = time.time()
                            result_dict = {}
                            radiant_hero_ids, dire_hero_ids, dire_hero_names, radiant_hero_names = [], [], [], []
                            matchups = dict()
                            radiant_lanes = dict()
                            dire_lanes = dict()
                            match_id = match['match_id']
                            radiant_team = match['radiant_team']['team_name']
                            radiant_team_id = match['radiant_team']['team_id']

                            dire_team = match['dire_team']['team_name']
                            dire_team_id = match['dire_team']['team_id']
                            print(radiant_team + ' vs ' + dire_team)

                            flag = False
                            def playerPos_steamId():
                                url = f'https://api.opendota.com/api/teams/{radiant_team_id}/matches'
                                radiant_team_data = json.loads(requests.get(url).text)
                                radiant_match_id = radiant_team_data[0]['match_id']
                                radiant_query = '''
                                {
                                    match(id:%s) {
                                        radiantTeam{
                                            name
                                            id
                                            }
                                        direTeam{
                                            name
                                            id
                                            }
                                        players{
                                            position
                                            lane
                                            steamAccountId
                                            isRadiant
                                      }
                                    }
                                }
                                ''' % radiant_match_id
                                url = "https://api.stratz.com/graphql"
                                api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTdWJqZWN0IjoiMWM5MDkyYTgtMGY0OS00OTExLTliMjQtNjM2OWZlNDQ2NzFhIiwiU3RlYW1JZCI6IjQ1MDgzMDI2MCIsIm5iZiI6MTY5NTM2NTcwOCwiZXhwIjoxNzI2OTAxNzA4LCJpYXQiOjE2OTUzNjU3MDgsImlzcyI6Imh0dHBzOi8vYXBpLnN0cmF0ei5jb20ifQ.WfU7Yd8DFBOuOg_MaoisTIhvgElC1E8qGn_OlZa7PYE"
                                headers = {"Authorization": f"Bearer {api_token}"}
                                map = json.loads(requests.post(url, json={"query": radiant_query}, headers=headers).text)
                                if map['data']['match']['radiantTeam']['name'] == radiant_team: flag = True
                                elif map['data']['match']['direTeam']['name'] == radiant_team: flag = False
                                for player in map['data']['match']['players']:
                                    if player['isRadiant'] == flag:
                                        pos = player['position'].split('POSITION_')[1]
                                        radiant_lanes[player['steamAccountId']] = pos
                                ### dire

                                url = f'https://api.opendota.com/api/teams/{dire_team_id}/matches'
                                dire_team_data = json.loads(requests.get(url).text)
                                dire_match_id = dire_team_data[0]['match_id']
                                dire_query = '''
                                {
                                    match(id:%s) {
                                        radiantTeam{
                                            name
                                            id
                                            }
                                        direTeam{
                                            name
                                            id
                                            }
                                        players{
                                            position
                                            lane
                                            steamAccountId
                                            isRadiant
                                      }
                                    }
                                }
                                ''' % dire_match_id
                                url = "https://api.stratz.com/graphql"
                                map_dire = json.loads(requests.post(url, json={"query": dire_query}, headers=headers).text)
                                if map_dire['data']['match']['radiantTeam']['name'] == dire_team:
                                    flag = True
                                elif map_dire['data']['match']['direTeam']['name'] == dire_team:
                                    flag = False
                                for player in map_dire['data']['match']['players']:
                                    if player['isRadiant'] == flag:
                                        pos = player['position'].split('POSITION_')[1]
                                        dire_lanes[player['steamAccountId']] = pos
                                return(dire_lanes, radiant_lanes)
                            try:
                                dire_lanes, radiant_lanes = playerPos_steamId()
                                for player in match['scoreboard']['radiant']['players']:
                                    pos = radiant_lanes[player['account_id']]
                                    hero = hero_n_ids[player['hero_id']]
                                    radiant_hero_ids.append(player['hero_id'])
                                    radiant_hero_names.append(hero)
                                    matchups[f'radiant_pos{pos}'] = hero
                                for player in match['scoreboard']['dire']['players']:
                                    pos = dire_lanes[player['account_id']]
                                    hero = hero_n_ids[player['hero_id']]
                                    dire_hero_ids.append(player['hero_id'])
                                    dire_hero_names.append(hero)
                                    matchups[f'dire_pos{pos}'] = hero


                                def radiant_results():
                                    send_message('Вероятность победы ' + radiant_team)
                                    send_message(result_dict)
                                    send_message(
                                        'Обязательно СВЕРЬ КОМАНДЫ' + '\n' + 'Максимальная ставка 5000 если команды равны +-')
                                    if matchups['radiant_pos1'] not in good_heroes or matchups['dire_pos1'] not in good_heroes:
                                        send_message('BAD HEROES')
                                def result_out():
                                    if [] not in result_dict.values():
                                        if result_dict["dotafix.github"][0] > 50 and \
                                                result_dict["dotafix.github"][
                                                    1] > 50 and result_dict["dotafix.github"][2] > 50 and \
                                                result_dict[
                                                    'pos1_vs_pos1'] > 50 and result_dict['mid'] > 50 and \
                                                result_dict['off_line'] > 0 and result_dict['safe_line'] > 0 and \
                                                matchups['radiant_pos1'] in good_heroes:

                                            radiant_results()
                                            send_message('Победитель ' + radiant_team)

                                        elif result_dict["dotafix.github"][0] < 50 and \
                                                result_dict["dotafix.github"][
                                                    1] < 50 and result_dict["dotafix.github"][2] < 50 and \
                                                result_dict[
                                                    'pos1_vs_pos1'] < 50 and result_dict['mid'] < 50 and \
                                                result_dict['off_line'] < 0 and result_dict['safe_line'] < 0 and \
                                                matchups['dire_pos1'] in good_heroes:
                                            radiant_results()
                                            send_message('Победитель ' + dire_team)
                                        else:
                                            radiant_results()
                                            send_message('Ставка неудачная')

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
                                def protracker(queue):
                                    start_p = time.time()
                                    c = 0
                                    a = 0
                                    b = 0
                                    d = 0
                                    f = 0
                                    print('protracker')
                                    lines = {}
                                    tracker_matchups = {}
                                    if [] not in matchups.values():
                                        for name in matchups:
                                            tracker_matchups[name] = matchups[name].replace(' ', '%20')
                                    dire_safe_line, mid, radiant_safe_line, radiant_off_line, dire_off_line, radiant_pos1_vs_team, dire_pos1_vs_team, pos1_vs_pos1 = 0, 0, 0, 0, 0, 0, 0, 0
                                    for position in [tracker_matchups['radiant_pos1'],
                                                     tracker_matchups['dire_pos1'],
                                                     tracker_matchups["radiant_pos2"],
                                                     tracker_matchups["radiant_pos3"],
                                                     tracker_matchups["dire_pos3"]]:
                                        url_dota2_protracker = f'https://www.dota2protracker.com/hero/{position}/new'
                                        response = requests.get(url_dota2_protracker)
                                        soup = BeautifulSoup(response.text, "lxml")
                                        blocks = soup.find_all('div', class_='overflow-y-scroll tbody h-96')
                                        if position in tracker_matchups['radiant_pos1']:
                                            if blocks[0] != '''<div class="overflow-y-scroll tbody h-96">
                                                                                    </div>''':
                                                div_blocks = blocks[0].find_all('div', {'data-hero': True})  # керри позиция
                                                for data in div_blocks:
                                                    flex = data.find_all('div', class_='flex w-1/4 items-center justify-center')
                                                    tracker_hero_name = flex[0]['data-sort-value']
                                                    wr = float(flex[1]['data-sort-value'])
                                                    pos = flex[3]['data-sort-value']
                                                    if tracker_hero_name == matchups['dire_pos1'] and pos == 'pos 1':
                                                        pos1_vs_pos1 = wr
                                                        radiant_pos1_vs_team += wr
                                                    if tracker_hero_name == matchups['dire_pos2'] and pos == 'pos 2':
                                                        radiant_pos1_vs_team += wr
                                                    if tracker_hero_name == matchups['dire_pos5'] and pos == 'pos 5':
                                                        radiant_pos1_vs_team += wr
                                                    if tracker_hero_name == matchups['dire_pos3'] and pos == 'pos 3':
                                                        radiant_safe_line += wr
                                                    if tracker_hero_name == matchups['dire_pos4'] and pos == 'pos 4':
                                                        radiant_safe_line += wr
                                        if position in tracker_matchups['dire_pos1']:
                                            if blocks[0] != '''<div class="overflow-y-scroll tbody h-96">
                                                                                    </div>''':
                                                div_blocks = blocks[0].find_all('div', {'data-hero': True})  # керри позиция
                                                for data in div_blocks:
                                                    flex = data.find_all('div', class_='flex w-1/4 items-center justify-center')
                                                    tracker_hero_name = flex[0]['data-sort-value']
                                                    wr = float(flex[1]['data-sort-value'])
                                                    pos = flex[3]['data-sort-value']
                                                    if tracker_hero_name == matchups['radiant_pos1'] and pos == 'pos 1':
                                                        dire_pos1_vs_team += wr
                                                    if tracker_hero_name == matchups['radiant_pos2'] and pos == 'pos 2':
                                                        dire_pos1_vs_team += wr
                                                    if tracker_hero_name == matchups['radiant_pos5'] and pos == 'pos 5':
                                                        dire_pos1_vs_team += wr
                                                    if tracker_hero_name == matchups['radiant_pos3'] and pos == 'pos 3':
                                                        dire_safe_line += wr
                                                    if tracker_hero_name == matchups['radiant_pos4'] and pos == 'pos 4':
                                                        dire_safe_line += wr
                                        if position == tracker_matchups['radiant_pos2']:
                                            if blocks[2] != '''<div class="overflow-y-scroll tbody h-96">
                                            </div>''':
                                                div_blocks = blocks[2].find_all('div', {'data-hero': True})
                                                for data in div_blocks:
                                                    flex = data.find_all('div', class_='flex w-1/4 items-center justify-center')
                                                    tracker_hero_name = flex[0]['data-sort-value']
                                                    wr = float(flex[1]['data-sort-value'])
                                                    pos = flex[3]['data-sort-value']
                                                    if tracker_hero_name == matchups['dire_pos2'] and pos == 'pos 2':
                                                        mid += wr
                                        if position == tracker_matchups['radiant_pos3']:
                                            if blocks[4] != '''<div class="overflow-y-scroll tbody h-96">
                                            </div>''':
                                                div_blocks = blocks[4].find_all('div', {'data-hero': True})
                                                for data in div_blocks:
                                                    flex = data.find_all('div', class_='flex w-1/4 items-center justify-center')
                                                    tracker_hero_name = flex[0]['data-sort-value']
                                                    wr = float(flex[1]['data-sort-value'])
                                                    pos = flex[3]['data-sort-value']
                                                    if tracker_hero_name == matchups['dire_pos5'] and pos == 'pos 5':
                                                        radiant_off_line += wr
                                                    if tracker_hero_name == matchups['dire_pos1'] and pos == 'pos 1':
                                                        radiant_off_line += wr
                                        if position == tracker_matchups['dire_pos3']:
                                            if blocks[4] != '''<div class="overflow-y-scroll tbody h-96">
                                                                                    </div>''':
                                                div_blocks = blocks[4].find_all('div', {'data-hero': True})
                                                for data in div_blocks:
                                                    flex = data.find_all('div', class_='flex w-1/4 items-center justify-center')
                                                    tracker_hero_name = flex[0]['data-sort-value']
                                                    wr = float(flex[1]['data-sort-value'])
                                                    pos = flex[3]['data-sort-value']
                                                    if tracker_hero_name == matchups['radiant_pos5'] and pos == 'pos 5':
                                                        dire_off_line += wr
                                                    if tracker_hero_name == matchups['radiant_pos1'] and pos == 'pos 1':
                                                        dire_off_line += wr
                                    pos1_vs_team = radiant_pos1_vs_team / 5 - dire_pos1_vs_team / 5
                                    if mid == 0 or pos1_vs_pos1 == 0 or dire_off_line == 0 or dire_safe_line == 0 or radiant_safe_line == 0 or radiant_off_line == 0:
                                        print('protracker error')
                                        error = True
                                    else:
                                        error = False
                                    pos1_vs_pos1 = pos1_vs_pos1 - 0.5
                                    mid = mid - 0.5
                                    off_line = (radiant_off_line/2)  - (dire_safe_line/2)
                                    safe_line = (radiant_safe_line/2)  - (dire_off_line/2)
                                    answer = [[pos1_vs_team*100, (pos1_vs_pos1*100), (mid+ off_line + safe_line)*100], error]
                                    queue.put(answer)
                                    end_p = time.time()
                                    print('protracker time ' + str(end_p - start_p))

                                def dotafix(queue):
                                    start = time.time()
                                    options = Options()
                                    options.add_argument("--start-maximized")
                                    options.add_argument("--no-sandbox")
                                    driver = webdriver.Edge(options=options)
                                    print('dotafix')
                                    radiant = ''.join(['&m=' + str(element) for element in radiant_hero_ids])
                                    dire = ''.join(['&e=' + str(element) for element in dire_hero_ids])
                                    dire = '?' + dire[1:]
                                    url_dotafix = "https://dotafix.github.io/" + dire + radiant
                                    # send_message(url_dotafix)
                                    driver.get(url_dotafix)
                                    element = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, 'rankData')))
                                    select = Select(element)
                                    select.select_by_index(9)
                                    time.sleep(10)
                                    aler_window = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, '//mat-icon[text()="content_copy"]')))
                                    aler_window.click()
                                    alert = Alert(driver)
                                    alert_text = alert.text
                                    alert.accept()
                                    datan = re.findall(r'\d+(?:\.\d+)?', alert_text)
                                    datan = [float(datan_element) for datan_element in datan]
                                    if len(datan) == 3 and datan[0] != datan[1] and datan[1] != datan[2]:
                                        driver.quit()
                                        queue.put([datan[0]] + [datan[1]] + [datan[2]])
                                        end = time.time()
                                        print('dotafix time ' + str(end - start))
                                    else:
                                        driver.refresh()
                                        time.sleep(10)
                                        aler_window = WebDriverWait(driver, 30).until(
                                            EC.visibility_of_element_located(
                                                (By.XPATH, '//mat-icon[text()="content_copy"]')))
                                        aler_window.click()
                                        alert = Alert(driver)
                                        alert_text = alert.text
                                        alert.accept()
                                        datan = re.findall(r'\d+(?:\.\d+)?', alert_text)
                                        datan = [float(datan_element) for datan_element in datan]
                                        if len(datan) == 3 and datan[0] != datan[1] and datan[1] != datan[2]:
                                            driver.quit()
                                            print('dotafix end')
                                            queue.put([datan[0]] + [datan[1]] + [datan[2]])
                                        else:
                                            send_message('dotafix error')

                                result_queue_1 = Queue()
                                result_queue_2 = Queue()
                                t1 = Thread(target=dotafix, args=(result_queue_1,))
                                t2 = Thread(target=protracker, args=(result_queue_2,))
                                t1.start()
                                t2.start()
                                t1.join()
                                t2.join()
                                result_dict['dotafix.github'] = result_queue_1.get()
                                answer = result_queue_2.get()
                                error = answer[1]
                                result_dict['pos1_vs_team'], result_dict[
                                    'pos1_vs_pos1'], result_dict['lanes'] = answer[0][0], answer[0][1], answer[0][2]
                                print(result_dict)
                                if not error:
                                    send_message(radiant_team)
                                    send_message(result_dict)
                                # result_out()
                                # ids.append(map_id)
                                # f.seek(0)
                                # json.dump(ids, f)
                                end_time = time.time()
                                print(end_time - start_time)
                            except Exception as e:
                                print(e)
                        else:
                            print('draft')
                    else:
                        print('draft')
            if not game:
                print('нет матчей')
                time.sleep(30)


get_current_matches(api_key, steam_id)
