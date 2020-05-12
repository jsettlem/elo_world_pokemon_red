import json
import pickle
import pickletools
import sys
import zlib

import progressbar

from common_methods import save_pickle
from common_types import *

sys.setrecursionlimit(99999999)


def main():
	trainer_dict = {}
	battle_dict = {}

	with open("V:\\Dropbox\\elo-world\\elo_world_pokemon_red_output\\omega2.json", 'r') as f:
		json_battles = json.load(f)

	print("Processing battle jsons")
	for battle in progressbar.progressbar(json_battles):
		battle_id = battle["run_id"]
		turns = battle["turns"]
		trainer_class, trainer_instance = battle["player_class"], battle["player_id"]
		enemy_class, enemy_instance = battle["enemy_class"], battle["enemy_id"]
		winner = battle["winner"]

		trainer = trainer_dict.setdefault(
			(trainer_class, trainer_instance),
			Trainer(trainer_class, trainer_instance,
			        [Pokemon(mon["species"], mon["max_hp"]) for mon in battle["trainer_party_mons"]])
		)

		enemy = trainer_dict.setdefault(
			(enemy_class, enemy_instance),
			Trainer(enemy_class, enemy_instance,
			        [Pokemon(mon["species"], mon["max_hp"]) for mon in battle["enemy_party_mons"]])
		)

		# hotfix for green1:
		if "rival_hotfix" not in battle["source"] and battle["enemy_class"] == 225:
			# don't include the battles where Green didn't have a chance to win
			continue

		battle = battle_dict.setdefault(
			battle_id,
			Battle(battle["source"], trainer, enemy, winner, [
				Turn(
					turn["turn_number"],
					Action(turn["move"], turn["item"], turn["switched"]),
					turn["trainer_battle_mon"],
					turn["enemy_battle_mon"],
					turn["trainer_hp"],
					turn["enemy_hp"]
				) for turn in turns
			])
		)

		for t in (trainer, enemy):
			t.add_battle(battle)

	save_pickle("../omega.pickle", trainer_dict, battle_dict)


if __name__ == '__main__':
	main()
