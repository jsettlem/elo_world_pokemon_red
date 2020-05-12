import json
import pickle
import zlib
import gc
from typing import Dict

from common_types import *


def load_json(path: str) -> dict:
	with open(path, 'r', encoding='utf-8') as f:
		return json.load(f)


trainers = load_json("trainers.json")


def get_trainer_by_id(trainer_id: int, instance_index: int) -> Tuple[dict, dict]:
	for trainer in trainers:
		if trainer["id"] == trainer_id:
			return trainer, trainer["instances"][instance_index - 1]
	raise ValueError("Trainer ID not found")


def load_pickle(pickle_loc: str) -> Tuple[Dict[str, Trainer], Dict[str, Battle]]:
	with open(pickle_loc, 'rb') as f:
		print("reading data")
		data = f.read()
		print("uncompressing")
		uncompressed = zlib.decompress(data)
		print("loading pickle")
		gc.disable()
		loaded_pickle = pickle.loads(uncompressed)
		print("returning pickle")
		gc.enable()
		return loaded_pickle


def save_pickle(pickle_loc: str, trainer_dict: Dict[str, Trainer], battle_dict: Dict[str, Battle]):
	with open(pickle_loc, 'wb') as f:
		f.write(zlib.compress(
			pickle.dumps((trainer_dict, battle_dict), protocol=pickle.HIGHEST_PROTOCOL),
			level=9)
		)
