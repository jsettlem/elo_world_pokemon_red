import itertools
import json
import os
import random
import shutil
import struct
import subprocess
import time
import uuid
from pprint import pprint
from typing import Iterable, Tuple
from hashids import Hashids


class StupidHack(Exception):
	pass


WORKING_DIR_BASE = "W:/elo_world_scratch/red_redux"
OUTPUT_BASE = "W:/elo_world_output/red_redux"

BGB_PATH = "bgb/bgb.exe"
LOSSLESS = True

ROM_IMAGE = "Pokemon - Red Version (UE) [S][!].gb"
BASE_SAVE = "basestate.sn1"
AI_SAVE = "ai_choose_state.sn1"

BATTLE_SAVE = "battlestate.sn1"
OUT_SAVE = "outstate.sn1"
OUT_DEMO = "outdemo.dem"

SAFE_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz1234567890"
SALT = "elo"
hash_encoder = Hashids(salt=SALT, alphabet=SAFE_ALPHABET)



def load_json(path: str) -> dict:
	with open(path, 'r', encoding='utf-8') as f:
		return json.load(f)


def load_memory_map(path: str) -> Tuple[dict, dict]:
	base = load_json(path)
	return {int(key, 16): value for key, value in base.items()}, {value: int(key, 16) for key, value in base.items()}


pokemon_names = load_json("pokemon_names.json")
trainers = load_json("trainers.json")
characters, reverse_characters = load_memory_map('charmap.json')
moves, reverse_moves = load_memory_map('moves.json')
items, reverse_items = load_memory_map('items.json')

GLOBAL_OFFSET = 0xBBC3

x_id = 201
x_index = 1
y_id = 202
y_index = 2

PLAYER_NAME = 0xd158
ENEMY_TRAINER_NAME = 0xd04a
POKEMON_NAME_LENGTH = 11
TRAINER_NAME_LENGTH = 13
NAME_TERMINATOR = 0x50

PARTY_NICKNAMES = 0xd2b5

PARTY_MON_OT = 0xd273
ENEMY_MON_OT = 0xd9ac

TRAINER_CLASS = 0xd059
TRAINER_CLASS_WITHOUT_OFFSET = 0xd031
TRAINER_INSTANCE = 0xd05d

PARTY_MON_LIST = 0xd164
ENEMY_PARTY_MON_LIST = 0xd89d
PARTY_MON_HP = 0xd16c

PARTY_COUNT = 0xd163
ENEMY_PARTY_COUNT = 0xd89c

PARTY_MONS = 0xd16b
ENEMY_PARTY_MONS = 0xd8a4

LONE_ATTACK_NO = 0xd05c

PARTY_STRUCT_SIZE = 0x2C

PLAYER_SELECTED_MOVE = 0xccdc
ENEMY_SELECTED_MOVE = 0xccdd

BATTLE_MON_NAME = 0xd009
BATTLE_MON = 0xd014
BATTLE_MON_HP = 0xd015
BATTLE_MON_MAX_HP = 0xd023
BATTLE_MON_PARTY_POS = 0xcc2f
BATTLE_MON_MOVES = 0xd01c
BATTLE_MON_SPEED = 0xd029
BATTLE_MON_PP = 0xd02d

ENEMY_BATTLE_MON_NAME = 0xcfda
ENEMY_BATTLE_MON = 0xcfe5
ENEMY_BATTLE_MON_PARTY_POS = 0xcfe8
ENEMY_BATTLE_MON_HP = 0xcfe6
ENEMY_BATTLE_MON_MAX_HP = 0xcff4
BATTLE_MON_SIZE = 0x1c

DISABLED_MOVE = 0xd06d
ENEMY_DISABLED_MOVE = 0xd072

ENEMY_ITEM_USED = 0xcf05
AI_ACTION_COUNT = 0xccdf

DIVISOR_OFFSET = 0x220
PC_OFFSET = 0xDA
TOTAL_CLOCKS_OFFSET = 0x232

