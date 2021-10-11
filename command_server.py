import json
import sys

from flask import Flask, request
import os
import atexit

OUTPUT_BASE = "W:/elo_world_output/red_redux_command/json"
legal_alphabet = set("abcdefghijkmnopqrstuvwxyz1234567890-! ")


def main():
	pending_battles = []
	claimed_battles = []

	if not os.path.exists("battles_to_run.txt"):
		print("loading from battle set")
		with open("battle_set_1.txt", 'r') as f1:
			with open("battles_to_run.txt", 'w') as f2:
				f2.write(f1.read())
	with open("battles_to_run.txt", 'r') as f:
		for line in f:
			pending_battles.append(line.strip())

	app = Flask(__name__)

	@app.route("/get_battle")
	def get_battle():
		try:
			hash_id = pending_battles.pop()
			claimed_battles.append(hash_id)

			print(f"providing hash id {hash_id} for ip {request.remote_addr}")
			return hash_id
		except IndexError:
			return None

	@app.route("/report_battle/<hash_id>", methods=["POST"])
	def report_battle(hash_id):
		if hash_id not in claimed_battles:
			return ""

		output_file = f"{OUTPUT_BASE}/{hash_id}.json"
		with open(output_file, 'w') as f:
			json.dump(request.get_json(), f, indent=2)

		claimed_battles.remove(hash_id)
		print(f"reported hash id {hash_id} for ip {request.remote_addr}")

		return ""

	def write_output():
		print("writing output!")
		with open("battles_to_run.txt", 'w') as f:
			for battle in pending_battles + claimed_battles:
				f.write(battle + "\n")

	atexit.register(write_output)
	try:
		app.run(host="0.0.0.0", port=1337)
	except KeyboardInterrupt:
		print("closing out...")
		sys.exit()


if __name__ == '__main__':
	main()