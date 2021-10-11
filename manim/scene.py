import os
import random
from itertools import chain

from manim import *

trainer_images = "Z:/Dropbox/elo-world/video/3d/textures/trainer_sprites/"

class TheEloScale(Scene):
	def construct(self):
		title = Text(r"The Elo scale", font_size=120)

		self.play(Write(title))
		self.wait()
		self.play(FadeOut(title))


class EloOpeningExample(Scene):
	def construct(self):
		winner = ImageMobject(trainer_images + "Spr_RG_Bug_Catcher.png", scale_to_resolution=3840)
		winner.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
		winner.shift(LEFT + UP)

		loser = ImageMobject(trainer_images + "Spr_RG_Blue_1.png", scale_to_resolution=3840)
		loser.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
		loser.shift(LEFT + DOWN)

		winner_elo = Text("Elo: 834").next_to(winner)
		loser_elo = Text("Elo: 625").next_to(loser)

		self.play(FadeIn(winner), FadeIn(loser))
		self.play(Write(winner_elo), Write(loser_elo))
		self.wait()

		combatant_group = Group(winner, loser, winner_elo, loser_elo)

		self.play(combatant_group.animate.shift(LEFT * 3.5))

		absolute_difference = MathTex(r"d &= \lvert 834 - 625 \rvert\\ &= 209").shift(RIGHT*2)
		self.play(Write(absolute_difference))
		self.wait()

		self.play(absolute_difference.animate.shift(UP * 2))

		p_win = MathTex(r"P_w &= \frac 1 {1 + 10^{-d/400}}\\ &= \frac 1 {1 + 10^{-209/400}}\\ &= 0.77").shift(RIGHT*2 + DOWN)

		self.play(Write(p_win), run_time=3)
		self.wait()

class EloPipeline(Scene):
	def construct(self):
		trainer_image_files = [trainer_images + img for img in os.listdir(trainer_images) if img.endswith(".png")][3:]
		random.shuffle(trainer_image_files)
		trainer_mobjects = []
		text_mobjects = []
		group_mobjects = []
		elo_values = []
		last_index = 7
		for i, img in enumerate(trainer_image_files[:8]):
			self.add_trainer(img, i, trainer_mobjects, text_mobjects, group_mobjects, elo_values)

		gary = ImageMobject(trainer_images + "Spr_RG_Blue_1.png", scale_to_resolution=3840)
		gary.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
		gary.shift(UP * 3)

		versus_text = Text("vs.")
		versus_text.shift((UP * 1.5))

		gary_elo = Variable(1000, Text("Elo"), num_decimal_places=1)
		gary_elo_value = 1000
		gary_elo.next_to(gary, LEFT)
		gary_elo_tracker = gary_elo.tracker

		self.play(
			AnimationGroup(*(FadeIn(t) for t in trainer_mobjects), lag_ratio=0.5, run_time=3),
			AnimationGroup(*(Write(t) for t in text_mobjects), lag_ratio=0.5, run_time=3),
			FadeIn(gary),
			Write(versus_text),
			Write(gary_elo)
		)
		self.wait()

		while(last_index < len(trainer_image_files) - 7):
			opponent_group = group_mobjects.pop(0)
			opponent_text = text_mobjects.pop(0)
			opponent_sprite = trainer_mobjects.pop(0)
			opponent_elo = elo_values.pop(0)

			winner = random.random() < (1 / (1 + 10 ** ((opponent_elo - gary_elo_value) / 400)))

			win_text = Text("Win", color=GREEN)
			lose_text = Text("Lose", color=RED)

			if winner:
				win_text.next_to(gary, RIGHT)
				lose_text.next_to(opponent_sprite, RIGHT)
			else:
				win_text.next_to(opponent_sprite, RIGHT)
				lose_text.next_to(gary, RIGHT)

			self.play(AnimationGroup(FadeIn(win_text, shift=UP), FadeIn(lose_text, shift=UP), lag_ratio=0.5, run_time=0.5))

			K = 32
			r1 = 10 ** (gary_elo_value / 400)
			r2 = 10 ** (opponent_elo / 400)
			e1 = r1 / (r1 + r2)
			elo_diff = K * (winner - e1)
			gary_elo_value += elo_diff

			elo_diff_text = DecimalNumber(elo_diff, color=RED if elo_diff < 0 else GREEN, include_sign=True)
			elo_diff_text.next_to(gary_elo, DOWN)

			self.play(FadeIn(elo_diff_text, shift=UP))

			self.play(
				FadeOut(win_text),
				FadeOut(lose_text),
				FadeOut(opponent_group, shift=RIGHT),
				FadeOut(elo_diff_text, shift=UP),
				gary_elo_tracker.animate.set_value(gary_elo_value)
			)

			last_index += 1

			self.add_trainer(trainer_image_files[last_index], 7, trainer_mobjects, text_mobjects, group_mobjects, elo_values)

			self.play(
				AnimationGroup(*(
					t.animate.shift(RIGHT * 1.2) for t in group_mobjects
				), lag_ratio=0.2, run_time=1),
				FadeIn(trainer_mobjects[-1]),
				Write(text_mobjects[-1])
			)

			self.wait()

	def add_trainer(self, img, i, trainer_mobjects, text_mobjects, group_mobjects, elo_values):
		trainer_image = ImageMobject(img, scale_to_resolution=3840)
		trainer_image.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
		trainer_image.shift(LEFT * i * 1.2)
		trainer_elo = random.randrange(500, 2000)
		elo_text = Text(f"Elo: {trainer_elo}")
		elo_text.rotate(-PI / 2)
		elo_text.next_to(trainer_image, DOWN)
		trainer_mobjects.append(trainer_image)
		text_mobjects.append(elo_text)
		group_mobjects.append(Group(trainer_image, elo_text))
		elo_values.append(trainer_elo)

	def get_tex(self, my_elo, other_elo, anchor):
		return MathTex(r" { 32 \over {10^{ {", my_elo, r" - ", other_elo, r" } \over 400 } + 1} } = ")\
			.scale(0.8)\
			.next_to(anchor, DOWN + LEFT / 2)\
			.shift(RIGHT * 0.5)


