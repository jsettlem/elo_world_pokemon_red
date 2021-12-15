import itertools
import json
import os
import random
import shutil
import struct
import subprocess
from dataclasses import dataclass
from pprint import pprint
from typing import Iterable, Tuple

BASE_DIR = os.path.abspath("./static_files")

# static files
BGB_PATH = f"{BASE_DIR}/bgb/bgb.exe"

ROM_NAME = "pokecrystal11.gbc"
MEMORY_MAP_NAME = "pokecrystal11.sym"

ROM_IMAGE = f"{BASE_DIR}/{ROM_NAME}"
MEMORY_MAP = f"{BASE_DIR}/{MEMORY_MAP_NAME}"


BASE_SAVE = f"{BASE_DIR}/base_state_1.sna"
BASE_AI_SAVE = f"{BASE_DIR}/base_ai_state.sna"
BASE_SWITCH_SAVE = f"{BASE_DIR}/ai_switch_base.sna"

AI_DEMO = f"{BASE_DIR}/ai_demo.dem"

# dynamic files
OUT_SAVE = "outstate.sn1"
AI_INPUT_SAVE = "ai_input.sn1"
AI_OUTPUT_SAVE = "ai_output.sn1"
BATTLE_SAVE = "battlestate.sn1"
OUT_DEMO = "outdemo.dem"

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
	(wCurPartyMon, wCurOTMon)  # TODO: check that wcurpartymon is correct
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


pokemon_names = load_json("data_files/pokemon_names.json")

characters, reverse_characters = load_memory_map('data_files/charmap.json')

raw_trainer_data = load_json("data_files/trainers.json")


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


def load_trainer_info(trainer_id: int, trainer_index: int, in_save: bytearray, working_save: str) -> bytearray:
	save = in_save.copy()
	save[OTHER_TRAINER_CLASS - GLOBAL_OFFSET] = trainer_id
	save[TRAINER_ID - GLOBAL_OFFSET] = trainer_index
	write_file(working_save, save)

	subprocess.call([BGB_PATH, '-rom', working_save,
	                 # '-br', 'BackUpBGMap2',
	                 '-br', 'PlaceCommandCharacter',
	                 '-hf',
	                 '-nobatt',
	                 '-stateonexit', working_save],
	                timeout=10
	                )

	return load_save(working_save)


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


@dataclass
class MovieContext:
	movie_name: str
	movie_index: int
	movie_working_dir: str
	movie_output_dir: str


def call_bgb(in_save: str,
             out_save: str,
             demo: str,
             breakpoint_list: Iterable[str],
             movie_context: "MovieContext" = None,
             hf: bool = True,
             timeout: int = 10) -> None:
	params = [BGB_PATH, '-rom', in_save,
	          *(['-br', ",".join(breakpoint_list)] if breakpoint_list else []),
	          '-hf' if hf else '',
	          '-nobatt',
	          '-stateonexit', out_save,
	          *(['-demoplay', demo] if demo else []),
	          *([
		            "-set", "RecordAVI=1",
		            "-set", "WavFileOut=1",
		            "-set", f"RecordAVIfourCC=cscd",
		            "-set", "RecordHalfSpeed=0",
		            "-set", "Speed=1",
		            "-set", f"RecordPrefix={movie_context.movie_working_dir}/movie{movie_context.movie_index:05}",
	            ] if movie_context is not None else []),
	          ]
	pprint(params)
	subprocess.call(params, timeout=timeout)


