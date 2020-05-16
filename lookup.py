import json

def lookup_weapon(name):

    with open("data/weapons.json") as json_file:
        weapons = json.load(json_file)
        for weapon in weapons:
            if name.lower() == weapon["name"].lower():
                print(weapon)
                return weapon
                
#lookup_weapon("Combat Axe")