from concurrent.futures.thread import ThreadPoolExecutor
from battle_x_as_y import *


def run(battle):
	run_from_hashid(battle, save_movie=True, auto_level=True, folder="initial_test_run2")


def main(start=0, stop=None):
	THREAD_COUNT = 10

	with open("battle_set_1.txt", 'r') as f:
		battles_to_run = f.readlines()
		battles_to_run = battles_to_run[start:stop if stop is not None else len(battles_to_run)]

	print(battles_to_run)

	with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
		executor.map(run, battles_to_run)


if __name__ == '__main__':
	main(stop=1)