def initial_testing():
	run_identifier = random.randint(1, 10000000)
	working_dir = os.path.abspath(f"./working/{run_identifier}")
	output_dir = os.path.abspath(f"./output/{run_identifier}")
	movie_working_dir = f"{working_dir}/movie"
	save_working_dir = f"{working_dir}/saves"
	demo_working_dir = f"{working_dir}/demo"
	movie_context = MovieContext(movie_name=str(run_identifier),
	                             movie_index=0,
	                             movie_working_dir=movie_working_dir,
	                             movie_output_dir=output_dir)

	for dir in [working_dir, output_dir, save_working_dir, demo_working_dir, movie_working_dir]:
		os.makedirs(dir, exist_ok=True)

	out_save_path = f"{save_working_dir}/{OUT_SAVE}"
	ai_input_save_path = f"{save_working_dir}/{AI_INPUT_SAVE}"
	ai_output_save_path = f"{save_working_dir}/{AI_OUTPUT_SAVE}"
	battle_save_path = f"{save_working_dir}/{BATTLE_SAVE}"
	out_demo_path = f"{demo_working_dir}/{OUT_DEMO}"

	print(BASE_DIR)
	shutil.copyfile(ROM_IMAGE, f"{save_working_dir}/{ROM_NAME}")
	shutil.copyfile(MEMORY_MAP, f"{save_working_dir}/{MEMORY_MAP_NAME}")

	# Set up player and enemy party data
	seed = random.randint(0, 1000000000)
	print("seed", seed)
	random.seed(seed)
	player_trainer, enemy_trainer = random.choice(raw_trainer_data), random.choice(raw_trainer_data)

	player_class = player_trainer['class']
	player_index = player_trainer['instance']
	enemy_class = enemy_trainer['class']
	enemy_index = enemy_trainer['instance']

	# player_class = 63
	# player_index = 1
	# enemy_class = 16
	# enemy_index = 1

	print(f"You are {get_trainer_identifier(player_trainer)}. Your opponent is {get_trainer_identifier(enemy_trainer)}")

	base_save = load_save(BASE_SAVE)

	player_trainer_info = load_trainer_info(player_class, player_index, base_save, out_save_path)

	battle_save = set_up_battle_save(base_save, player_trainer_info, enemy_class, enemy_index)

	write_file(battle_save_path, battle_save)

	write_file(out_demo_path, generate_demo([]))
	total_clocks = get_total_clocks(battle_save)

	while True:
		# Play till the player gains control
		breakpoint_condition = f"TOTALCLKS!=${total_clocks:x}"
		call_bgb(in_save=battle_save_path,
		         out_save=battle_save_path,
		         demo=out_demo_path,
		         breakpoint_list=[
			         f'BattleMenu/{breakpoint_condition}',
			         f'SetUpBattlePartyMenu/{breakpoint_condition}',
			         f'WinTrainerBattle/{breakpoint_condition}',
			         f'LostBattle/{breakpoint_condition},',
		         ],
		         movie_context=movie_context)

		battle_save = load_save(battle_save_path)

		pc = get_program_counter(battle_save)
		print(f'Program counter: {pc:x}')
		if pc == breakpoints["WinTrainerBattle"]:
			# Player won!

			print("You win!")
			break
		elif pc == breakpoints["LostBattle"]:
			# Enemy won!

			print("You lose!")
			break
		elif pc == breakpoints["SetUpBattlePartyMenu"]:
			# AI is forced to switch out, what should we switch to?

			ai_output = get_ai_action(battle_save=battle_save,
			                          base_save=BASE_SWITCH_SAVE,
			                          working_save=ai_input_save_path,
			                          out_save=ai_output_save_path)

			selected_pokemon_index = get_value(ai_output, wCurPartyMon[0], wCurPartyMon[1])[0]
			current_pokemon_index = get_value(battle_save, wPartyMenuCursor[0], wPartyMenuCursor[1])[0]

			# wPartyMenu cursor starts unpopulated (0), but is 1-indexed
			current_pokemon_index = max(current_pokemon_index, 1) - 1
			print("The selected pokemon was", selected_pokemon_index, "and the current pokemon was",
			      current_pokemon_index)

			button_sequence = choose_pokemon(current_pokemon_index, selected_pokemon_index)
		else:
			# We're at the battle menu, what should we choose?

			ai_output = get_ai_action(battle_save=battle_save,
			                          base_save=BASE_AI_SAVE,
			                          working_save=ai_input_save_path,
			                          out_save=ai_output_save_path)

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

		write_file(out_demo_path, button_sequence)

		total_clocks = get_total_clocks(battle_save)

	build_movie(movie_context)


