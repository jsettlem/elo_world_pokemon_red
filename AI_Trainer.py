'''
this is the code I briefly show in the video when I say
"it would be easy enough to implement in Python"

it doesn't actually run
'''

import random

THUNDERWAVE, REST, PSYCHIC, TACKLE = 0, 0, 0, 0


def mod1(t):
	print(t)
	pass


def mod2(t):
	print(t)
	pass


def mod3(t):
	print(t)
	pass


class AI_Trainer:
	action_count = 3
	move_modifications = (mod1, mod2, mod3)
	moves = [THUNDERWAVE, REST, PSYCHIC, TACKLE]
	current_hp = 123
	max_hp = 123

	def take_turn(self):
		selected_move = self.select_move()
		if self.action_count > 0:
			selected_action = self.select_action()
			if selected_action:
				self.take_action(selected_action)
				return
		self.take_move(selected_move)

	def select_move(self):
		move_priorities = [10] * len(self.moves)
		for mod in self.move_modifications:
			mod(self)
		max_priority = min(move_priorities)
		return random.choice(move for i, move in enumerate(self.moves) if move_priorities[i] == max_priority)

	def select_action(self):
		if self.action_count and self.current_hp < self.max_hp / 5 and random.random() < 0.5:
			return "SUPER_POTION"
		return "ATTACK"

	def take_action(self, selected_action):
		pass

	def take_move(self, selected_move):
		pass
