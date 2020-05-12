from concurrent.futures.thread import ThreadPoolExecutor

import progressbar

from battle_x_as_y import *

THREAD_COUNT = 10

trainer_list = [(trainer_class, trainer_instance) for trainer_class in trainers for trainer_instance in trainer_class["instances"]]

with open("battles_to_run_rival.json", 'r') as f:
	battles_to_run = json.load(f)


def run(index):
	# your_class, your_instance = random.choice(trainer_list)
	your_class, your_instance = get_trainer_by_id(*battles_to_run[index][0])
	enemy_class, enemy_instance = get_trainer_by_id(*battles_to_run[index][1])

	battle_x_as_y(your_class, your_instance, enemy_class, enemy_instance, run_number=("rival_hotfix/" + str(uuid.uuid4())),
	              save_movie=False)


def main():
	with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
		executor.map(run, range(len(battles_to_run)))


if __name__ == '__main__':
	main()
