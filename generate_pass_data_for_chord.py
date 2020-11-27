
"""
Chord data needs a co-occurence matrix like:

matrix = [
    [0, 5, 6, 4, 7, 4],
    [5, 0, 5, 4, 6, 5],
    [6, 5, 0, 4, 5, 5],
    [4, 4, 4, 0, 5, 5],
    [7, 6, 5, 5, 0, 4],
    [4, 5, 5, 5, 4, 0],
]

names = ["Julie Ertz", "Yuki Nagasato" etc]

"""

import csv, json
import chord


players = {}
passes = []

passed_by = None
passed_by_team = None
skipped_players = set([])


with open('2019_nwsl_final.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:

        if row['code'].lower() == "start":
            continue

        if row['code'] not in players:
            players[row['code']] = row['team']

        if row['action'] == "Passes accurate":

            passed_by, passed_by_team = row['code'], row['team']

        if passed_by:
            # waiting on next player to get the recipient of pass
            if row['code'] == passed_by:
                continue  # still same player

            if row['code'] != passed_by:

                if row['team'] != passed_by_team:

                    # sometimes there's opposing team members
                    # in between. if there's just one (player, not entry)
                    # we ignore them, if there's more than one, assume
                    # the pass is miscoded and reset

                    skipped_players.add(row['code'])

                    if len(skipped_players) > 1:

                        print("Too many skipped players, giving up")
                        print(skipped_players)
                        passed_by, passed_by_team = None, None
                        skipped_players = set([])
                        continue

                else:

                    passes.append({"source": passed_by, "target": row['code']})

                    passed_by, passed_by_team = None, None
                    skipped_player_count = 0



temp_links = {}

for p in passes:

    if p['source'] < p['target']:
        unique_key = p['source'] + "_" + p['target']
    else:
        unique_key = p['target'] + "_" + p['source']

    temp_links[unique_key] = temp_links.get(unique_key, 0) + 1


name_fixes = {"Bernardo": "Di Bernardo", "Ogimi-Nagasato": "Nagasato"}

def fix_name(name):
    new_name = name.split(" ")[-1]
    if new_name in name_fixes:
        new_name = name_fixes[new_name]
    return new_name


matrix = []
names = []

for player, team in players.items():

    names.append(fix_name(player))

    occurence_row = []

    for second_player, second_team in players.items():

        if player == second_player:
            occurence_row.append(0)
            continue

        if player + "_" + second_player in temp_links:
            occurence_row.append(temp_links[player + "_" + second_player])
            continue

        if second_player + "_" + player in temp_links:
            occurence_row.append(temp_links[second_player + "_" + player])
            continue

        occurence_row.append(0)

    matrix.append(occurence_row)

chord.Chord(matrix, names, width=800, margin=5).to_html()