SWITCH_CALL_OFFSET = 0x6765
DISPLAY_BATTLE_MENU_OFFSET = 0x4eb6
PARTY_MENU_INIT_OFFSET = 0x1420

TRAINER_WIN_OFFSET = 0x4696
ENEMY_WIN_OFFSET = 0x4874

MOVE_LIST_INDEX = 0xcc2e

BAG_ITEM_COUNT = 0xd31d
BAG_ITEMS = 0xd31e

A_BUTTON = 0b00000001
B_BUTTON = 0b00000010
RIGHT_BUTTON = 0b00010000
LEFT_BUTTON = 0b00100000
UP_BUTTON = 0b01000000
DOWN_BUTTON = 0b10000000

BATTLE_ANIMATIONS = True
OPTIONS = 0xd355
ANIMATION_FLAG = 0b11111111

INSTANT_TEXT = True
LETTER_PRINTING_DELAY = 0xd355
LETTER_PRINTING_DELAY_FLAG = 0b0100000

PARTY_MENU_CHOICE = 0xcc2b
GAIN_EXP_FLAG = 0xd058


def byte_to_pokestring(byte_array: Iterable[int]) -> str:
	return "".join(characters[b_int] if (b_int := int(b)) in characters else f"[0x{b:x}]" for b in byte_array)


def name_to_bytes(name: str, length: int = POKEMON_NAME_LENGTH) -> Iterable[int]:
	return (reverse_characters[name[i]] if i < len(name) else NAME_TERMINATOR for i in range(length))


def load_trainer_info(trainer_id: int, trainer_index: int, lone_move_number: int, battle_save: str = BATTLE_SAVE,
                      out_save: str = OUT_SAVE) -> None:
	save = load_save(BASE_SAVE)
	save[TRAINER_CLASS - GLOBAL_OFFSET] = trainer_id
	save[TRAINER_INSTANCE - GLOBAL_OFFSET] = trainer_index
	save[LONE_ATTACK_NO - GLOBAL_OFFSET] = lone_move_number
	write_file(battle_save, save)

	subprocess.call([BGB_PATH, '-rom', battle_save,
	                 '-ab', 'da44//w',
	                 '-hf',
	                 '-nobatt',
	                 '-stateonexit', out_save],
	                timeout=10)


def get_trainer_string(trainer_class: dict, trainer_instance: dict) -> str:
	location = trainer_instance['location']
	return f"a {trainer_class['class']} from {location if location != '' else 'somewhere'} who has a " + \
	       ", ".join(f"level {pokemon['level']} {pokemon['species']}" for pokemon in trainer_instance["party"]) + \
	       f" (class id: {trainer_class['id']}, instance number: {trainer_instance['index']})"


def get_ai_action(out_save: str = OUT_SAVE) -> Tuple[int, int, bool]:
	subprocess.call([BGB_PATH, '-rom', out_save,
	                 '-br', '4349,6765',
	                 '-ab', 'cf05//r',
	                 '-hf',
	                 '-nobatt',
	                 '-stateonexit', out_save],
	                timeout=10)
	save = load_save(out_save)
	move_id = get_value(save, ENEMY_SELECTED_MOVE, 1)[0]
	item_id = get_value(save, ENEMY_ITEM_USED, 1)[0]
	program_counter = get_program_counter(save)
	return move_id, item_id, program_counter == SWITCH_CALL_OFFSET


def get_random_trainer() -> Tuple[dict, dict]:
	trainer = random.choice(trainers)
	trainer_instance = random.choice(trainer["instances"])
	return trainer, trainer_instance


def get_trainer_by_id(trainer_id: int, instance_index: int) -> Tuple[dict, dict]:
	for trainer in trainers:
		if trainer["id"] == trainer_id:
			return trainer, trainer["instances"][instance_index - 1]
	raise ValueError("Trainer ID not found")


def get_string(source: bytearray, offset: int, length: int) -> str:
	return byte_to_pokestring(get_value(source, offset, length))


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


def randomize_rdiv(source: bytearray, rng):
	source[DIVISOR_OFFSET:DIVISOR_OFFSET + 3] = (rng.randint(0, 255) for _ in range(3))


