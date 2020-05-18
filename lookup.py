"""
Created on 16 May 2020
@author: John Thomas
"""
import json

ENTRY_TYPES = ["weapon", "armor", "matrix", "gear", "augmentation", "skill", "spell", "form", "sprite", "spirit", "streetpedia"]

def lookup_weapon(name):
    with open("data/weapons.json") as json_file:
        weapons = json.load(json_file)
        return weapons.get(name.lower())