class EloUpdateFormula(Scene):
	def construct(self):
		formula = MathTex(r" \mathrm {elo_{winner}} \stackrel{+}{=} { {{K}} \over {10^{ { \mathrm {elo_{winner} }  - \mathrm { elo_{\mathrm loser} } } \over {{400}} } + 1} }")

		self.play(Write(formula, run_time=2))
		k_box = SurroundingRectangle(formula[1])
		four_box = SurroundingRectangle(formula[3])
		self.wait()
		self.play(Create(k_box))
		# self.play(TransformMatchingTex(formula, formula2))
		self.wait()
		self.play(ReplacementTransform(k_box, four_box))
		self.wait()
		self.play(Uncreate(four_box))
		self.wait()

from manim import *

class EpicycloidWithFormula(Scene):
	def construct(self):
		#First, display the formula for an epicycloid
		formula = MathTex("x","=","R","(","1","+","\\frac{1}{n}",")","t")
		formula.set_color_by_tex_to_color_map({"x":RED,"R":YELLOW,"t":GREEN})
		formula.scale(1.5)
		formula.shift(2*UP)
		self.play(Write(formula))
		self.wait()
		#Then, display the epicycloid
		epicycloid = ParametricFunction(
			lambda t: np.array([
				t*np.cos(PI/5)-t*np.sin(PI/5),
				t*np.sin(PI/5)+t*np.cos(PI/5),
				0
			]),color=RED,t_range=[-2, 2, 0.05],
			)
		epicycloid.shift(2*DOWN)
		self.play(Write(epicycloid))
		self.wait()
		#Then, display the formula for an epicycloid
		formula2 = MathTex("x","=","R","(","1","-","\\frac{1}{n}",")","t")
		formula2.set_color_by_tex_to_color_map({"x":RED,"R":YELLOW,"t":GREEN})
		formula2.scale(1.5)
		formula2.shift(2*UP)
		self.play(Transform(formula,formula2))
		self.wait()

class TheWordLogisticRegression(Scene):
	def construct(self):
		title = Text(r"Logistic Regression", font_size=90)
		self.play(Write(title))
		self.wait()
		self.play(FadeOut(title))

class DogsAndCats(Scene):
	def construct(self):
		dog_table = DecimalTable(
			[
				[5.9, 12.3, 6.1, 10.6],
				[1.2, 0.9, 1.1, 0.8]
			],
			row_labels=[
				MathTex(r"\iffalse green \fi s", r" = {snout}:{body}").set_color_by_tex("green", GREEN),
				MathTex(r"\iffalse yellow \fi h", r" = {height}:{length}").set_color_by_tex("yellow", YELLOW)
			]
		)
		self.play(dog_table.create(), run_time=3)
		self.wait()
		dog_formula = MathTex(
			r"p_{dog} = {1 \over {1 + 10^{-(", "c_0", "+", "c_1", r"\cdot",  "s", " + ", "c_2", r"\cdot ", "h", ")}}}"
		).set_color_by_tex("s", GREEN).set_color_by_tex("h", YELLOW)
		self.play(dog_table.animate.shift(UP).scale(0.7))
		dog_formula.shift(DOWN).scale(1.1)
		self.play(Write(dog_formula))
		self.wait()

		coef_boxes = [
			SurroundingRectangle(dog_formula[1], buff=0.1),
			SurroundingRectangle(dog_formula[3], buff=0.1),
			SurroundingRectangle(dog_formula[7], buff=0.1),
		]

		self.play(AnimationGroup(*(Create(b) for b in coef_boxes), lag_ratio=0.5))
		self.wait()

		self.play(AnimationGroup(*(Uncreate(b) for b in coef_boxes), lag_ratio=0.5))
		self.wait()

		box_1 = SurroundingRectangle(dog_formula[3], buff=0.1)
		box_2 = SurroundingRectangle(dog_formula[7], buff=0.1)

		self.play(Create(box_1))
		self.wait()

		self.play(ReplacementTransform(box_1, box_2))
		self.wait()

		self.play(Uncreate(box_2))
		self.wait()

