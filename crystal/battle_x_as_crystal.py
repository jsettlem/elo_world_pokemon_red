import itertools
import json
import random
import struct
import subprocess
from typing import Iterable, Tuple

BGB_PATH = "bgb/bgb.exe"
ROM_IMAGE = "pokecrystal11.gbc"

BASE_SAVE = "base_state_1.sna"
BASE_AI_SAVE = "base_ai_state.sna"
BASE_SWITCH_SAVE = "ai_switch_base.sna"

OUT_SAVE = "outstate.sn1"
AI_INPUT_SAVE = "ai_input.sn1"
AI_OUTPUT_SAVE = "ai_output.sn1"
BATTLE_SAVE = "battlestate.sn1"
OUT_DEMO = "outdemo.dem"
AI_DEMO = "ai_demo.dem"

# GLOBAL_OFFSET = 0xBBC3
GLOBAL_OFFSET = 0xBAF0
TOTAL_CLOCKS_OFFSET = 0x21F
PC_OFFSET = 0xC7

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
BATTLE_MON_SIZE = 0x20

ENEMY_PARTY_START = 0xd280
ENEMY_PARTY_STRUCTS_START = 0xd288
ENEMY_PARTY_COUNT = 0xd280
ENEMY_PARTY_NICKS = 0xd3ea
MON_NICK_LENGTH = 11
ENEMY_PARTY_END = 0xd42c


PLAYER_PARTY_START = 0xdcd7
PLAYER_PARTY_COUNT = 0xdcd7
PLAYER_PARTY_STURCTS_START = 0xdcdf
PLAYER_PARTY_NICKS = 0xde41
PLAYER_PARTY_OTS = 0xddff
PLAYER_PARTY_END = 0xde83

wBattleMonNickname = (0xc621, POKEMON_NAME_LENGTH)
wEnemyMonNickname = (0xc616, POKEMON_NAME_LENGTH)

wBattleMon = (0xc62c, BATTLE_MON_SIZE)
wEnemyMon = (0xd206, BATTLE_MON_SIZE)
wEnemyMoveStruct = (0xc608, 7)
wPlayerMoveStruct = (0xc60f, 7)

wPlayerSubStatus1 = (0xc668, 1)
wEnemySubStatus1 = (0xc66d, 1)
wPlayerSubStatus2 = (0xc669, 1)
wEnemySubStatus2 = (0xc66e, 1)
wPlayerSubStatus3 = (0xc66a, 1)
wEnemySubStatus3 = (0xc66f, 1)
wPlayerSubStatus4 = (0xc66b, 1)
wEnemySubStatus4 = (0xc670, 1)
wPlayerSubStatus5 = (0xc66c, 1)
wEnemySubStatus5 = (0xc671, 1)

wCurPlayerMove = (0xc6e3, 1)
wCurEnemyMove = (0xc6e4, 1)
wLastPlayerCounterMove = (0xc6f8, 1)
wLastEnemyCounterMove = (0xc6f9, 1)
wLastPlayerMove = (0xc71b, 1)
wLastEnemyMove = (0xc71c, 1)
wPlayerRolloutCount = (0xc672, 1)
wEnemyRolloutCount = (0xc67a, 1)
wPlayerConfuseCount = (0xc673, 1)
wEnemyConfuseCount = (0xc67b, 1)
wPlayerToxicCount = (0xc674, 1)
wEnemyToxicCount = (0xc67c, 1)
wPlayerDisableCount = (0xc675, 1)
wEnemyDisableCount = (0xc67d, 1)
wPlayerEncoreCount = (0xc676, 1)
wEnemyEncoreCount = (0xc67e, 1)
wPlayerPerishCount = (0xc677, 1)
wEnemyPerishCount = (0xc67f, 1)
wPlayerFuryCutterCount = (0xc678, 1)
wEnemyFuryCutterCount = (0xc680, 1)
wPlayerProtectCount = (0xc679, 1)
wEnemyProtectCount = (0xc681, 1)
wPlayerScreens = (0xc6ff, 1)
wEnemyScreens = (0xc700, 1)
wPlayerDamageTaken = (0xc682, 2)
wEnemyDamageTaken = (0xc684, 2)
wPlayerStats = (0xc6b6, 10)
wEnemyStats = (0xc6c1, 10)
wPlayerStatLevels = (0xc6cc, 7)
wEnemyStatLevels = (0xc6d4, 7)
wPlayerTurnsTaken = (0xc6dd, 1)
wEnemyTurnsTaken = (0xc6dc, 1)
wPlayerSubstituteHP = (0xc6df, 1)
wEnemySubstituteHP = (0xc6e0, 1)
wDisabledMove = (0xc6f5, 1)
wEnemyDisabledMove = (0xc6f6, 1)

