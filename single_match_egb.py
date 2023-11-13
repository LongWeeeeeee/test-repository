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

# bad_heroes = {'Monkey King':114, "Nature's Prophet":53, 'Lina':25, 'Bristleback':99, 'Necrophos':36, 'Gyrocopter':72, 'Lycan':77, 'Templar Assasin':46, 'Riki':32, 'Meepo':82, }
good_heroes = {'Phantom Assassin', 'Faceless Void', 'Slark', 'Sven', 'Terrorblade', 'Naga Siren', 'Morphling',
               'Bloodseeker', 'Drow Ranger', 'Troll Warlord', 'Ursa', 'Phantom Lancer', 'Wraith King', 'Spectre',
               'Juggernaut', 'Luna', 'Anti-Mage', 'Muerta', 'Chaos Knight', 'Medusa', 'Lifestealer', 'Gyrocopter'}
# Флаг состояния выполнения функции
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
start_time = time.time()
query = '''
{
  live {
    matches(request: { tiers: [PROFESSIONAL, DPC_LEAGUE, DPC_QUALIFIER, DPC_LEAGUE_FINALS, DPC_LEAGUE_QUALIFIER, AMATEUR, UNSET, MINOR, MAJOR, INTERNATIONAL], isCompleted:false, gameStates:[GAME_IN_PROGRESS, INIT, WAIT_FOR_MAP_TO_LOAD, HERO_SELECTION, STRATEGY_TIME, PRE_GAME, DISCONNECT, TEAM_SHOWCASE, CUSTOM_GAME_SETUP, WAIT_FOR_MAP_TO_LOAD, SCENARIO_SETUP, LAST]}) {
      matchId
    }
  }
}
'''
url = "https://api.stratz.com/graphql"
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTdWJqZWN0IjoiMWM5MDkyYTgtMGY0OS00OTExLTliMjQtNjM2OWZlNDQ2NzFhIiwiU3RlYW1JZCI6IjQ1MDgzMDI2MCIsIm5iZiI6MTY5NTM2NTcwOCwiZXhwIjoxNzI2OTAxNzA4LCJpYXQiOjE2OTUzNjU3MDgsImlzcyI6Imh0dHBzOi8vYXBpLnN0cmF0ei5jb20ifQ.WfU7Yd8DFBOuOg_MaoisTIhvgElC1E8qGn_OlZa7PYE"
headers = {"Authorization": f"Bearer {api_token}"}
map_id = 7436541641
match_query = '''
{ 
  live {
    match(id: %s) {
      radiantTeam{
        name
      }
      direTeam{
        name
      }
      players{
        hero{
          name
          id
        }
        position
        isRadiant
      }
    }
  }
}

''' % map_id
matchups = {}
map = requests.post(url, json={"query": match_query}, headers=headers).text
map_json = json.loads(map)['data']['live']['match']
dire_hero_ids, radiant_hero_ids, result_dict, dire_hero_names, radiant_hero_names = [], [], {}, [], []
for heroes in map_json['players']:
    if heroes['hero']['name'] == 'npc_dota_hero_vengefulspirit':
        heroes['hero']['name'] = 'npc_dota_hero_vengeful_spirit'
    elif heroes['hero']['name'] == 'npc_dota_hero_shredder':
        heroes['hero']['name'] = 'npc_dota_hero_timbersaw'
    elif heroes['hero']['name'] == 'npc_dota_hero_wisp':
        heroes['hero']['name'] = 'npc_dota_hero_io'
    elif heroes['hero']['name'] == 'npc_dota_hero_centaur':
        heroes['hero']['name'] = 'npc_dota_hero_centaur_warrunner'
    elif heroes['hero']['name'] == 'npc_dota_hero_furion':
        heroes['hero']['name'] = "npc_dota_hero_nature's_prophet"
    elif heroes['hero']['name'] == 'npc_dota_hero_queenofpain':
        heroes['hero']['name'] = 'npc_dota_hero_queen_of_pain'
    elif heroes['hero']['name'] == 'npc_dota_hero_zuus':
        heroes['hero']['name'] = 'npc_dota_hero_zeus'
    elif heroes['hero']['name'] == 'npc_dota_hero_treant':
        heroes['hero']['name'] = 'npc_dota_hero_treant_protector'
    elif heroes['hero']['name'] == 'npc_dota_hero_necrolyte':
        heroes['hero']['name'] = 'npc_dota_hero_necrophos'
    elif heroes['hero']['name'] == 'npc_dota_hero_life_stealer':
        heroes['hero']['name'] = 'npc_dota_hero_lifestealer'
    elif heroes['hero']['name'] == 'npc_dota_hero_skeleton_king':
        heroes['hero']['name'] = 'npc_dota_hero_wraith_king'
    elif heroes['hero']['name'] == 'npc_dota_hero_windrunner':
        heroes['hero']['name'] = 'npc_dota_hero_windranger'
    elif heroes['hero']['name'] == 'npc_dota_hero_nevermore':
        heroes['hero']['name'] = 'npc_dota_hero_shadow_fiend'
    elif heroes['hero']['name'] == 'npc_dota_hero_rattletrap':
        heroes['hero']['name'] = 'npc_dota_hero_clockwerk'
    elif heroes['hero']['name'] == 'npc_dota_hero_magnataur':
        heroes['hero']['name'] = 'npc_dota_hero_magnus'
    elif heroes['hero']['name'] == 'npc_dota_hero_obsidian_destroyer':
        heroes['hero']['name'] = 'npc_dota_hero_outworld_destroyer'


    if heroes['isRadiant']:
        hero = heroes['hero']['name'].split('npc_dota_hero_')[1].split('_')
        pos = heroes['position'].split('_')[1]
        if len(hero) == 1:
            if hero[0] == 'antimage':
                hero = 'Anti-Mage'
            else:
                hero = hero[0].capitalize()
        elif len(hero) == 2:
            hero = hero[0].capitalize() + ' ' + hero[1].capitalize()
        elif len(hero) == 3:
            hero = hero[0].capitalize() + ' ' + hero[1] + ' ' + hero[2].capitalize()
        elif len(hero) == 4:
            hero = hero[0].capitalize() + ' ' + hero[1] + ' ' + \
                   hero[2] + ' ' + \
                   hero[3].capitalize()
        radiant_hero_names.append(hero)
        matchups[f'radiant_pos{pos}'] = hero
        radiant_hero_ids.append(heroes['hero']['id'])
    elif not heroes['isRadiant']:
        pos = heroes['position'].split('_')[1]
        hero = heroes['hero']['name'].split('npc_dota_hero_')[1].split('_')
        if len(hero) == 1:
            if hero[0] == 'antimage':
                hero = 'Anti-Mage'
            else:
                hero = hero[0].capitalize()
        elif len(hero) == 2:
            hero = hero[0].capitalize() + ' ' + hero[1].capitalize()
        elif len(hero) == 3:
            hero = hero[0].capitalize() + ' ' + hero[1] + ' ' + \
                   hero[2].capitalize()
        elif len(hero) == 4:
            hero = hero[0].capitalize() + ' ' + hero[1] + ' ' + \
                   hero[2] + ' ' + \
                   hero[3].capitalize()
        matchups[f'dire_pos{pos}'] = hero
        dire_hero_names.append(hero)
        dire_hero_ids.append(heroes['hero']['id'])


