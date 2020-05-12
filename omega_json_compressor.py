import json

from progressbar import progressbar


def main():
	with open("omega.json", 'r') as f:
		omega_json = json.load(f)

	for battle in progressbar(omega_json):
		base_turn = battle["turns"][0]
		battle["trainer_party_mons"] = base_turn["trainer_party_mons"]
		battle["enemy_party_mons"] = base_turn["enemy_party_mons"]

		for turn in battle["turns"]:
			turn["trainer_battle_mon"] = turn["trainer_battle_mon"]["party_index"]
			turn["enemy_battle_mon"] = turn["enemy_battle_mon"]["party_index"]
			turn["trainer_hp"] = [mon["hp"] for mon in turn["trainer_party_mons"]]
			turn["enemy_hp"] = [mon["hp"] for mon in turn["enemy_party_mons"]]
			del turn["trainer_party_mons"]
			del turn["enemy_party_mons"]

		for mon in battle["trainer_party_mons"] + battle["enemy_party_mons"]:
			del mon["hp"]

	with open("omega2.json", 'w') as f:
		json.dump(omega_json, f)


if __name__ == '__main__':
	main()
