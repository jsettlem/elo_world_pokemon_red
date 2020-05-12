from common_methods import *
import numpy
from numpy import array, linspace
from sklearn.neighbors import KernelDensity
from matplotlib import pyplot
from scipy.signal import argrelextrema


def greatest_diffs_cluster(elo_list, cluster_count=14):
	boundaries = sorted(list(range(len(elo_list) - 1)), key=lambda i: elo_list[i + 1] - elo_list[i], reverse=True)
	return sorted([elo_list[b] for b in boundaries[:cluster_count]])


def kde_cluster(elo_list: List[int], K: int = 10):
	min_elo, max_elo = min(elo_list), max(elo_list)

	elo_array = array(elo_list).reshape(-1, 1)
	kde = KernelDensity(bandwidth=K).fit(elo_array)

	space = linspace(min_elo, max_elo, num=int(max_elo - min_elo) * 2)
	estimates = kde.score_samples(space.reshape(-1, 1))

	mins = argrelextrema(estimates, numpy.less)[0]

	pyplot.plot(space, estimates)
	pyplot.plot(space[mins], estimates[mins], 'ro')
	pyplot.title(f"K: {K}, mins: {len(mins)}")
	pyplot.show()

	return [space[k] for k in mins]


def update_elo(t1: Trainer, t2: Trainer, winner: str, K: int = 32):
	r1 = 10 ** (t1.elo / 400)
	r2 = 10 ** (t2.elo / 400)

	e1 = r1 / (r1 + r2)
	e2 = r2 / (r1 + r2)

	if winner == "trainer":
		s1, s2 = 1, 0
	elif winner == "enemy":
		s1, s2 = 0, 1
	else:
		s1, s2 = 0.5, 0.5

	t1.elo = t1.elo + K * (s1 - e1)
	t2.elo = t2.elo + K * (s2 - e2)


def main():
	trainer_dict, battle_dict = load_pickle("../omega.pickle")

	trainer_wins = enemy_wins = draws = 0
	battle_list = list(battle_dict.values())
	for battle in battle_list:
		if battle.winner == 'trainer':
			trainer_wins += 1
		elif battle.winner == 'enemy':
			enemy_wins += 1
		else:
			draws += 1
		if battle.player != battle.enemy:
			update_elo(battle.player, battle.enemy, battle.winner)

	print("Trainer wins:", trainer_wins, "enemy wins:", enemy_wins, "draws:", draws)
	battle_trainers = list(trainer_dict.values())
	battle_trainers.sort(key=lambda t: t.elo)

	elo_list = [t.elo for t in battle_trainers]
	kde_boundaries = kde_cluster(elo_list, K=28)
	greatest_diff_boundaries = greatest_diffs_cluster(elo_list, cluster_count=14)

	print(greatest_diff_boundaries)
	current_kde_tier = 0
	current_diff_tier = 0
	for trainer in battle_trainers:
		if current_kde_tier < len(kde_boundaries) and trainer.elo > kde_boundaries[current_kde_tier]:
			current_kde_tier += 1
		if current_diff_tier < len(greatest_diff_boundaries) and trainer.elo > greatest_diff_boundaries[current_diff_tier]:
			current_diff_tier += 1
		trainer.tier = current_kde_tier
		win_count, lose_count, draw_count = trainer.get_win_rate()
		print("\t".join(("trainer:", trainer.identifier, "win count:", str(win_count), "lose count:", str(lose_count),
		                 "draw count:", str(draw_count), "elo:", str(trainer.elo),
		                 "kde tier:", str(trainer.tier), "diff tier:", str(current_diff_tier))))

	return
	battle_list.sort(key=lambda b: b.losing_trainer.elo - b.winning_trainer.elo, reverse=True)
	for upset in battle_list[:100]:
		print("\t".join((upset.original_path, upset.winning_trainer.identifier, str(upset.winning_trainer.elo),
		                 upset.losing_trainer.identifier, str(upset.losing_trainer.elo),
		                 str(upset.losing_trainer.elo - upset.winning_trainer.elo))))


if __name__ == '__main__':
	main()
