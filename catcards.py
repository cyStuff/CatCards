import json
import random

weights = [1000,500,200,50,1]
lootbox_total = 6

f = open('data/catCards.json')
cats = json.loads(f.read())
f.close()
def get_cat_json(name):
	return cats[name]

def get_cat_names():
	return cats.keys()

def get_random():
	rarity = 0
	total = sum(weights)
	rand = random.randint(1, total)
	for n, i in enumerate(weights):
		rand -= i
		if rand <= 0:
			return n

def lootbox():
	return [random.choice([x for x in cats if cats[x]['rarity'] == rarity]) for rarity in [get_random() for _ in range(lootbox_total)]]