from typing import List, Optional, Tuple


class Pokemon:
    def __init__(self, species: str, max_hp: int, level: int = 0):
        self.species = species
        self.max_hp = max_hp
        self.level = level


class Action(object):
    def __init__(self, move: str, item: str, switched: bool):
        self.switched = switched
        self.item = item
        self.move = move


class Turn:
    def __init__(self, index: int, action: Action, trainer_battle_mon_index: int, enemy_battle_mon_index: int,
                 trainer_party_mon_hps: List[int], enemy_party_mon_hps: List[int]):
        self.index = index
        self.action = action
        self.trainer_battle_mon_index = trainer_battle_mon_index
        self.enemy_battle_mon_index = enemy_battle_mon_index
        self.trainer_party_mon_hps = trainer_party_mon_hps
        self.enemy_party_mon_hps = enemy_party_mon_hps


class Battle:
    def __init__(self, original_path: str, player: "Trainer", enemy: "Trainer", winner: str, seed: str, turns: List[Turn]):
        self.original_path = original_path
        self.player = player
        self.enemy = enemy
        self.winner = winner
        self.turns = turns
        self.seed = seed
        if winner == "trainer":
            self.winning_trainer = player
            self.losing_trainer = enemy
        elif winner == "enemy":
            self.winning_trainer = enemy
            self.losing_trainer = player
        else:
            self.winning_trainer, self.losing_trainer = player, player


class Trainer:
    def __init__(self, class_id: int, instance_id: int, party_mons: List[Pokemon]):
        self.class_id: int = class_id
        self.instance_id: int = instance_id
        self.party_mons: List[Pokemon] = party_mons
        self.battles: List[Battle] = []
        self.elo: int = 1500
        self.lr_elo: Optional[int] = None

        from common_methods import get_trainer_by_id
        trainer_class, trainer_instance = get_trainer_by_id(class_id, instance_id)
        self.name = trainer_class["class"]
        self.identifier = f"{self.name} #{trainer_instance['index']}"
        self.location = trainer_instance['location']
        for index, pokemon in enumerate(self.party_mons):
            pokemon.level = trainer_instance['party'][index]['level']

        self.win_count: Optional[int] = None
        self.lose_count: Optional[int] = None
        self.draw_count: Optional[int] = None
        self.greatest_defeat: Optional[Trainer] = None
        self.greatest_victory: Optional[Trainer] = None
        self.tier: int = 0

    def add_battle(self, battle: Battle):
        self.battles.append(battle)

    def get_win_rate(self) -> Tuple[int, int, int]:
        if not hasattr(self, "win_count") or self.win_count is None:
            self.win_count, self.lose_count, self.draw_count = 0, 0, 0
            for battle in self.battles:
                if battle.winner == "trainer" and battle.player == self \
                        or battle.winner == "enemy" and battle.enemy == self:
                    self.win_count += 1
                elif "Draw" in battle.winner:
                    self.draw_count += 1
                else:
                    self.lose_count += 1

        return self.win_count, self.lose_count, self.draw_count

    def __eq__(self, other):
        return isinstance(other, Trainer) \
               and other.class_id == self.class_id \
               and other.instance_id == self.instance_id

    def __hash__(self):
        return hash(self.class_id * 100 + self.instance_id)