wCurPartyMon = (0xd109, 1)
wCurOTMon = (0xc663, 1)

wEnemyItemState = (0xc6e6, 1)
wCurEnemyMoveNum = (0xc6e9, 1)
wEnemyMinimized = (0xc6fa, 1)
wAlreadyFailed = (0xc6fb, 1)
wCurMoveNum = (0xd0d5, 1)

wPartyMenuCursor = (0xd0d8, 1)
wEnemySwitchMonIndex = (0xc718, 1)

breakpoints = {
	"SetUpBattlePartyMenu": 0x52f7,
	"AI_Switch": 0x446c,
	"LostBattle": 0x538e,
	"WinTrainerBattle": 0x4fa4
}

player_enemy_pairs = (
	(wBattleMonNickname, wEnemyMonNickname),
	(wBattleMon, wEnemyMon),
	(wPlayerMoveStruct, wEnemyMoveStruct),
	(wPlayerSubStatus1, wEnemySubStatus1),
	(wPlayerSubStatus2, wEnemySubStatus2),
	(wPlayerSubStatus3, wEnemySubStatus3),
	(wPlayerSubStatus4, wEnemySubStatus4),
	(wPlayerSubStatus5, wEnemySubStatus5),
	(wCurPlayerMove, wCurEnemyMove),
	(wLastPlayerCounterMove, wLastEnemyCounterMove),
	(wLastPlayerMove, wLastEnemyMove),
	(wPlayerRolloutCount, wEnemyRolloutCount),
	(wPlayerConfuseCount, wEnemyConfuseCount),
	(wPlayerToxicCount, wEnemyToxicCount),
	(wPlayerDisableCount, wEnemyDisableCount),
	(wPlayerEncoreCount, wEnemyEncoreCount),
	(wPlayerPerishCount, wEnemyPerishCount),
	(wPlayerFuryCutterCount, wEnemyFuryCutterCount),
	(wPlayerProtectCount, wEnemyProtectCount),
	(wPlayerScreens, wEnemyScreens),
	(wPlayerDamageTaken, wEnemyDamageTaken),
	(wPlayerStats, wEnemyStats),
	(wPlayerStatLevels, wEnemyStatLevels),
	(wPlayerTurnsTaken, wEnemyTurnsTaken),
	(wPlayerSubstituteHP, wEnemySubstituteHP),
	(wDisabledMove, wEnemyDisabledMove),
	(wCurPartyMon, wCurOTMon) #TODO: check that wcurpartymon is correct
)

NOTHING_BUTTON = 0b0
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

raw_trainer_data = load_json("trainers.json")

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


def get_total_clocks(source: bytearray) -> int:
	return struct.unpack_from("<Q", source[TOTAL_CLOCKS_OFFSET:])[0] & 0x7f_ff_ff_ff


def get_program_counter(source: bytearray) -> int:
	return (source[PC_OFFSET + 1] << 8) | source[PC_OFFSET]


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

def select_menu_item(current: int, target: int) -> Iterable[int]:
	if target < current:
		return [UP_BUTTON] * (current - target)
	else:
		return [DOWN_BUTTON] * (target - current)


def select_move(current_move: int, target_move: int) -> bytearray:
	return generate_demo([
		B_BUTTON,
		UP_BUTTON,
		LEFT_BUTTON,
		A_BUTTON,
		0, 0,
		*select_menu_item(current_move, target_move),
		A_BUTTON
	])


def choose_pokemon(current: int, target: int) -> bytearray:
	return generate_demo([
		0, 0, 0, 0, 0,
		*select_menu_item(current, target),
		A_BUTTON,
		0, 0, 0, 0, 0,
		A_BUTTON
	])

def select_switch(buffer_size=1) -> bytearray:
	return generate_demo([
		B_BUTTON,
		UP_BUTTON,
		RIGHT_BUTTON,
		A_BUTTON
	], buffer_button=NOTHING_BUTTON, buffer_size=buffer_size)

def get_trainer_identifier(trainer_dict):
	return f"{trainer_dict['title']} {trainer_dict['name']} #{trainer_dict['rematch']} (class: {trainer_dict['class']}, id: {trainer_dict['instance']})"


