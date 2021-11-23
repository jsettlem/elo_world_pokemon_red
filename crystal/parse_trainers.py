from pprint import pprint

class_names = [
	"LEADER", "LEADER", "LEADER", "LEADER", "LEADER", "LEADER", "LEADER", "LEADER", "RIVAL", "#MON PROF.", "ELITE FOUR",
	"PKMN TRAINER", "ELITE FOUR", "ELITE FOUR", "ELITE FOUR", "CHAMPION", "LEADER", "LEADER", "LEADER", "SCIENTIST",
	"LEADER", "YOUNGSTER", "SCHOOLBOY", "BIRD KEEPER", "LASS", "LEADER", "COOLTRAINER", "COOLTRAINER", "BEAUTY",
	"#MANIAC", "ROCKET", "GENTLEMAN", "SKIER", "TEACHER", "LEADER", "BUG CATCHER", "FISHER", "SWIMMER♂", "SWIMMER♀",
	"SAILOR", "SUPER NERD", "RIVAL", "GUITARIST", "HIKER", "BIKER", "LEADER", "BURGLAR", "FIREBREATHER", "JUGGLER",
	"BLACKBELT", "ROCKET", "PSYCHIC", "PICNICKER", "CAMPER", "ROCKET", "SAGE", "MEDIUM", "BOARDER", "#FAN",
	"KIMONO GIRL", "TWINS", "POKéFAN", "PKMN TRAINER", "LEADER", "OFFICER", "ROCKET", "MYSTICALMAN"
]

class_dvs = [[9, 10, 7, 7], [8, 8, 8, 8], [9, 8, 8, 8], [9, 8, 8, 8], [9, 8, 8, 8], [9, 8, 8, 8], [9, 8, 8, 8],
             [7, 12, 13, 13], [13, 13, 13, 13], [9, 8, 8, 8], [13, 12, 13, 13], [13, 12, 13, 13], [13, 12, 13, 13],
             [7, 15, 13, 15], [13, 12, 13, 13], [13, 12, 13, 13], [9, 8, 8, 8], [7, 8, 8, 8], [9, 8, 8, 8],
             [9, 8, 8, 8], [7, 8, 8, 8], [9, 8, 8, 8], [9, 8, 8, 8], [9, 8, 8, 8], [5, 8, 8, 8], [9, 8, 8, 8],
             [13, 8, 12, 8], [7, 12, 12, 8], [6, 9, 12, 8], [9, 8, 8, 8], [13, 8, 10, 8], [9, 8, 8, 8], [9, 8, 8, 8],
             [6, 8, 8, 8], [7, 13, 8, 7], [9, 8, 8, 8], [9, 8, 8, 8], [9, 8, 8, 8], [7, 8, 8, 8], [9, 8, 8, 8],
             [9, 8, 8, 8], [9, 8, 8, 8], [9, 8, 8, 8], [10, 8, 8, 8], [9, 8, 8, 8], [9, 8, 8, 8], [9, 8, 8, 8],
             [9, 8, 8, 8], [9, 8, 8, 8], [9, 8, 8, 8], [13, 8, 10, 8], [9, 8, 8, 8], [6, 10, 10, 8], [9, 8, 8, 8],
             [7, 14, 10, 8], [9, 8, 8, 8], [7, 8, 8, 8], [9, 8, 8, 8], [9, 8, 8, 8], [6, 8, 8, 10], [6, 8, 10, 8],
             [6, 13, 8, 8], [15, 13, 13, 14], [9, 13, 13, 13], [9, 8, 8, 8], [7, 14, 10, 8], [9, 8, 8, 8]]

