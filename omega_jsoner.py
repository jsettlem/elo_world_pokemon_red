import json
import os

import progressbar


def find_jsons(base_json_dir):
	jsons = [f"{base_json_dir}\\{f}" for f in os.listdir(base_json_dir) if f.endswith(".json")]
	return jsons


def read_battle_json(path):
	with open(path, 'r') as f:
		battle = json.load(f)
	battle["source"] = path
	assert isinstance(battle, object)
	return battle

def main():
	jsons = find_jsons("V:\\Dropbox\\elo-world\\elo_world_pokemon_red_output\\json")
	jsons = jsons + find_jsons("V:\\Dropbox\\elo-world\\elo_world_pokemon_red_output\\json\\no_movie")
	jsons = jsons + find_jsons("V:\\Dropbox\\elo-world\\elo_world_pokemon_red_output\\json\\rival_hotfix")
	print("Reading battle jsons")
	omega_json = [read_battle_json(j) for j in progressbar.progressbar(jsons)]
	with open("omega.json", 'w') as f:
		json.dump(omega_json, f)


if __name__ == '__main__':
	main()
