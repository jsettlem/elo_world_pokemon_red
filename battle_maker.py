from master_controller import *
import progressbar


class Trainer:
	def __init__(self, class_id, instance_id):
		self.class_id = class_id
		self.instance_id = instance_id

	def __eq__(self, o: object) -> bool:
		return isinstance(o, Trainer) and self.class_id == o.class_id and self.instance_id == o.instance_id

	def __hash__(self):
		return hash(self.class_id * 100 + self.instance_id)

	def __str__(self):
		return f"Trainer({self.class_id}, {self.instance_id})"

	def __repr__(self):
		return str(self)


class Matchup:
	def __init__(self, combatant1, combatant2):
		self.combatants = frozenset({combatant1, combatant2})

	def __eq__(self, other):
		return isinstance(other, Matchup) and self.combatants == other.combatants

	def __hash__(self):
		return hash(self.combatants)

	def __str__(self):
		return f"Matchup({', '.join(str(c) for c in self.combatants)})"

	def __repr__(self):
		return str(self)


def read_battle_json(path):
	with open(path, 'r') as f:
		battle_summary = json.load(f)

	return Matchup(Trainer(battle_summary["player_class"], battle_summary["player_id"]),
	               Trainer(battle_summary["enemy_class"], battle_summary["enemy_id"]))


def get_list_of_battles():
	combatants = {Trainer(trainer[0]["id"], trainer[1]["index"]) for trainer in trainer_list}
	battles = {Matchup(t1, t2) for t1 in combatants for t2 in combatants}
	return battles


def get_list_of_battles_that_were_to_be_done():
	with open("battles_to_run3.json", 'r') as f:
		battles_that_were_to_be_run = json.load(f)
	return {Matchup(Trainer(battle[0][0], battle[0][1]),
	                Trainer(battle[-1][0], battle[-1][1])) for battle in battles_that_were_to_be_run}


def make_rival_battles():
	combatants = {Trainer(trainer[0]["id"], trainer[1]["index"]) for trainer in trainer_list}
	rivals = {Trainer(225, i) for i in range(1, 10)}
	battles = {Matchup(t1, t2) for t1 in combatants for t2 in rivals}
	return battles


def find_jsons(base_json_dir):
	jsons = [f"{base_json_dir}\\{f}" for f in os.listdir(base_json_dir) if f.endswith(".json")]
	return jsons


def main():
	# battles = make_rival_battles()
	battles = get_list_of_battles_that_were_to_be_done()
	# battles = get_list_of_battles()
	print(len(battles))
	# jsons = find_jsons("V:\\Dropbox\\elo-world\\elo_world_pokemon_red_output\\json")
	# jsons = jsons + find_jsons("V:\\Dropbox\\elo-world\\elo_world_pokemon_red_output\\json\\no_movie")

	jsons = find_jsons("V:\\Dropbox\\elo-world\\elo_world_pokemon_red_output\\json\\rival_hotfix")
	print(len(jsons))
	json_battles = {read_battle_json(jsons[i]) for i in progressbar.progressbar(range(len(jsons)))}
	print(len(json_battles))
	battles_to_run = battles - json_battles
	# battles_to_run = battles
	print(len(battles_to_run))
	battle_dump = [[[combatant.class_id, combatant.instance_id]
	                for combatant in battle.combatants]
	               for battle in battles_to_run]
	with open("battles_to_run_rival.json", 'w') as f:
		json.dump(battle_dump, f)


if __name__ == '__main__':
	main()