def get_total_clocks(source: bytearray) -> int:
	return struct.unpack_from("<Q", source[TOTAL_CLOCKS_OFFSET:])[0] & 0x7f_ff_ff_ff


def get_program_counter(source: bytearray) -> int:
	return (source[PC_OFFSET + 1] << 8) | source[PC_OFFSET]


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


def select_switch() -> bytearray:
	return generate_demo([
		UP_BUTTON,
		RIGHT_BUTTON,
		A_BUTTON
	])


def get_move_count(battle_state: bytearray) -> int:
	battle_moves = get_value(battle_state, BATTLE_MON_MOVES, 4)
	return len([b for b in battle_moves if b != 0x0])


def get_move_index(battle_state: bytearray, move_id: int) -> int:
	battle_moves = get_value(battle_state, BATTLE_MON_MOVES, 4)
	return battle_moves.index(move_id) if move_id in battle_moves else 0


def get_pokemon_to_switch_to(battle_state: bytearray) -> int:
	current_pokemon = get_value(battle_state, BATTLE_MON_PARTY_POS, 1)[0]
	for i in range(6):
		if i == current_pokemon:
			continue
		party_mon_hp = get_value(battle_state, PARTY_MON_HP + i * PARTY_STRUCT_SIZE, 2)
		if party_mon_hp[0] | party_mon_hp[1]:
			return i
	return 0


def choose_pokemon(current: int, target: int) -> bytearray:
	return generate_demo([
		0, 0, 0, 0, 0,
		*select_menu_item(current, target),
		A_BUTTON,
		0, 0, 0, 0, 0,
		A_BUTTON
	])


def use_item():
	return generate_demo([
		0, 0, 0, 0,
		DOWN_BUTTON,
		LEFT_BUTTON,
		A_BUTTON,
		0, 0, 0, 0, 0,
		A_BUTTON,
		A_BUTTON
	])


def copy_dependencies(working_dir):
	for file in [ROM_IMAGE]:
		shutil.copyfile(file, f"{working_dir}/{file}")


def get_hp(source, offset):
	hp_word = get_value(source, offset, 2)
	return hp_word[0] << 8 | hp_word[1]


def get_party_mon(source: bytearray, offset: int, i: int):
	party_mon = get_value(source, offset + PARTY_STRUCT_SIZE * i, PARTY_STRUCT_SIZE)
	try:
		return {
			"species": pokemon_names[str(int(party_mon[0]) - 1)].strip("@"),
			"hp": party_mon[0x1] << 8 | party_mon[0x2],
			"max_hp": party_mon[34] << 8 | party_mon[35]
		}
	except KeyError:
		# gross edge case hack -- if the rival wins, the battle end breakpoint isn't hit. We can detect that here because the species of their first Pokemon becomes -1
		raise StupidHack()