class EloLogistic(Scene):
	def construct(self):
		elo_formula = MathTex(
			r"p_{win} = {1 \over {1 + 10^{-(", "c_0", "+",
			"c_1", r"\cdot", "{player}_1", " + ",
			"c_2", r"\cdot", "{player}_2", " + ",
			"c_3", r"\cdot", "{player}_3", " + ",
			"c_4", r"\cdot", "{player}_4", " + ",
			r"\ldots", " + ",
			"c_{391}", r"\cdot ", "{player}_{391}",
			")}}}"
		).set_color_by_tex("c_", YELLOW).scale(0.7)
		self.play(Write(elo_formula), run_time=3)
		self.wait()

		trainer_mobjects = []
		number_mobjects = [Integer(0) for _ in range(19)]
		trainer_image_files = [trainer_images + img for img in os.listdir(trainer_images) if img.endswith(".png")][3:]
		random.shuffle(trainer_image_files)
		for image in trainer_image_files[:19]:
			trainer_image = ImageMobject(image, scale_to_resolution=3840)
			trainer_image.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
			trainer_mobjects.append(trainer_image)

		trainer_group = Group(*trainer_mobjects, *number_mobjects)
		trainer_group.arrange_in_grid(2, 19, buff=(0, 0.15))
		trainer_group.shift(UP*1.5)

		line = Line((number_mobjects[0].get_corner(UP+LEFT) + trainer_mobjects[0].get_corner(DOWN+LEFT)) / 2,
		            (number_mobjects[-1].get_corner(UP+RIGHT) + trainer_mobjects[-1].get_corner(DOWN+RIGHT)) / 2,
		            stroke_width=1)

		trainer_table = Group(trainer_group, line).scale(0.7)

		self.play(elo_formula.animate.shift(DOWN))
		self.play(Create(line))
		self.add(trainer_table)
		self.play(AnimationGroup(
			*chain.from_iterable(zip(
				(Write(t) for t in number_mobjects),
				(FadeIn(t) for t in trainer_mobjects)
			)), lag_ratio=0.5
		), run_time=3)
		self.wait()

		box1 = SurroundingRectangle(Group(trainer_mobjects[6], number_mobjects[6]))
		box2 = SurroundingRectangle(Group(trainer_mobjects[13], number_mobjects[13]))

		self.play(AnimationGroup(
			Create(box1),
			number_mobjects[6].animate.set_value(1), lag_ratio=0.5)
		)

		self.play(AnimationGroup(
			Create(box2),
			number_mobjects[13].animate.set_value(-1), lag_ratio=0.5)
		)
		self.wait()

		self.play(Uncreate(box1), Uncreate(box2))

		self.wait()

		new_formula = MathTex(
			r"p_{win} = {1 \over {1 + 10^{-(", "c_0", "+",
			"c_1", r"\cdot", "0", " + ",
			"c_2", r"\cdot", "1", " + ",
			"c_3", r"\cdot", "0", " + ",
			"c_4", r"\cdot", "-1", " + ",
			r"\ldots", " + ",
			"c_{391}", r"\cdot ", "0",
			")}}}"
		).set_color_by_tex("c_", YELLOW).scale(0.7).shift(DOWN)

		self.play(TransformMatchingTex(elo_formula, new_formula))
		self.wait()

		even_newer_formula = MathTex(
			r"p_{win} = {1 \over {1 + 10^{-(", "c_0", "+",
			"c_2", r"\cdot", "1", " + ",
			"c_4", r"\cdot", "-1"
			")}}}"
		).set_color_by_tex("c_", YELLOW).scale(0.7).shift(DOWN)

		footnote = Text("*the first coefficient ends up representing a \"home field advantage\"")
		footnote.scale(0.4).shift(DOWN * 3)

		self.play(TransformMatchingTex(new_formula, even_newer_formula))
		self.wait()

		box3 = SurroundingRectangle(even_newer_formula[3])
		box4 = SurroundingRectangle(even_newer_formula[7])
		self.play(Create(box3), Create(box4))
		self.play(Write(footnote))
		self.wait()


class TheMathZone(Scene):
	def construct(self):
		title = Text("The Math Zone is brought to you by:").scale(1.2)
		self.play(Write(title), run_time=6)
		self.wait()
		self.play(title.animate.shift(UP*3))
		l1 = Text("- Nic Dobson (math)")
		l2 = Text("- The Manim Community community")
		l3 = Text("- Vincent Rubinetti (music)")
		l4 = Text("- Viewers like you")

		text_group = Group(l1, l2, l3, l4).arrange(direction=DOWN, aligned_edge=LEFT).shift(LEFT * 0.2).scale(0.75)

		self.play(AnimationGroup(
			*(Write(t) for t in text_group), lag_ratio=0.75
		), run_time=6)
		self.wait()
