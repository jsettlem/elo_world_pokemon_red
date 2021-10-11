import random

from hash_id_common import *

def main():
	trainer_list = [(trainer_class, trainer_instance) for trainer_class in trainers for trainer_instance in
	                trainer_class["instances"]]

	ids = [display_hashid(generate_hashid(t1, t2, 0)) for t1 in trainer_list for t2 in trainer_list]

	random.shuffle(ids)

	with open("battle_set_1.txt", 'w') as f:
		f.write("\n".join(ids))

if __name__ == '__main__':
	main()