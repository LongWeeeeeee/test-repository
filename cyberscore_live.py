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
    while True:
        url = 'https://api.cyberscore.live/api/v1/matches/?limit=20&liveOrUpcoming=1'
        response = requests.get(url).text
        json_data = json.loads(response)
        for match in json_data['rows']:
            if match['status'] in {'online', 'draft'} and match['tournament']['tier'] in {1,2,3}:
                map_id = match['id']
                with open('map_id_check.txt', 'r+') as f:
                    ids = json.load(f)
                    if map_id not in ids:
                        result_dict = {"winner": [], "player_analyze": [], "ranks": [], "dotafix.github": [], "dotatools": [], "dota2protracker1": [], "dota2protracker2": [], "dotapicker": [], "dota2protracker3": []}
                        best_of = match['best_of']
                        score = match['best_of_score']

                        radiant_team_name = match['team_radiant']['name']
                        dire_team_name = match['team_dire']['name']
                        dire_hero_names, dire_hero_ids, radiant_hero_names, radiant_hero_ids, dire_team_rangs, radiant_team_rangs = [], [], [], [], [], []

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
                            if len(dire_pick) == 5 and len(radiant_pick) == 5 and dire_pick[4]['hero'] != '':
                                redflag = 0
                                for radiant_hero in radiant_pick:
                                    radiant_hero_names.append(radiant_hero['hero']['label'])
                                    radiant_hero_ids.append(radiant_hero['hero']['id_steam'])
                                for dire_hero in dire_pick:
                                    dire_hero_names.append(dire_hero['hero']['label'])
                                    dire_hero_ids.append(dire_hero['hero']['id_steam'])

                                title = json_map['title']
                                radiant_team_name = \
                                json_map['team_radiant']['name']
                                dire_team_name = json_map['team_dire'][
                                    'name']
                                send_message(
                                    title + '\n' + 'Играется бест оф: ' + str(best_of) + '\n' + 'Текущий счет: ' + str(score) + '\n' + 'Вероятность победы ' + radiant_team_name)

                                # Пики закончились
                                if len(dire_hero_names) == 5 and len(radiant_hero_names) == 5:
                                    wr_dict = {}
                                    wr_dict_with_radiant = {}
                                    wr_dict_with_dire = {}

                                    options = Options()
                                    options.add_argument("--start-maximized")
                                    options.add_argument("--no-sandbox")
                                    driver = webdriver.Chrome(options=options)
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
                                        if (datan[0] >= 54 or datan[0] <= 46) and (datan[1] >= 54 or datan[1] <= 46) and (datan[1] >= 54 or datan[0] <= 46):
                                            result_dict['dotafix.github'] = [datan[0]] + [datan[1]] + [datan[2]]
                                    driver.quit()
                                    ids.append(map_id)
                                    f.seek(0)
                                    json.dump(ids, f)
                                    if result_dict["dotapicker"] == [] and result_dict["dotafix.github"] == [] and result_dict["dotatools"] == [] and result_dict["dota2protracker1"] == []:
                                        send_message('Недостаточно материала')
                                    else:
                                        analyze_results(result_dict)
                    else:
                        pass


        print('сплю')
        time.sleep(60)
    is_running = False
    print("Работа завершена")