matchups ={'radiant_pos3': 'Legion Commander', 'radiant_pos4': 'Muerta', 'radiant_pos1': 'Wraith King', 'radiant_pos5': 'Treant Protector', 'radiant_pos2': 'Clinkz', 'dire_pos2': 'Outworld Destroyer', 'dire_pos1': 'Troll Warlord', 'dire_pos4': "Nature's Prophet", 'dire_pos3': 'Beastmaster', 'dire_pos5': 'Shadow Shaman'}

print(matchups)


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
    aler_window = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.XPATH, '//mat-icon[text()="content_copy"]')))
    aler_window.click()
    alert = Alert(driver)
    alert_text = alert.text
    alert.accept()
    datan = re.findall(r'\d+(?:\.\d+)?', alert_text)
    datan = [float(datan_element) for datan_element in datan]
    if len(datan) == 3 and datan[0] != datan[1] or datan[1] != datan[2]:
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


def protracker(queue):
    start_p = time.time()
    off_c = 0
    safe_c = 0

    print('protracker')
    lines = {}
    tracker_matchups = {}
    if [] not in matchups.values():
        for name in matchups:
            tracker_matchups[name] = matchups[name].replace(' ', '%20')
    dire_pos3_vs_pos1, dire_pos3_vs_pos5, dire_pos1_vs_pos3, dire_pos1_vs_pos4, radiant_pos3_vs_pos1, radiant_pos3_vs_pos5, radiant_pos1_vs_pos3, radiant_pos1_vs_pos4 = 0,0,0,0,0,0,0,0
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
                        safe_c += 1
                        radiant_pos1_vs_pos3 = wr
                    if tracker_hero_name == matchups['dire_pos4'] and pos == 'pos 4':
                        radiant_safe_line += wr
                        safe_c += 1
                        radiant_pos1_vs_pos4 = wr
                if radiant_pos1_vs_pos4 == 0:
                    print(position + ' pos 1' + ' VS ' + matchups['dire_pos4'] + ' pos 4 нету на protracker')
                if pos1_vs_pos1 == 0:
                    print(position + ' pos 1' + ' VS ' + matchups['dire_pos1'] + ' pos 1 нету на protracker')
                if radiant_pos1_vs_pos3 == 0:
                    print(position + ' pos 1' + ' VS ' + matchups['dire_pos3'] + ' pos 3 нету на protracker')
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
                        safe_c += 1
                        dire_safe_line += wr
                        dire_pos1_vs_pos3 = wr
                    if tracker_hero_name == matchups['radiant_pos4'] and pos == 'pos 4':
                        dire_safe_line += wr
                        safe_c += 1
                        dire_pos1_vs_pos4 = wr
                if dire_pos1_vs_pos4 == 0:
                    print(position + ' pos 1' + ' VS ' + matchups['radiant_pos4'] + ' pos 4 нету на protracker')
                if dire_pos1_vs_pos3 == 0:
                    print(position + ' pos 1' + ' VS ' + matchups['radiant_pos3'] + ' pos 3 нету на protracker')
        if position == tracker_matchups['radiant_pos2']:
            if blocks[2] != '''<div class="overflow-y-scroll tbody h-96">
                                                </div>''':
                if len(blocks) == 10:
                    div_blocks = blocks[2].find_all('div', {'data-hero': True})
                    for data in div_blocks:
                        flex = data.find_all('div', class_='flex w-1/4 items-center justify-center')
                        tracker_hero_name = flex[0]['data-sort-value']
                        wr = float(flex[1]['data-sort-value'])
                        pos = flex[3]['data-sort-value']
                        if tracker_hero_name == matchups['dire_pos2'] and pos == 'pos 2':
                            mid += wr
                    if mid == 0:
                        print(position + ' pos 2' + ' VS ' + matchups['dire_pos2'] + ' pos 2 нету на protracker')

                else:
                    div_blocks = blocks[0].find_all('div', {'data-hero': True})
                    for data in div_blocks:
                        flex = data.find_all('div', class_='flex w-1/4 items-center justify-center')
                        tracker_hero_name = flex[0]['data-sort-value']
                        wr = float(flex[1]['data-sort-value'])
                        pos = flex[3]['data-sort-value']
                    if mid == 0:
                        print(position + ' pos 2' + ' VS ' + matchups['dire_pos2'] + ' pos 2 нету на protracker')
        if position == tracker_matchups['radiant_pos3']:
            if len(blocks) == 10:
                if blocks[4] != '''<div class="overflow-y-scroll tbody h-96">
                                                    </div>''':
                    div_blocks = blocks[4].find_all('div', {'data-hero': True})
                    for data in div_blocks:
                        flex = data.find_all('div', class_='flex w-1/4 items-center justify-center')
                        tracker_hero_name = flex[0]['data-sort-value']
                        wr = float(flex[1]['data-sort-value'])
                        pos = flex[3]['data-sort-value']
                        if tracker_hero_name == matchups['dire_pos5'] and pos == 'pos 5':
                            off_c += 1
                            radiant_off_line += wr
                            radiant_pos3_vs_pos5 = wr
                        if tracker_hero_name == matchups['dire_pos1'] and pos == 'pos 1':
                            off_c += 1
                            radiant_off_line += wr
                            radiant_pos3_vs_pos1 = wr
                    if radiant_pos3_vs_pos1 == 0:
                        print(position + ' pos 3' + ' VS ' + matchups['dire_pos1'] + ' pos 1 нету на protracker')
                    if radiant_pos3_vs_pos5 == 0:
                        print(position + ' pos 3' + ' VS ' + matchups['dire_pos5'] + ' pos 5 нету на protracker')
            else:
                if blocks[2] != '''<div class="overflow-y-scroll tbody h-96">
                                                    </div>''':
                    div_blocks = blocks[2].find_all('div', {'data-hero': True})
                    for data in div_blocks:
                        flex = data.find_all('div', class_='flex w-1/4 items-center justify-center')
                        tracker_hero_name = flex[0]['data-sort-value']
                        wr = float(flex[1]['data-sort-value'])
                        pos = flex[3]['data-sort-value']
                        if tracker_hero_name == matchups['dire_pos5'] and pos == 'pos 5':
                            off_c += 1
                            radiant_off_line += wr
                            radiant_pos3_vs_pos5 = wr
                        if tracker_hero_name == matchups['dire_pos1'] and pos == 'pos 1':
                            off_c += 1
                            radiant_off_line += wr
                            radiant_pos3_vs_pos1 = wr
                    if radiant_pos3_vs_pos1 == 0:
                        print(position + ' pos 3' + ' VS ' + matchups['dire_pos1'] + ' pos 1 нету на protracker')
                    if radiant_pos3_vs_pos5 == 0:
                        print(position + ' pos 3' + ' VS ' + matchups['dire_pos5'] + ' pos 5 нету на protracker')
        if position == tracker_matchups['dire_pos3']:
            if len(blocks) == 10:
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
                            off_c += 1
                            dire_pos3_vs_pos5 = wr
                        if tracker_hero_name == matchups['radiant_pos1'] and pos == 'pos 1':
                            dire_off_line += wr
                            off_c += 1
                            dire_pos3_vs_pos1 = wr
            else:
                if blocks[2] != '''<div class="overflow-y-scroll tbody h-96">
                                                                                            </div>''':
                    div_blocks = blocks[2].find_all('div', {'data-hero': True})
                    for data in div_blocks:
                        flex = data.find_all('div', class_='flex w-1/4 items-center justify-center')
                        tracker_hero_name = flex[0]['data-sort-value']
                        wr = float(flex[1]['data-sort-value'])
                        pos = flex[3]['data-sort-value']
                        if tracker_hero_name == matchups['radiant_pos5'] and pos == 'pos 5':
                            dire_off_line += wr
                            off_c += 1
                            dire_pos3_vs_pos5 = wr
                        if tracker_hero_name == matchups['radiant_pos1'] and pos == 'pos 1':
                            dire_off_line += wr
                            off_c += 1
                            dire_pos3_vs_pos1 = wr
                    if dire_pos3_vs_pos1 == 0:
                        print(position + ' pos 3' + ' VS '  + matchups['radiant_pos1'] + ' pos 1 нету на protracker')
                    if dire_pos3_vs_pos5 == 0:
                        print(position + ' pos 3' + ' VS '  + matchups['radiant_pos5'] + ' pos 5 нету на protracker')
    pos1_vs_team = radiant_pos1_vs_team / 5 - dire_pos1_vs_team / 5
    if mid == 0 or pos1_vs_pos1 == 0 or dire_off_line == 0 or dire_safe_line == 0 or radiant_safe_line == 0 or radiant_off_line == 0 or safe_c != 4 or off_c != 4:
        print('protracker error')
    if mid != 0:
        mid = mid - 0.5
    if pos1_vs_pos1 !=0:
        pos1_vs_pos1 = pos1_vs_pos1 - 0.5
    off_line = (radiant_off_line / 2) - (dire_safe_line / 2)
    safe_line = (radiant_safe_line / 2) - (dire_off_line / 2)
    answer = [pos1_vs_team * 100, (pos1_vs_pos1 * 100), (mid + off_line + safe_line) * 100, mid, off_line, safe_line]
    queue.put(answer)
    end_p = time.time()
    print('protracker time ' + str(end_p - start_p))