def battle_x_as_y(your_class, your_instance, enemy_class, enemy_instance, run_number="", save_movie=True,
                  save_json=True, seed=None) -> dict:
	if seed is None:
		rng = random.Random()
	else:
		rng = random.Random(seed)

	working_dir = f"{WORKING_DIR_BASE}/{run_number}"
	os.makedirs(working_dir, exist_ok=True)

	rom_image_path = f"{working_dir}/{ROM_IMAGE}"
	shutil.copyfile(ROM_IMAGE, rom_image_path)

	movie_path = f"{working_dir}/movies"
	movie_index = 0

	bgb_options = ["-hf", "-nowarn", "-nobatt"]
	if save_movie:
		os.makedirs(movie_path)
		bgb_options = [*bgb_options,
		               "-set", "RecordAVI=1",
		               "-set", "WavFileOut=1",
		               "-set", f"RecordAVIfourCC={'cscd' if LOSSLESS else 'X264'}",
		               "-set", "RecordHalfSpeed=0",
		               "-set", "Speed=1",
		               "-set", "//set in battle loop",
		               ]

	battle_save_path = f"{working_dir}/{BATTLE_SAVE}"
	out_save_path = f"{working_dir}/{OUT_SAVE}"
	out_demo_path = f"{working_dir}/{OUT_DEMO}"

	base = load_save(BASE_SAVE)

	print("getting trainer info")
	start = time.time()
	load_trainer_info(your_class["id"], your_instance["index"],
	                  your_instance["loneMoves"] if "loneMoves" in your_instance else 0,
	                  battle_save_path, out_save_path)
	print("Got trainer info in ", time.time() - start)

	new = load_save(out_save_path)
	copy_values(new, ENEMY_TRAINER_NAME, base, PLAYER_NAME, POKEMON_NAME_LENGTH - 1)
	set_value(base, PLAYER_NAME + POKEMON_NAME_LENGTH - 1, [NAME_TERMINATOR], 1)

	copy_values(new, ENEMY_PARTY_COUNT, base, PARTY_COUNT, 1)
	copy_values(new, ENEMY_PARTY_MON_LIST, base, PARTY_MON_LIST, 7)
	copy_values(new, ENEMY_PARTY_MONS, base, PARTY_MONS, PARTY_STRUCT_SIZE * 6)

	party_size = get_value(new, ENEMY_PARTY_COUNT, 1)[0]
	enemy_mons = get_value(new, ENEMY_PARTY_MONS, PARTY_STRUCT_SIZE * party_size)
	for i in range(party_size):
		pokemon_index = enemy_mons[PARTY_STRUCT_SIZE * i] - 1
		pokemon_name = name_to_bytes(pokemon_names[str(pokemon_index)])
		set_value(base, PARTY_NICKNAMES + POKEMON_NAME_LENGTH * i, pokemon_name, POKEMON_NAME_LENGTH)
		copy_values(new, ENEMY_TRAINER_NAME, base, PARTY_MON_OT + POKEMON_NAME_LENGTH * i, POKEMON_NAME_LENGTH)

	set_value(base, TRAINER_CLASS, [enemy_class["id"]], 1)
	set_value(base, TRAINER_INSTANCE, [enemy_instance["index"]], 1)

	if "loneMoves" in enemy_instance:
		set_value(base, LONE_ATTACK_NO, [enemy_instance["loneMoves"]], 1)

	if BATTLE_ANIMATIONS:
		set_value(base, OPTIONS, [ANIMATION_FLAG], 1)

	if INSTANT_TEXT:
		set_value(base, LETTER_PRINTING_DELAY, [LETTER_PRINTING_DELAY_FLAG], 1)

	randomize_rdiv(base, rng)

	base_ai_action_count = your_class["actionCount"] if "actionCount" in your_class else 3
	ai_action_count = base_ai_action_count

	print(f"You are {get_trainer_string(your_class, your_instance)}")
	print(f"Your opponent is {get_trainer_string(enemy_class, enemy_instance)}")

	write_file(battle_save_path, base)
	write_file(out_demo_path, generate_demo([]))

	total_clocks = get_total_clocks(base)

	using_item = False
	last_pokemon = 0

	battle_log = {
		"run_id": run_number,
		"player_class": your_class['id'],
		"player_id": your_instance['index'],
		"enemy_class": enemy_class['id'],
		"enemy_id": enemy_instance['index'],
		"winner": None,
		"turn_count": 0,
		"turns": []
	}

	turn_number = 0
	enemy_party_size = 0
	record_low_total_hp = 99999
	turns_without_damage = 0

	while True:
		if turn_number > 1000:
			battle_log["winner"] = "Draw by 1000 turn rule"
			print("Too long! It's a draw!")
			break
		elif turns_without_damage > 75:
			battle_log["winner"] = "Draw by 75 turn damage rule"
			print("Too long without damage! It's a draw!")
			break

		if save_movie:
			movie_index += 1
			bgb_options[-1] = f"RecordPrefix={movie_path}/movie{movie_index:05}"

		breakpoint_condition = f"TOTALCLKS>${total_clocks:x}"

		try:
			subprocess.call([BGB_PATH, battle_save_path, *bgb_options,
			                 "-br", f"4eb6/{breakpoint_condition},"
			                        f"1420/{breakpoint_condition},"
			                        f"4696/{breakpoint_condition},"
			                        f"4874/{breakpoint_condition}",
			                 "-stateonexit", battle_save_path,
			                 "-demoplay", out_demo_path],
			                timeout=60)
		except subprocess.TimeoutExpired:
			battle_log["winner"] = "Draw by bgb timeout in move"
			break

		battle_state = load_save(battle_save_path)
		ai_base = load_save(AI_SAVE)

		if enemy_party_size == 0:
			enemy_party_size = get_value(battle_state, ENEMY_PARTY_COUNT, 1)[0]

		total_clocks = get_total_clocks(battle_state)
		pc = get_program_counter(battle_state)

		current_pokemon = get_value(battle_state, BATTLE_MON_PARTY_POS, 1)[0]
		if pc == PARTY_MENU_INIT_OFFSET:
			current_party_menu_choice = get_value(battle_state, PARTY_MENU_CHOICE, 1)[0]
			if using_item:
				button_sequence = choose_pokemon(current_party_menu_choice, current_pokemon)
				using_item = False
			else:
				button_sequence = choose_pokemon(current_party_menu_choice, get_pokemon_to_switch_to(battle_state))
		elif pc == TRAINER_WIN_OFFSET:
			print(f"{your_class['class']} wins!")
			battle_log["winner"] = "trainer"
			break
		elif pc == ENEMY_WIN_OFFSET:
			print(f"{enemy_class['class']} wins!")
			battle_log["winner"] = "enemy"
			break
		else:
			turn_number += 1
			if current_pokemon != last_pokemon:
				last_pokemon = current_pokemon
				ai_action_count = base_ai_action_count
			using_item = False
			copy_values(battle_state, BATTLE_MON, ai_base, ENEMY_BATTLE_MON, BATTLE_MON_SIZE - 1)
			copy_values(battle_state, ENEMY_BATTLE_MON, ai_base, BATTLE_MON, BATTLE_MON_SIZE - 1)

			copy_values(battle_state, PARTY_COUNT, ai_base, ENEMY_PARTY_COUNT, 1)
			copy_values(battle_state, DISABLED_MOVE, ai_base, ENEMY_DISABLED_MOVE, 1)

			copy_values(battle_state, ENEMY_PARTY_MON_LIST, ai_base, PARTY_MON_LIST, 7)
			copy_values(battle_state, ENEMY_PARTY_MONS, ai_base, PARTY_MONS, PARTY_STRUCT_SIZE * 6)
			copy_values(battle_state, PARTY_MON_LIST, ai_base, ENEMY_PARTY_MON_LIST, 7)
			copy_values(battle_state, PARTY_MONS, ai_base, ENEMY_PARTY_MONS, PARTY_STRUCT_SIZE * 6)

			set_value(ai_base, TRAINER_CLASS, [your_class["id"]], 1)
			set_value(ai_base, TRAINER_CLASS_WITHOUT_OFFSET, [your_class["id"] - 200], 1)

			set_value(ai_base, BATTLE_MON_SPEED, [0, 0], 2)
			set_value(ai_base, PLAYER_SELECTED_MOVE, [reverse_moves["COUNTER"]], 1)
			set_value(ai_base, ENEMY_ITEM_USED, [0], 1)
			set_value(ai_base, AI_ACTION_COUNT, [ai_action_count], 1)

			randomize_rdiv(ai_base, rng)

			write_file(out_save_path, ai_base)

			try:
				move_id, item_id, switch = get_ai_action(out_save_path)
			except subprocess.TimeoutExpired:
				battle_log["winner"] = "Draw by bgb timeout in AI move selection"
				break
			try:
				trainer_party_mon = [get_party_mon(battle_state, PARTY_MONS, i) for i in range(party_size)]
				enemy_party_mon = [get_party_mon(battle_state, ENEMY_PARTY_MONS, i) for i in range(enemy_party_size)]
			except StupidHack:
				# I apologize
				battle_log["winner"] = "enemy"
				break
			total_hp = sum(mon["hp"] for mon in [*trainer_party_mon, *enemy_party_mon])
			if total_hp < record_low_total_hp:
				record_low_total_hp = total_hp
				turns_without_damage = 0
			else:
				turns_without_damage += 1

			print(total_hp, record_low_total_hp, turns_without_damage)

			turn_summary = {
				"turn_number": turn_number,
				"move": moves[move_id],
				"item": items[item_id],
				"switched": switch,
				"trainer_battle_mon": {
					"species": get_string(battle_state, BATTLE_MON_NAME, POKEMON_NAME_LENGTH).strip("@"),
					"hp": get_hp(battle_state, BATTLE_MON_HP),
					"max_hp": get_hp(battle_state, BATTLE_MON_MAX_HP),
					"party_index": current_pokemon
				},
				"enemy_battle_mon": {
					"species": get_string(battle_state, ENEMY_BATTLE_MON_NAME, POKEMON_NAME_LENGTH).strip("@"),
					"hp": get_hp(battle_state, ENEMY_BATTLE_MON_HP),
					"max_hp": get_hp(battle_state, ENEMY_BATTLE_MON_MAX_HP),
					"party_index": get_value(battle_state, ENEMY_BATTLE_MON_PARTY_POS, 1)[0]
				},
				"trainer_party_mons": trainer_party_mon,
				"enemy_party_mons": enemy_party_mon
			}

			battle_log["turns"].append(turn_summary)
			pprint(turn_summary)

			if switch:
				button_sequence = select_switch()
			elif item_id:
				set_value(battle_state, BAG_ITEM_COUNT, [1], 1)
				set_value(battle_state, BAG_ITEMS, [item_id, 1, 0xFF], 3)
				ai_action_count = max(ai_action_count - 1, 0)

				using_item = True
				button_sequence = use_item()
			else:
				target_move_index = get_move_index(battle_state, move_id)
				current_move_index = get_value(battle_state, MOVE_LIST_INDEX, 1)[0]
				button_sequence = select_move(current_move_index, target_move_index)

		battle_mon_move_count = get_move_count(battle_state)
		set_value(battle_state, BATTLE_MON_PP, [0xff] * battle_mon_move_count, battle_mon_move_count)
		set_value(battle_state, GAIN_EXP_FLAG, [0], 1)

		write_file(battle_save_path, battle_state)
		write_file(out_demo_path, button_sequence)

	battle_log["turn_count"] = turn_number

	for file in [battle_save_path, out_save_path, out_demo_path, rom_image_path]:
		os.remove(file)

	output_dir = OUTPUT_BASE

	if save_movie:
		build_movie(movie_path, output_dir, run_number)

	if save_json:
		json_dir = f"{output_dir}/json/"
		output_json = f"{output_dir}/json/{run_number}.json"
		os.makedirs(json_dir, exist_ok=True)
		with open(output_json, 'w') as f:
			json.dump(battle_log, f, indent=2)

	os.rmdir(working_dir)

	return battle_log