class_genders = ["MALE", "FEMALE", "FEMALE", "MALE", "MALE", "FEMALE", "MALE", "FEMALE", "MALE", "MALE", "FEMALE",
                 "MALE", "MALE", "FEMALE", "MALE", "MALE", "MALE", "FEMALE", "MALE", "MALE", "FEMALE", "MALE", "MALE",
                 "MALE", "FEMALE", "FEMALE", "MALE", "FEMALE", "FEMALE", "MALE", "MALE", "MALE", "FEMALE", "FEMALE",
                 "FEMALE", "MALE", "MALE", "MALE", "FEMALE", "MALE", "MALE", "MALE", "MALE", "MALE", "MALE", "MALE",
                 "MALE", "MALE", "MALE", "MALE", "MALE", "MALE", "FEMALE", "MALE", "FEMALE", "MALE", "FEMALE", "MALE",
                 "MALE", "FEMALE", "FEMALE", "FEMALE", "MALE", "MALE", "MALE", "FEMALE", "ENBY"]

class_attributes = [

]

with open("class_attributes.txt", 'r') as f:
	clines = f.readlines()

i = 0
while i < len(clines):
	class_attribute = {
		"items": [],
		"techniques": [],
		"switch_style": ""
	}
	i += 1
	items = clines[i].partition(";")[0].strip().split()[1:]
	for item in items:
		item_name = item.strip().strip(",")
		if item_name != "NO_ITEM":
			class_attribute["items"].append(item_name)
	i += 1
	i += 1
	techniques = clines[i].strip().replace("|", "").split()[1:]
	for technique in techniques:
		technique_name = technique.strip()
		class_attribute["techniques"].append(technique_name)

	i += 1
	switch_style = clines[i].strip().split()[-1]
	class_attribute["switch_style"] = switch_style
	i += 1
	i += 1
	class_attributes.append(class_attribute)

with open("trainer_data.txt", 'r') as f:
	lines = f.readlines()

current_class_index = -1
current_instance_index = 0
current_trainer = {}
current_trainer_type = ""
trainers = []

for line in lines:
	if "Group:" in line:
		current_class_index += 1
		current_instance_index = 0
	elif line.strip().startswith("db"):
		parsed_line = line.strip()[2:].partition(";")[0].split(",")
		if parsed_line[0].strip().strip("-").isnumeric():
			level = int(parsed_line[0])
			if level == -1:
				trainers.append(current_trainer)
			else:
				species = parsed_line[1].strip()
				pokemon = {
					"species": species,
					"level": level
				}
				match current_trainer_type:
					case "NORMAL":
						pass
					case "MOVES":
						pokemon["moves"] = [m.strip() for m in parsed_line[2:] if m.strip() != "NO_MOVE"]
					case "ITEM":
						item = parsed_line[2].strip()
						if item != "NO_ITEM":
							pokemon["item"] = item
					case "ITEM_MOVES":
						item = parsed_line[2].strip()
						if item != "NO_ITEM":
							pokemon["item"] = item
						pokemon["moves"] = [m.strip() for m in parsed_line[3:] if m.strip() != "NO_MOVE"]
				current_trainer["pokemon"].append(pokemon)
		else:
			current_instance_index += 1
			parsed_line = line.strip()[2:].partition(";")[0].split(",")
			current_trainer_type = parsed_line[1].strip().removeprefix("TRAINERTYPE_")
			current_trainer = {
				"title": class_names[current_class_index],
				"name": parsed_line[0].strip().strip("\"").rstrip("@"),
				"pokemon": [],
				"class": current_class_index + 1,
				"instance": current_instance_index,
				"items": class_attributes[current_class_index]["items"],
				"techniques": class_attributes[current_class_index]["techniques"],
				"switch_style": class_attributes[current_class_index]["switch_style"],
				"dvs": class_dvs[current_class_index],
				"gender": class_genders[current_class_index]
			}
			rematch_count = 1 + len([t for t in trainers if
			                         t["name"] == current_trainer["name"] and t["title"] == current_trainer["title"]])
			if rematch_count > 1:
				current_trainer["rematch"] = rematch_count

pprint(trainers)
