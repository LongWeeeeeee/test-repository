import json
c1 = 0#1077
c2 = 0#10
with open('new_matches_results_pro_copy.json', 'r+') as f:
    json_file = json.load(f)
    for match in json_file[1]:
        if match["dotafix.github"] == '' or match["dotafix.github"] == []:
            c1 += 1

pass
