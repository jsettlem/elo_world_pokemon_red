import random
import time
import threading
import requests
from battle_x_as_y import *

# <editor-fold desc="endpoints">
endpoint = "http://localhost:5000"
# </editor-fold>

def run_battle():
	while True:
		hash_id = requests.get(endpoint + "/get_battle").text
		if not hash_id:
			print("We're done here")
			return
		print("got hashid", hash_id)

		battle_log = run_from_hashid(hash_id, save_movie=False, auto_level=True, folder="command_runner")

		print("reporting hashid", hash_id)
		requests.post(endpoint + "/report_battle/" + hash_id,
		              json=battle_log)

def main():
	THREAD_COUNT = 8

	for i in range(THREAD_COUNT):
		a = threading.Thread(target=run_battle, daemon=True)
		a.start()


if __name__ == '__main__':
	main()