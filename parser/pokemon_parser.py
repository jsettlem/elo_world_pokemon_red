import json


def parse(file):
	trainer_classes = []
	current_class = {}
	current_class_id = 201
	current_location = ""
	current_class_index = 1
	for line in file:
		line = line.strip()
		if len(line) == 0:
			continue
		print(line)
		tokens = line.split()
		if line.endswith(":"):
			if current_class:
				if current_class["instances"]:
					trainer_classes.append(current_class)
				current_class_id += 1
				current_class_index = 1
			current_class = {"class": line[:-5], "id": current_class_id, "instances": []}
			current_location = ""
			print("New class: " + current_class["class"] + ", ID: " + str(current_class["id"]))
		elif tokens[0] == ";":
			current_location = " ".join(tokens[1:])
			print("New location: " + current_location)
		elif tokens[0] == "db":
			print("New trainer")
			current_class["instances"].append(parse_trainer(tokens[1], current_location, current_class_index))
			current_class_index += 1
	trainer_classes.append(current_class)
	return trainer_classes


def parse_trainer(line, location, index):
	trainer = {
		"location": location,
		"index": index,
		"party": []
	}

	tokens = line.split(",")
	print(tokens)
	if tokens[0] == "$FF":
		print("Multiple levels")
		tokens = tokens[1:-1]
		for index in range(0, len(tokens) // 2):
			pokemon = {
				"species": tokens[index * 2 + 1],
				"level": int(tokens[index * 2])
			}
			trainer["party"].append(pokemon)
	else:
		level = int(tokens[0])
		print("Same levels: " + str(level))
		for token in tokens[1:-1]:
			pokemon = {
				"species": token,
				"level": level
			}
			trainer["party"].append(pokemon)
	return trainer


with open("input", encoding="utf-8") as file, open("output.json", "w", encoding="utf-8") as outputFile:
	parsed = parse(file)
	json.dump(parsed, outputFile, indent=4, sort_keys=True)