def build_movie(movie_path, output_dir, run_number):
	movie_output_dir = f"{output_dir}/movies/"
	output_movie = f"{output_dir}/movies/{run_number}.mkv"
	os.makedirs(movie_output_dir, exist_ok=True)

	files = [f for f in os.listdir(movie_path)]
	files.sort()

	video_list_txt = f"{movie_path}/videos.txt"
	audio_list_txt = f"{movie_path}/audio.txt"

	create_concat_file(video_list_txt, [f for f in files if f.endswith(".avi")])
	create_concat_file(audio_list_txt, [f for f in files if f.endswith(".wav")])

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

	for f in [*files, "videos.txt", "audio.txt"]:
		os.remove(f"{movie_path}/{f}")
	os.rmdir(movie_path)


def create_concat_file(list_txt, files):
	with open(list_txt, 'w') as f:
		f.write("ffconcat version 1.0\n")
		f.write("\n".join(f"file '{f}'" for f in files))


def battle_until_win():
	while True:
		you = get_trainer_by_id(214, 9)
		enemy = get_trainer_by_id(214, 8)
		battle_log_winner = run_one_battle(enemy, you)
		print(battle_log_winner)
		if battle_log_winner == "trainer":
			break


def run_one_battle(enemy, you):
	your_class, your_instance = you
	enemy_class, enemy_instance = enemy
	run_number = str(uuid.uuid4())
	battle_log = battle_x_as_y(your_class, your_instance, enemy_class, enemy_instance,
	                           run_number=f"upset_attempts/{run_number}",
	                           save_movie=True)
	battle_log_winner = battle_log["winner"]
	return battle_log_winner

