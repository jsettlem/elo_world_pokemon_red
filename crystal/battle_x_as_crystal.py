import itertools
import json
import random
import subprocess
from typing import Iterable, Tuple

BGB_PATH = "bgb/bgb.exe"
ROM_IMAGE = "pokecrystal11.gbc"

BASE_SAVE = "base_state_1.sna"

OUT_SAVE = "outstate.sn1"
BATTLE_SAVE = "battlestate.sn1"
OUT_DEMO = "outdemo.dem"

# GLOBAL_OFFSET = 0xBBC3
GLOBAL_OFFSET = 0xBAF0

OTHER_TRAINER_CLASS = 0xd22f
# TRAINER_CLASS = 0xd233
TRAINER_ID = 0xd231

STRING_BUFFER_1 = 0xd073

ENEMY_NAME_LENGTH = 11
POKEMON_NAME_LENGTH = 11
NAME_TERMINATOR = 0x50

PLAYER_TRAINER_NAME = 0xd47d
PLAYER_NAME_LENGTH = 8

PLAYER_GENDER = 0xd472

PARTY_STRUCT_SIZE = 0x30

ENEMY_PARTY_START = 0xd280
ENEMY_PARTY_STRUCTS_START = 0xd288
ENEMY_PARTY_COUNT = 0xd280
ENEMY_PARTY_NICKS = 0xd3ea
MON_NICK_LENGTH = 11
ENEMY_PARTY_END = 0xd42c


PLAYER_PARTY_START = 0xdcd7
PLAYER_PARTY_NICKS = 0xde41
PLAYER_PARTY_OTS = 0xddff
PLAYER_PARTY_END = 0xde83

wBattleMon = (0, 0)
wEnemyMon = (0, 0)
wEnemyMoveStruct = (0, 0)
wPlayerMoveStruct = (0, 0)

wPlayerSubStatus1 = (0, 1)
wEnemySubStatus1 = (0, 1)
wPlayerSubStatus2 = (0, 1)
wEnemySubStatus2 = (0, 1)
wPlayerSubStatus3 = (0, 1)
wEnemySubStatus3 = (0, 1)
wPlayerSubStatus4 = (0, 1)
wEnemySubStatus4 = (0, 1)
wPlayerSubStatus5 = (0, 1)
wEnemySubStatus5 = (0, 1)
wBattleMonStatus = (0, 1)
wEnemyMonStatus = (0, 1)
wPlayerMoveStructAnimation = (0, 1)
wEnemyMoveStructAnimation = (0, 1)
wPlayerMoveStructEffect = (0, 1)
wEnemyMoveStructEffect = (0, 1)
wPlayerMoveStructPower = (0, 1)
wEnemyMoveStructPower = (0, 1)
wPlayerMoveStructType = (0, 1)
wEnemyMoveStructType = (0, 1)
wCurPlayerMove = (0, 1)
wCurEnemyMove = (0, 1)
wLastPlayerCounterMove = (0, 1)
wLastEnemyCounterMove = (0, 1)
wLastPlayerMove = (0, 1)
wLastEnemyMove = (0, 1)

wPlayerRolloutCount = (0, 1)
wEnemyRolloutCount = (0, 1)
wPlayerConfuseCount = (0, 1)
wEnemyConfuseCount = (0, 1)
wPlayerToxicCount = (0, 1)
wEnemyToxicCount = (0, 1)
wPlayerDisableCount = (0, 1)
wEnemyDisableCount = (0, 1)
wPlayerEncoreCount = (0, 1)
wEnemyEncoreCount = (0, 1)
wPlayerPerishCount = (0, 1)
wEnemyPerishCount = (0, 1)
wPlayerFuryCutterCount = (0, 1)
wEnemyFuryCutterCount = (0, 1)
wPlayerProtectCount = (0, 1)
wEnemyProtectCount = (0, 1)

wPlayerScreens = (0, 1)
wEnemyScreens = (0, 1)
wPlayerDamageTaken = (0, 1)
wEnemyDamageTaken = (0, 1)
wPlayerStats = (0, 1)
wEnemyStats = (0, 1)
wPlayerStatLevels = (0, 1)
wEnemyStatLevels = (0, 1)
wPlayerTurnsTaken = (0, 1)
wEnemyTurnsTaken = (0, 1)
wPlayerSubstituteHP = (0, 1)
wEnemySubstituteHP = (0, 1)
wDisabledMove = (0, 1)
wEnemyDisabledMove = (0, 1)

wEnemyItemState = (0, 1)
wCurEnemyMoveNum = (0, 1)
wEnemyMinimized = (0, 1)
wAlreadyFailed = (0, 1)

A_BUTTON = 0b00000001
B_BUTTON = 0b00000010
RIGHT_BUTTON = 0b00010000
LEFT_BUTTON = 0b00100000
UP_BUTTON = 0b01000000
DOWN_BUTTON = 0b10000000

