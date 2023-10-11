import requests, json
from queue import Queue
import time
from threading import Thread
from selenium.webdriver.chrome.options import Options
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
map_id = 7376082994
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
        heroes['hero']['name'] = 'npc_dota_hero_treant_protecter'
    if heroes['isRadiant']:
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

pass


def dotafix(queue):
    start = time.time()
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    print('dotafix')
    radiant = ''.join(['&m=' + str(element) for element in radiant_hero_ids])
    dire = ''.join(['&e=' + str(element) for element in dire_hero_ids])
    dire = '?' + dire[1:]
    url_dotafix = "https://dotafix.github.io/" + dire + radiant
    # send_message(url_dotafix)
    driver.get(url_dotafix)
    element = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, 'rankData')))
    select = Select(element)
    select.select_by_index(9)
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
        queue.put([datan[0]] + [datan[1]] + [datan[2]])
        end = time.time()
        print('dotafix time ' + str(end - start))
    else:
        driver.refresh()
        time.sleep(5)
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
            print('dotafix error')


def protracker(queue):
    start_p = time.time()
    c = 0
    print('protracker')
    lines = {}
    tracker_matchups = {}
    if [] not in matchups.values():
        for name in matchups:
            tracker_matchups[name] = matchups[name].replace(' ', '%20')
    dire_safe_line, mid, radiant_safe_line, radiant_off_line, dire_off_line, radiant_pos1_vs_team, dire_pos1_vs_team, radiant_pos1_vs_cores, dire_pos1_vs_cores, pos1_vs_pos1 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    for position in [tracker_matchups['radiant_pos1'],
                     tracker_matchups['dire_pos1'],
                     tracker_matchups["radiant_pos2"],
                     tracker_matchups["radiant_pos3"],
                     tracker_matchups["dire_pos3"]]:
        url_dota2_protracker = f'https://www.dota2protracker.com/hero/{position}'
        response = requests.get(url_dota2_protracker)
        if response.status_code != 200:
            print(url_dota2_protracker)
            print(position)
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
                against_wr = re.match('[0-9]{1,}\.[0-9]{1,}',
                                      against_wr).group()
                if position == tracker_matchups['radiant_pos1']:
                    if dota2protracker_hero_name == matchups[
                        'dire_pos3'] or dota2protracker_hero_name == \
                            matchups['dire_pos4']:
                        c +=1
                        radiant_safe_line += float(against_wr) / 2
                    elif dota2protracker_hero_name == matchups['dire_pos1']:
                        radiant_pos1_vs_cores += int(float(against_wr))
                        pos1_vs_pos1 = float(against_wr)
                    elif dota2protracker_hero_name in {matchups['dire_pos2'],
                                                       matchups['dire_pos3']}:
                        radiant_pos1_vs_cores += int(float(against_wr))
                    if dota2protracker_hero_name in dire_hero_names:
                        radiant_pos1_vs_team += int(float(against_wr))
                if position == tracker_matchups['dire_pos1']:
                    if dota2protracker_hero_name == matchups[
                        'radiant_pos3'] or dota2protracker_hero_name == \
                            matchups['radiant_pos4']:
                        c +=1
                        dire_safe_line += float(against_wr) / 2
                    if dota2protracker_hero_name in {
                        matchups['radiant_pos1'],
                        matchups['radiant_pos2'],
                        matchups['radiant_pos3']}:
                        dire_pos1_vs_cores += int(float(against_wr))
                    if dota2protracker_hero_name in radiant_hero_names:
                        dire_pos1_vs_team += int(float(against_wr))
                if position == tracker_matchups['radiant_pos2']:
                    if dota2protracker_hero_name == matchups['dire_pos2']:
                        mid += float(against_wr)
                        c+=1
                if position == tracker_matchups['radiant_pos3']:
                    if dota2protracker_hero_name == matchups['dire_pos1'] or \
                            dota2protracker_hero_name == matchups[
                        'dire_pos5']:
                        # if int(float(against_wr)) > 53 or int(float(against_wr)) < 47:
                        radiant_off_line += float(against_wr) / 2
                        c+=1
                if position == tracker_matchups['dire_pos3']:
                    if dota2protracker_hero_name == matchups[
                        'radiant_pos1'] or \
                            dota2protracker_hero_name == matchups[
                        'radiant_pos5']:
                        # if int(float(against_wr)) > 53 or int(float(against_wr)) < 47:
                        dire_off_line += float(against_wr) / 2
                        c+=1
            except Exception as e:
                print(e)
    pos1_vs_team = radiant_pos1_vs_team / 5 - dire_pos1_vs_team / 5
    pos1_vs_cores = radiant_pos1_vs_cores / 3 - dire_pos1_vs_cores / 3
    if mid ==0 or pos1_vs_pos1 ==0 or dire_off_line == 0 or dire_safe_line==0 or radiant_safe_line==0 or radiant_off_line==0 or c!=9:
        print('protracker error')
    if mid != 0 and pos1_vs_pos1 != 0:
        mid -= 50
        pos1_vs_pos1 -= 50
    answer = [pos1_vs_team, pos1_vs_cores, pos1_vs_pos1, mid,
              radiant_off_line - dire_off_line,
              radiant_safe_line - dire_safe_line]
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
result_dict['pos1_vs_team'], result_dict['pos1_vs_cores'], result_dict[
    'pos1_vs_pos1'], result_dict['mid'], result_dict['off_line'], result_dict[
    'safe_line'] = answer[0], answer[1], answer[2], answer[3], answer[4], answer[5]
result_out()
# ids.append(map_id)
# f.seek(0)
# json.dump(ids, f)
end_time = time.time()
print(end_time - start_time)