def get_rival_videos():
	for rival in range(1, 7):
		for i in range(5):
			your_class, your_instance = get_random_trainer()
			# your_class, your_instance = get_trainer_by_id(225, 2)
			# enemy_class, enemy_instance = get_random_trainer()
			enemy_class, enemy_instance = get_trainer_by_id(225, rival)

			run_number = str(uuid.uuid4())
			battle_log = battle_x_as_y(your_class, your_instance, enemy_class, enemy_instance,
			                           run_number=f"vidvals/{run_number}",
			                           save_movie=True)

def seed_testing():
	for _ in range(100):
		your_class, your_instance = get_random_trainer()
		enemy_class, enemy_instance = get_random_trainer()

		run_number = str(uuid.uuid4())

		battle_log = battle_x_as_y(your_class, your_instance, enemy_class, enemy_instance, run_number=run_number,
		                           save_movie=False, seed="test123")
		first_turn_count = battle_log["turn_count"]

		battle_log = battle_x_as_y(your_class, your_instance, enemy_class, enemy_instance, run_number=run_number + "_2",
		                           save_movie=False, seed="test123")
		second_turn_count = battle_log["turn_count"]

		if first_turn_count == second_turn_count:
			print("all is well!")
		else:
			print("Mismatch!")
			break

def run_from_hashid(hashid):
	your_class_id, your_instance_id, enemy_class_id, enemy_instance_id, hash_nonce = hash_encoder.decode(hashid)
	your_class, your_instance = get_trainer_by_id(your_class_id, your_instance_id)
	enemy_class, enemy_instance = get_trainer_by_id(enemy_class_id, enemy_instance_id)

	battle_nonce = str(uuid.uuid4())
	return battle_x_as_y(your_class, your_instance, enemy_class, enemy_instance, run_number=f"{hashid}_{battle_nonce}", save_movie=False, seed=hashid)