def set_up_battle_save(base_save: bytearray, player_trainer_info: bytearray, enemy_class: int,
                       enemy_index: int) -> bytearray:
	battle_save = base_save.copy()

	copy_values(player_trainer_info, ENEMY_PARTY_START, battle_save, PLAYER_PARTY_START,
	            PLAYER_PARTY_END - PLAYER_PARTY_START)

	enemy_party_size = get_value(player_trainer_info, ENEMY_PARTY_COUNT, 1)[0]
	enemy_mons = get_value(player_trainer_info, ENEMY_PARTY_STRUCTS_START, PARTY_STRUCT_SIZE * enemy_party_size)

	for i in range(enemy_party_size):
		pokemon_index = enemy_mons[PARTY_STRUCT_SIZE * i] - 1
		pokemon_name = name_to_bytes(pokemon_names[str(pokemon_index)])
		set_value(battle_save, PLAYER_PARTY_NICKS + POKEMON_NAME_LENGTH * i, pokemon_name, POKEMON_NAME_LENGTH)
		copy_values(player_trainer_info, STRING_BUFFER_1, battle_save, PLAYER_PARTY_OTS + POKEMON_NAME_LENGTH * i,
		            POKEMON_NAME_LENGTH)

	copy_values(player_trainer_info, STRING_BUFFER_1, battle_save, PLAYER_TRAINER_NAME, PLAYER_NAME_LENGTH)
	set_value(battle_save, PLAYER_TRAINER_NAME + PLAYER_NAME_LENGTH - 1, [NAME_TERMINATOR], 1)
	set_value(battle_save, PLAYER_GENDER, [0x1], 1)

	set_value(battle_save, OTHER_TRAINER_CLASS, [enemy_class], 1)
	set_value(battle_save, TRAINER_ID, [enemy_index], 1)

	return battle_save


def generate_ai_demo():
	write_file(AI_DEMO, generate_demo([B_BUTTON, B_BUTTON, B_BUTTON, B_BUTTON, A_BUTTON, A_BUTTON,
	                                   B_BUTTON, B_BUTTON, A_BUTTON, DOWN_BUTTON, A_BUTTON,
	                                   B_BUTTON, B_BUTTON, A_BUTTON, DOWN_BUTTON, A_BUTTON,
	                                   B_BUTTON, B_BUTTON, A_BUTTON, DOWN_BUTTON, A_BUTTON]))


def get_ai_action(battle_save: bytearray, base_save: str, working_save: str, out_save: str):
	ai_save = load_save(base_save)
	swap_pairings(battle_save, ai_save)

	# TODO: Randomize rdiv w/ seeded value
	# TODO: Item counts
	# TODO: we may need to update more values here. Check the disassembly.
	# TODO: wTrainerClass in the AI branch

	# These allow us to make the game think our Pokemon is always on the last turn of Perish Song
	# set_value(ai_save, wEnemySubStatus1[0], [0x10], 1)
	# set_value(ai_save, wEnemyPerishCount[0], [0x1], 1)

	write_file(working_save, ai_save)
	# Open the AI state, wait for the results
	call_bgb(in_save=working_save,
	         out_save=out_save,
	         demo=AI_DEMO,
	         breakpoint_list=[
		         # for switching:
		         'LoadEnemyMon',
		         # for move selection:
		         'PlayerTurn_EndOpponentProtectEndureDestinyBond',
		         'EnemyTurn_EndOpponentProtectEndureDestinyBond',
		         'AI_Switch',
		         'EnemyUsedFullHeal',
		         'EnemyUsedMaxPotion',
		         'EnemyUsedFullRestore',
		         'EnemyUsedPotion',
		         'EnemyUsedSuperPotion',
		         'EnemyUsedHyperPotion',
		         'EnemyUsedXAccuracy',
		         'EnemyUsedGuardSpec',
		         'EnemyUsedDireHit',
		         'EnemyUsedXAttack',
		         'EnemyUsedXDefend',
		         'EnemyUsedXSpeed',
		         'EnemyUsedXSpecial',
	         ])
	# Parse AI actions
	ai_output = load_save(out_save)
	return ai_output


def create_concat_file(list_txt, files):
	with open(list_txt, 'w') as f:
		f.write("ffconcat version 1.0\n")
		f.write("\n".join(f"file '{f}'" for f in files))


def build_movie(movie_context: "MovieContext"):
	files = [f for f in os.listdir(movie_context.movie_working_dir)]
	files.sort()

	video_list_txt = f"{movie_context.movie_working_dir}/videos.txt"
	audio_list_txt = f"{movie_context.movie_working_dir}/audio.txt"

	create_concat_file(video_list_txt, [f for f in files if f.endswith(".avi")])
	create_concat_file(audio_list_txt, [f for f in files if f.endswith(".wav")])

	output_movie = f"{movie_context.movie_output_dir}/movies/{movie_context.movie_name}.mkv"
	os.makedirs(os.path.dirname(output_movie), exist_ok=True)

	subprocess.call(["ffmpeg",
	                 "-i", video_list_txt,
	                 "-i", audio_list_txt,
	                 "-c:v", "libx265",
	                 "-preset", "slow",
	                 "-crf", "17",
	                 "-c:a", "libopus",
	                 "-b:a", "32k",
	                 "-threads", "1",
	                 output_movie])


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