def analyze_results(result_dict):
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
    with open('new_matches_results_pro_copy.json', 'r') as f:
        json_file = json.load(f)  # 912
        while flag:
            counter += 1
            print(counter)
            for match in json_file[1]:
                if match["winner"] == 'radiant':
                    if result_dict['dotafix.github'] != []:
                        if match["dotafix.github"][0] >= result_dict['dotafix.github'][0] - g and \
                                match["dotafix.github"][0] <= result_dict['dotafix.github'][0] + g \
                                and match["dotafix.github"][1] >= result_dict['dotafix.github'][1] - g and \
                                match["dotafix.github"][1] <= result_dict['dotafix.github'][1] + g \
                                and match["dotafix.github"][2] >= result_dict['dotafix.github'][2] - g and \
                                match["dotafix.github"][2] <= result_dict['dotafix.github'][2] + g:
                                wins_looses['w_g'] += 1
                    if result_dict["dotatools"] != []:
                        if match["dotatools"]['Radiant'] >= result_dict['dotatools']['Radiant'] - t and \
                                match["dotatools"]['Radiant'] <= result_dict['dotatools']['Radiant'] + t:
                            wins_looses['w_t'] += 1
                    if result_dict["dotapicker"] != []:
                        if match["dotapicker"][0] >= result_dict['dotapicker'][0] - p and match["dotapicker"][0] <= \
                                result_dict['dotapicker'][0] + p:
                            wins_looses['w_p'] += 1
                    if result_dict["dota2protracker1"] != []:
                        if match['dota2protracker1'] >= result_dict['dota2protracker1'] - pt and match[
                            'dota2protracker1'] <= result_dict['dota2protracker1'] + pt:
                            wins_looses['w_pt'] += 1
                    # if result_dict["dota2protracker2"] != []:
                    #     if match['dota2protracker2'] >= result_dict['dota2protracker2'] - pt2 and match[
                    #         'dota2protracker2'] <= result_dict['dota2protracker2'] + pt2:
                            wins_looses['w_pt2'] += 1
                elif match['winner'] == 'dire':
                    if result_dict['dotafix.github'] != []:
                        if match["dotafix.github"][0] >= result_dict['dotafix.github'][0] - g and \
                                match["dotafix.github"][0] <= result_dict['dotafix.github'][0] + g \
                                and match["dotafix.github"][1] >= result_dict['dotafix.github'][1] - g and \
                                match["dotafix.github"][1] <= result_dict['dotafix.github'][1] + g \
                                and match["dotafix.github"][2] >= result_dict['dotafix.github'][2] - g and \
                                match["dotafix.github"][2] <= result_dict['dotafix.github'][2] + g:
                            wins_looses['l_g'] += 1
                    if result_dict["dotatools"] != []:
                        if match["dotatools"]['Radiant'] >= result_dict['dotatools']['Radiant'] - t and \
                                match["dotatools"]['Radiant'] <= result_dict['dotatools']['Radiant'] + t:
                            wins_looses['l_t'] += 1
                    if result_dict["dotapicker"] != []:
                        if match["dotapicker"][0] >= result_dict['dotapicker'][0] - p and match["dotapicker"][0] <= \
                                result_dict['dotapicker'][0] + p:
                            wins_looses['l_p'] += 1
                    if result_dict["dota2protracker1"] != []:
                        if match['dota2protracker1'] >= result_dict['dota2protracker1'] - pt and match[
                            'dota2protracker1'] <= result_dict['dota2protracker1'] + pt:
                            wins_looses['l_pt'] += 1
                    # if result_dict["dota2protracker2"] != []:
                    #     if match['dota2protracker2'] >= result_dict['dota2protracker2'] - pt2 and match[
                    #         'dota2protracker2'] <= result_dict['dota2protracker2'] + pt2:
                    #         wins_looses['l_pt2'] += 1
            flag = False
            if (wins_looses['l_g'] == 0 or wins_looses['w_g'] == 0) and result_dict["dotafix.github"] != []:
                g += 1
                flag = True
            if (wins_looses['l_p'] == 0 or wins_looses['w_p'] == 0) and result_dict["dotapicker"] != []:
                p += 1
                flag = True
            if (wins_looses['l_t'] == 0 or wins_looses['w_t'] == 0) and result_dict["dotatools"] != []:
                t += 0.01
                flag = True
            if (wins_looses['l_pt'] == 0 or wins_looses['w_pt'] == 0) and result_dict["dota2protracker1"] != []:
                pt += 0.1
                flag = True
            # if wins_looses['l_pt2'] == 0 or wins_looses['w_pt2'] == 0:
            #     pt2 += 0.1
            #     flag = True
            if flag:
                for key in wins_looses:
                    wins_looses[key] = 0
        global_perc = []
        # if result_dict["dotapicker"] != []:
        #     picker_percents = (wins_looses['w_p'] * 100 / (wins_looses['w_p'] + wins_looses['l_p']))
        #     global_perc.append(picker_percents)
        #     print('Picker WR: ' + str(picker_percents) + '%' + '\n' + str(wins_looses['w_p'] + wins_looses['l_p']))
        if result_dict["dotafix.github"] != []:
            github_percents = (wins_looses['w_g'] * 100 / (wins_looses['w_g'] + wins_looses['l_g']))
            global_perc.append(github_percents)
            print('Github WR: ' + str(github_percents) + '%' + '\n' + str(wins_looses['w_g'] + wins_looses['l_g']))
        # if result_dict["dotatools"] != []:
        #     tools_percents = (wins_looses['w_t'] * 100 / (wins_looses['w_t'] + wins_looses['l_t']))
        #     global_perc.append(tools_percents)
        #     print('Tools WR: ' + str(tools_percents) + '%' + '\n' + str(wins_looses['w_t'] + wins_looses['l_t']))
        # if result_dict["dota2protracker1"] != []:
        #     dota2protracker1_percents = (wins_looses['w_pt'] * 100 / (wins_looses['w_pt'] + wins_looses['l_pt']))
        #     global_perc.append(dota2protracker1_percents)
        #     print('Dota2protracker1 WR: ' + str(dota2protracker1_percents) + '%' + '\n' + str(wins_looses['w_pt'] + wins_looses['l_pt']))
        # dota2protracker2_percents = (wins_looses['w_pt2'] * 100 / (wins_looses['w_pt2'] + wins_looses['l_pt2']))
        # global_perc.append(dota2protracker2_percents)
        # print('Dota2protracker2 WR: ' + str(dota2protracker2_percents) + '%' + '\n' + str(wins_looses['w_pt2'] + wins_looses['l_pt2']))
        # if len(global_perc) >= 2:
        #     total = sum(global_perc) // len(global_perc)
        #     send_message(result_dict)
        #     send_message('Общий шанс на победу: ' + str(total) + '%')
        # elif global_perc != []:
        #     send_message('Недостаточно материала')
        #     total = sum(global_perc) // len(global_perc)
        #     send_message(result_dict)
        #     send_message('Общий шанс на победу: ' + str(total) + '%')
        # else:
        #     send_message('Ставка невозможна')










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