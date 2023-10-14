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
    matches(request: {isCompleted:false, tiers:[PROFESSIONAL, INTERNATIONAL, DPC_LEAGUE, DPC_QUALIFIER, DPC_LEAGUE_FINALS, DPC_LEAGUE_QUALIFIER, UNSET, AMATEUR, MINOR, MAJOR]}) {
      matchId
    }
  }
}
'''
url = "https://api.stratz.com/graphql"
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTdWJqZWN0IjoiMWM5MDkyYTgtMGY0OS00OTExLTliMjQtNjM2OWZlNDQ2NzFhIiwiU3RlYW1JZCI6IjQ1MDgzMDI2MCIsIm5iZiI6MTY5NTM2NTcwOCwiZXhwIjoxNzI2OTAxNzA4LCJpYXQiOjE2OTUzNjU3MDgsImlzcyI6Imh0dHBzOi8vYXBpLnN0cmF0ei5jb20ifQ.WfU7Yd8DFBOuOg_MaoisTIhvgElC1E8qGn_OlZa7PYE"
headers = {"Authorization": f"Bearer {api_token}"}
matches = requests.post(url, json={"query": query}, headers=headers).text
for map_id in json.loads(matches)['data']['live']['matches']:
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
    
    ''' % map_id['matchId']
    matchups = {}
    map = requests.post(url, json={"query": match_query}, headers=headers).text
    map_json = json.loads(map)['data']['live']['match']
    dire_team = map_json['direTeam']['name']
    radiant_team = map_json['radiantTeam']['name']
    send_message(radiant_team + ' VS ' + dire_team)
    dire_hero_ids, radiant_hero_ids, result_dict, dire_hero_names, radiant_hero_names = [], [], {}, [], []
    heroes_dict = {'vengefulspirit': 'vengeful_spirit', 'shredder':'timbersaw', 'wisp':'io', 'centaur': 'centaur_warrunner', 'furion': "nature's_prophet", 'queenofpain': 'queen_of_pain', 'zuus':'zeus', 'treant':'treant_protector', 'necrolyte':'necrophos', 'life_stealer':'lifestealer', 'skeleton_king':'wraith_king'}
    for heroes in map_json['players']:
        heroes['hero']['name'] = heroes['hero']['name'].split('npc_dota_hero_')[1]
        if heroes['hero']['name'] in heroes_dict:
            heroes['hero']['name'] = heroes_dict[heroes['hero']['name']]
        hero = heroes['hero']['name'].split('_')
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
        if heroes['isRadiant']:
            radiant_hero_names.append(hero)
            matchups[f'radiant_pos{pos}'] = hero
            radiant_hero_ids.append(heroes['hero']['id'])
        elif not heroes['isRadiant']:
            matchups[f'dire_pos{pos}'] = hero
            dire_hero_names.append(hero)
            dire_hero_ids.append(heroes['hero']['id'])
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
                            a +=1
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
                            b +=1
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
                            d+=1
                    if position == tracker_matchups['dire_pos3']:
                        if dota2protracker_hero_name == matchups['radiant_pos1'] or \
                                dota2protracker_hero_name == matchups['radiant_pos5']:
                            # if int(float(against_wr)) > 53 or int(float(against_wr)) < 47:
                            dire_off_line += float(against_wr) / 2
                            f+=1
                except Exception as e:
                    print(e)
        pos1_vs_team = radiant_pos1_vs_team / 5 - dire_pos1_vs_team / 5
        pos1_vs_cores = radiant_pos1_vs_cores / 3 - dire_pos1_vs_cores / 3
        if mid ==0 or pos1_vs_pos1 ==0 or dire_off_line == 0 or dire_safe_line==0 or radiant_safe_line==0 or radiant_off_line==0:
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
        send_message('Вероятность победы ' + radiant_team)
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