def initial_testing():

	# Set up player and enemy party data
	seed = random.randint(0, 1000000000)
	print("seed", seed)
	random.seed(seed)
	player_trainer, enemy_trainer = random.choice(raw_trainer_data), random.choice(raw_trainer_data)

	# player_class = player_trainer['class']
	# player_index = player_trainer['instance']
	# enemy_class = enemy_trainer['class']
	# enemy_index = enemy_trainer['instance']

	player_class = 50
	player_index = 1
	enemy_class = 9
	enemy_index = 1

	print(f"You are {get_trainer_identifier(player_trainer)}. Your opponent is {get_trainer_identifier(enemy_trainer)}")

	base = load_save(BASE_SAVE)
	load_trainer_info(player_class, player_index, BASE_SAVE, OUT_SAVE)
	new = load_save(OUT_SAVE)

	copy_values(new, ENEMY_PARTY_START, base, PLAYER_PARTY_START, PLAYER_PARTY_END - PLAYER_PARTY_START)
	enemy_party_size = get_value(new, ENEMY_PARTY_COUNT, 1)[0]

	enemy_mons = get_value(new, ENEMY_PARTY_STRUCTS_START, PARTY_STRUCT_SIZE * enemy_party_size)

	for i in range(enemy_party_size):
		pokemon_index = enemy_mons[PARTY_STRUCT_SIZE * i] - 1
		pokemon_name = name_to_bytes(pokemon_names[str(pokemon_index)])
		set_value(base, PLAYER_PARTY_NICKS + POKEMON_NAME_LENGTH * i, pokemon_name, POKEMON_NAME_LENGTH)
		copy_values(new, STRING_BUFFER_1, base, PLAYER_PARTY_OTS + POKEMON_NAME_LENGTH * i, POKEMON_NAME_LENGTH)

	copy_values(new, STRING_BUFFER_1, base, PLAYER_TRAINER_NAME, PLAYER_NAME_LENGTH)
	set_value(base, PLAYER_TRAINER_NAME + PLAYER_NAME_LENGTH - 1, [NAME_TERMINATOR], 1)
	set_value(base, PLAYER_GENDER, [0x1], 1)

	write_file(OUT_DEMO, generate_demo([]))
	write_file(AI_DEMO, generate_demo([B_BUTTON, B_BUTTON, B_BUTTON, B_BUTTON, A_BUTTON, A_BUTTON,
	                                   B_BUTTON, B_BUTTON, A_BUTTON, DOWN_BUTTON, A_BUTTON,
	                                   B_BUTTON, B_BUTTON, A_BUTTON, DOWN_BUTTON, A_BUTTON,
	                                   B_BUTTON, B_BUTTON, A_BUTTON, DOWN_BUTTON, A_BUTTON]))

	set_value(base, OTHER_TRAINER_CLASS, [enemy_class], 1)
	set_value(base, TRAINER_ID, [enemy_index], 1)
	write_file(BATTLE_SAVE, base)
	total_clocks = get_total_clocks(base)

	while True:
		# Play till the player first gains control
		breakpoint_condition = f"TOTALCLKS!=${total_clocks:x}"
		try:
			subprocess.call([BGB_PATH, '-rom', BATTLE_SAVE,
			                 '-br', f'BattleMenu/{breakpoint_condition},'
			                        f'SetUpBattlePartyMenu/{breakpoint_condition},'
			                        f'WinTrainerBattle/{breakpoint_condition},'
			                        f'LostBattle/{breakpoint_condition},',
			                 # '-hf',
			                 '-nobatt',
			                 '-stateonexit', BATTLE_SAVE,
			                 "-demoplay", OUT_DEMO,
			                 ], timeout=100)
		except subprocess.TimeoutExpired:
			pass

		battle_save = load_save(BATTLE_SAVE)

		pc = get_program_counter(battle_save)
		print(f'Program counter: {pc:x}')
		if pc in [breakpoints["WinTrainerBattle"], breakpoints["LostBattle"]]:
			print("You win and/or lose!")
			break
		elif pc == breakpoints["SetUpBattlePartyMenu"]:
			ai_save = load_save(BASE_SWITCH_SAVE)

			swap_pairings(battle_save, ai_save)

			write_file(AI_INPUT_SAVE, ai_save)

			# Open the AI state, wait for the results

			subprocess.call([BGB_PATH, '-rom', AI_INPUT_SAVE,
			                 '-br', 'LoadEnemyMon',
			                 '-hf',
			                 '-nobatt',
			                 # '-runfast',
			                 '-stateonexit', AI_OUTPUT_SAVE,
			                 "-demoplay", AI_DEMO,
			                 ], timeout=1000)

			# Parse AI actions
			ai_output = load_save(AI_OUTPUT_SAVE)

			selected_pokemon_index = get_value(ai_output, wCurPartyMon[0], wCurPartyMon[1])[0]
			current_pokemon_index = get_value(battle_save, wPartyMenuCursor[0], wPartyMenuCursor[1])[0]

			# wPartyMenu cursor starts unpopulated (0), but is 1-indexed
			current_pokemon_index = max(current_pokemon_index, 1) - 1
			print("The selected pokemon was", selected_pokemon_index, "and the current pokemon was", current_pokemon_index)

			button_sequence = choose_pokemon(current_pokemon_index, selected_pokemon_index)
		else:
			ai_save = load_save(BASE_AI_SAVE)

			swap_pairings(battle_save, ai_save)

			# TODO: Randomize rdiv w/ seeded value
			# TODO: Item counts
			# TODO: we may need to update more values here. Check the disassembly.
			# TODO: wTrainerClass in the AI branch

			# These allow us to make the game think our Pokemon is always on the last turn of Perish Song
			# set_value(ai_save, wEnemySubStatus1[0], [0x10], 1)
			# set_value(ai_save, wEnemyPerishCount[0], [0x1], 1)
			write_file(AI_INPUT_SAVE, ai_save)

			# Open the AI state, wait for the results

			subprocess.call([BGB_PATH, '-rom', AI_INPUT_SAVE,
			                 '-br', 'PlayerTurn_EndOpponentProtectEndureDestinyBond,'
			                        'EnemyTurn_EndOpponentProtectEndureDestinyBond,'
			                        'AI_Switch,'
			                        'EnemyUsedFullHeal,'
			                        'EnemyUsedMaxPotion,'
			                        'EnemyUsedFullRestore,'
			                        'EnemyUsedPotion,'
			                        'EnemyUsedSuperPotion,'
			                        'EnemyUsedHyperPotion,'
			                        'EnemyUsedXAccuracy,'
			                        'EnemyUsedGuardSpec,'
			                        'EnemyUsedDireHit,'
			                        'EnemyUsedXAttack,'
			                        'EnemyUsedXDefend,'
			                        'EnemyUsedXSpeed,'
			                        'EnemyUsedXSpecial',
			                 '-hf',
			                 '-nobatt',
			                 # '-runfast',
			                 '-stateonexit', AI_OUTPUT_SAVE,
			                 "-demoplay", AI_DEMO,
			                 ], timeout=1000)

			# Parse AI actions
			ai_output = load_save(AI_OUTPUT_SAVE)

			ai_pc = get_program_counter(ai_output)

			if ai_pc == breakpoints["AI_Switch"]:
				print("The AI wants to switcharino")
				target_pokemon = get_value(ai_output, wEnemySwitchMonIndex[0], wEnemySwitchMonIndex[1])[0] - 1
				current_pokemon_index = get_value(battle_save, wPartyMenuCursor[0], wPartyMenuCursor[1])[0]

				# wPartyMenu cursor starts unpopulated (0), but is 1-indexed
				current_pokemon_index = max(current_pokemon_index, 1) - 1
				print("The selected pokemon was", target_pokemon, "and the current pokemon was",
				      current_pokemon_index)

				button_sequence = select_switch() + choose_pokemon(current_pokemon_index, target_pokemon)

			else:
				selected_move_index = get_value(ai_output, wCurEnemyMoveNum[0], wCurEnemyMoveNum[1])[0]
				print("The selected move was", selected_move_index)
				current_move_index = get_value(battle_save, wCurMoveNum[0], wCurMoveNum[1])[0]

				button_sequence = select_move(current_move_index, selected_move_index)

		write_file(OUT_DEMO, button_sequence)

		total_clocks = get_total_clocks(battle_save)


def swap_pairings(source_save, target_save):
	# Copy data from battle save to ai save, swapping the player and enemy data
	for pairing in player_enemy_pairs:
		player_offset = pairing[0][0]
		enemy_offset = pairing[1][0]
		assert pairing[0][1] == pairing[1][1]
		size = pairing[0][1]
		copy_values(source_save, player_offset, target_save, enemy_offset, size)
		copy_values(source_save, enemy_offset, target_save, player_offset, size)
	copy_values(source_save, PLAYER_PARTY_START, target_save, ENEMY_PARTY_START, ENEMY_PARTY_END - ENEMY_PARTY_START)
	copy_values(source_save, ENEMY_PARTY_START, target_save, PLAYER_PARTY_START, PLAYER_PARTY_END - PLAYER_PARTY_START)


if __name__ == '__main__':
	initial_testing()
