import json

from hashids import Hashids

def load_json(path: str) -> dict:
	with open(path, 'r', encoding='utf-8') as f:
		return json.load(f)

trainers = load_json("trainers.json")
SAFE_ALPHABET = "abcdefghijkmnopqrstuvwxyz1234567890-!"
SALT = "elo"

hash_encoder = Hashids(salt=SALT, alphabet=SAFE_ALPHABET)

def generate_hashid(player, enemy, seed, debug=False):
	your_class, your_instance = player
	enemy_class, enemy_instance = enemy
	hash_nonce = seed

	your_class_id, your_instance_id = your_class["id"], your_instance["index"]
	enemy_class_id, enemy_instance_id = enemy_class["id"], enemy_instance["index"]

	hashid = hash_encoder.encode(your_class_id, your_instance_id, enemy_class_id, enemy_instance_id, hash_nonce)
	if debug:
		print("The hashid is    :", display_hashid(hashid))
		print("The simple id is :",
	      f"{your_class_id}-{your_instance_id}-{enemy_class_id}-{enemy_instance_id}-{hash_nonce}")
	return hashid

def display_hashid(hashid):
	return hashid[0:4] + " " + hashid[4:8] + " " + hashid[8:]


