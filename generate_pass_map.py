
"""
Final output for an FDG needs to be nodes (players, with group (team)) and
links (pairs of players - source and target - with "value" aka count of links
between them.)

"""

import csv, json


players = {}
passes = []

passed_by = None
passed_by_team = None
skipped_players = set([])


with open('2019_nwsl_final.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:

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

"""
After step one we've got the following:
players = {'10. Vanessa Sue Di Bernardo': 'Chicago Red Stars'}
passes = {'timestamp': X, source': 10. Vanessa Sue Di Bernardo': 'target': 'etc'}
"""

name_fixes = {"Bernardo": "Di Bernardo"}
nodes = []


def fix_name(name):
    new_name = name.split(" ")[-1]
    if new_name in name_fixes:
        new_name = name_fixes[new_name]
    return new_name


for player_name, team in players.items():
    new_name = fix_name(player_name)
    team_id = 1 if team == "Chicago Red Stars" else 2
    nodes.append({"id": new_name, "group": team_id})


temp_links = {}

for p in passes:

    if p['source'] < p['target']:
        unique_key = p['source'] + "_" + p['target']
    else:
        unique_key = p['target'] + "_" + p['source']

    temp_links[unique_key] = temp_links.get(unique_key, 0) + 1



links = []

for key, count in temp_links.items():

    player_a, player_b = key.split("_")

    player_a_name = fix_name(player_a)
    player_b_name = fix_name(player_b)

    a_index = None
    for index, node in enumerate(nodes):
        if node['id'] == player_a_name:
            a_index = index
            break

    b_index = None
    for index, node in enumerate(nodes):
        if node['id'] == player_b_name:
            b_index = index
            break

    links.append({"source": a_index, "target": b_index,
                  "value": count})

    # links.append({"source": player_a_name, "target": player_b_name,
    #               "value": count})



with open('2019_nwsl_final.json', 'w') as outfile:
    json.dump({"nodes": nodes, "links": links}, outfile)