def test_hash_id():
	for _ in range(20):
		your_class, your_instance = get_random_trainer()
		enemy_class, enemy_instance = get_random_trainer()
		hash_nonce = random.randint(1, 10)

		your_class_id, your_instance_id = your_class["id"], your_instance["index"]
		enemy_class_id, enemy_instance_id = enemy_class["id"], enemy_instance["index"]

		hashid = hash_encoder.encode(your_class_id, your_instance_id, enemy_class_id, enemy_instance_id, hash_nonce)
		print("The hashid is", hashid)

		battle_nonce = str(uuid.uuid4())
		battle_log_1 = battle_x_as_y(your_class, your_instance, enemy_class, enemy_instance, run_number=f"{hashid}_{battle_nonce}", save_movie=False, seed=hashid)

		battle_log_2 = run_from_hashid(hashid)

		if battle_log_1["turn_count"] != battle_log_2["turn_count"]:
			print("They don't match!")


def main():
	your_class, your_instance = get_random_trainer()
	# your_class, your_instance = get_trainer_by_id(226, 3)
	enemy_class, enemy_instance = get_random_trainer()
	# enemy_class, enemy_instance = get_trainer_by_id(226, 3)

	run_number = str(uuid.uuid4())
	battle_log = battle_x_as_y(your_class, your_instance, enemy_class, enemy_instance, run_number=f"extra/{run_number}",
	                           save_movie=True)

	pprint(battle_log)


if __name__ == '__main__':
	# battle_until_win()
	# get_rival_videos()
	main()
	# test_hash_id()
	# seed_testing()