def duration():
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

    for key in final_time:
        if final_time[key] < 0:
            send_message('На ' + str(
                key) + ' минуте radiant слабее на ' + str(
                int(final_time[key]) * -1) + '%')


def radiant_results():
    send_message('Вероятность победы radiant')
    send_message(result_dict)
    send_message(
        'Обязательно СВЕРЬ КОМАНДЫ' + '\n' + 'Максимальная ставка 5000 если команды равны +-')
    if matchups['radiant_pos1'] not in good_heroes or matchups['dire_pos1'] not in good_heroes:
        send_message('BAD HEROES')


# вывод результатов
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
            send_message('Победитель radiant')

        elif result_dict["dotafix.github"][0] < 50 and \
                result_dict["dotafix.github"][
                    1] < 50 and result_dict["dotafix.github"][2] < 50 and \
                result_dict[
                    'pos1_vs_pos1'] < 50 and result_dict['mid'] < 50 and \
                result_dict['off_line'] < 0 and result_dict['safe_line'] < 0 and \
                matchups['dire_pos1'] in good_heroes:
            radiant_results()
            send_message('Победитель dire')
        else:
            radiant_results()
            send_message('Ставка неудачная')


# result_queue_1 = Queue()
result_queue_2 = Queue()
# t1 = Thread(target=dotafix, args=(result_queue_1,))
t2 = Thread(target=protracker, args=(result_queue_2,))
# t1.start()
t2.start()
# t1.join()
t2.join()
# result_dict['dotafix.github'] = result_queue_1.get()
answer = result_queue_2.get()
error = answer[1]
result_dict['pos1_vs_team'], result_dict[
    'pos1_vs_pos1'], result_dict['lanes'], result_dict['mid'], result_dict['off'], result_dict['safe'] = answer[0], answer[1], answer[2], answer[3], answer[4], answer[5]
send_message(result_dict)
print(result_dict)
# ids.append(map_id)
# f.seek(0)
# json.dump(ids, f)
end_time = time.time()
print(end_time - start_time)