def load_json(path: str) -> dict:
	with open(path, 'r', encoding='utf-8') as f:
		return json.load(f)


def load_memory_map(path: str) -> Tuple[dict, dict]:
	base = load_json(path)
	return {int(key, 16): value for key, value in base.items()}, {value: int(key, 16) for key, value in base.items()}

pokemon_names = load_json("pokemon_names.json")

characters, reverse_characters = load_memory_map('charmap.json')

def name_to_bytes(name: str, length: int = POKEMON_NAME_LENGTH) -> Iterable[int]:
	return (reverse_characters[name[i]] if i < len(name) else NAME_TERMINATOR for i in range(length))


def get_value(source: bytearray, offset: int, length: int) -> bytearray:
	return source[offset - GLOBAL_OFFSET:offset + length - GLOBAL_OFFSET]


def set_value(target: bytearray, offset: int, source: Iterable[int], length: int) -> None:
	target[offset - GLOBAL_OFFSET:offset + length - GLOBAL_OFFSET] = source


def copy_values(source: bytearray, source_offset: int, target: bytearray, target_offset: int, length: int) -> None:
	target[target_offset - GLOBAL_OFFSET:target_offset + length - GLOBAL_OFFSET] = source[
	                                                                               source_offset - GLOBAL_OFFSET:source_offset + length - GLOBAL_OFFSET]


def write_file(file: str, save: bytearray) -> None:
	with open(file, 'wb') as f:
		f.write(save)


def load_save(file: str) -> bytearray:
	with open(file, 'rb') as f:
		save = bytearray(f.read())
	return save


def load_trainer_info(trainer_id: int, trainer_index: int, battle_save: str = BATTLE_SAVE,
                      out_save: str = OUT_SAVE) -> None:
	save = load_save(BASE_SAVE)
	save[OTHER_TRAINER_CLASS - GLOBAL_OFFSET] = trainer_id
	save[TRAINER_ID - GLOBAL_OFFSET] = trainer_index
	write_file(battle_save, save)

	subprocess.call([BGB_PATH, '-rom', battle_save,
	                 # '-br', 'BackUpBGMap2',
	                 '-br', 'PlaceCommandCharacter',
	                 '-hf',
	                 '-nobatt',
	                 '-stateonexit', out_save],
	                timeout=10
	                )


def make_button_sequence(buttons: Iterable[int]) -> Iterable[int]:
	zero = itertools.repeat(0)
	buffer_size = 12
	return [
		half_press
		for full_press in zip(zero, buttons, buttons, *([zero] * buffer_size))
		for half_press in full_press
	]


def generate_demo(buttons: Iterable[int], buffer_button: int = B_BUTTON, buffer_size: int = 1000) -> bytearray:
	return bytearray([
		*make_button_sequence(buttons),
		*make_button_sequence([buffer_button] * buffer_size)
	])

def initial_testing():
	base = load_save(BASE_SAVE)
	load_trainer_info(27, 7, BASE_SAVE, OUT_SAVE)
	new = load_save(OUT_SAVE)

	copy_values(new, ENEMY_PARTY_START, base, PLAYER_PARTY_START, PLAYER_PARTY_END - PLAYER_PARTY_START)
	enemy_party_size = get_value(new, ENEMY_PARTY_COUNT, 1)[0]

	enemy_mons = get_value(new, ENEMY_PARTY_STRUCTS_START, PARTY_STRUCT_SIZE * enemy_party_size)

	for i in range(enemy_party_size):
		pokemon_index = enemy_mons[PARTY_STRUCT_SIZE * i] - 1
		print(pokemon_index)
		pokemon_name = name_to_bytes(pokemon_names[str(pokemon_index)])
		set_value(base, PLAYER_PARTY_NICKS + POKEMON_NAME_LENGTH * i, pokemon_name, POKEMON_NAME_LENGTH)
		copy_values(new, STRING_BUFFER_1, base, PLAYER_PARTY_OTS + POKEMON_NAME_LENGTH * i, POKEMON_NAME_LENGTH)

	copy_values(new, STRING_BUFFER_1, base, PLAYER_TRAINER_NAME, PLAYER_NAME_LENGTH)
	set_value(base, PLAYER_TRAINER_NAME + PLAYER_NAME_LENGTH - 1, [NAME_TERMINATOR], 1)
	set_value(base, PLAYER_GENDER, [0x1], 1)

	write_file(OUT_DEMO, generate_demo([]))

	set_value(base, OTHER_TRAINER_CLASS, [15], 1)
	write_file(BATTLE_SAVE, base)
	try:
		subprocess.call([BGB_PATH, '-rom', BATTLE_SAVE,
		                 '-br', 'BattleMenu',
		                 # '-hf',
		                 '-nobatt',
		                 '-stateonexit', OUT_SAVE,
		                 "-demoplay", OUT_DEMO,
		                 ], timeout=100)
	except subprocess.TimeoutExpired:
		pass


if __name__ == '__main__':
	initial_testing()
