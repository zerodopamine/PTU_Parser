import json
import os
import re
import sys
import pdfplumber

# Import the file I wrote to control chrome
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from chromium import chromium

# Pokemon
pokemon = {
    "Name" : "Swinub",
    "Level" : 26,
}

# pdf location
pokedex_path = "/home/josh/Downloads/Pokedex 1.05.pdf"
abilities_path = '/home/josh/Downloads/PTU_Parser/abilities.json'
moves_path = '/home/josh/Downloads/PTU_Parser/moves.json'
index_path = "/home/josh/Downloads/PTU_Parser/index.txt"

def read_pokedex_pdf(chromium):

    # Load moves
    with open(moves_path, 'r') as opf:
        moves = json.load(opf)

    # Load abilities
    with open(abilities_path, 'r') as opf:
        abilities = json.load(opf)

    skill_to_attr = {
        'Athl' : 'attr_Athletics',
        'Acro' : 'attr_Acrobatics',
        'Combat' : 'attr_Combat',
        'Stealth' : 'attr_Stealth',
        'Percep' : 'attr_Perception',
        'Focus' : 'attr_Focus'
    }

    def read_pokedex_data(data):
        def parse_line_data(poke_dict, key, found):
            try: index = found.index(':')
            except ValueError: index = False
            found = found.replace(':','').strip()
            # Type is split by /
            if key == 'Type':
                typing = found.split('/')
                for value in typing:
                    poke_dict[key][0].append(value.strip())
            elif key == 'Weight':
                weight = found.replace(')','').split('(')
                for value in weight:
                    poke_dict[key][0].append(value.strip())
            elif 'Ability' in key:
                if index:
                    poke_dict['Abilities'][0].append(found[index:])
                else:
                    poke_dict['Abilities'][0].append(found)
            else:
                poke_dict[key][0] = found
            return poke_dict

        poke_dict = {
            'HP' : ['','attr_base_HP'],
            'Attack' : ['','attr_base_ATK'],
            'Defense' : ['','attr_base_DEF'],
            'Special Attack' : ['','attr_base_SPATK'],
            'Special Defense' : ['','attr_base_SPDEF'],
            'Speed' : ['','attr_base_SPEED'],
            'Type' : [[],['attr_type1','attr_type2']],
            'Basic Ability' : None,
            'Adv Ability' : None,
            'High Ability' : None,
            'Height' : ['','attr_height'],
            'Weight' : [[],['attr_weight','attr_weightClass']],
            'Capability List' : [[],[
                'attr_Overland',
                'attr_Swim',
                'attr_LJ',
                'attr_HJ',
                'attr_Power'
            ]],
            'Capability Extra' : ['','attr_notes'],
            'Skill List' : [[],[],[]], #Skill, roll, bonus
            'Move List' : [[],[],[
                'attr_mlName',
                'attr_mlType',
                'attr_mlFrequency',
                'attr_mlAC',
                'attr_mlDB',
                'attr_mlCat',
                'attr_mlRange',
                'attr_mlEffects',
                'attr_mlContestType',
                'attr_mlContestEffect'
            ]],
            'Abilities' : [[],[
                'attr_Ability_Name',
                'attr_Ability_Freq',
                'attr_Ability_Trigger',
                'attr_Ability_Target',
                'attr_Ability_Info'
            ]]
        }
        keys = list(poke_dict.keys())
        for key in keys:
            if key == 'Capability List': break
            found = re.findall(f'{key}(.*)\n', data)
            # Skip keys with no data
            if len(found) == 0: continue
            # Fix Physical atk/def so it doesnt grab special
            if key == 'Attack' or key == 'Defense': found = [found[0]]
            # If there is a single return value
            if len(found) == 1:
                poke_dict = parse_line_data(poke_dict, key, found[0])
            # If there are multiple instances of key (i.e abilities)
            else:
                for value in found:
                    poke_dict = parse_line_data(poke_dict, key, value)
        
        # Now we need to find the capability list
        match = re.search(r"Capability List(.*?)Skill List", data, re.DOTALL)
        if match:
            text = match.group(1).strip().replace('-\n','').replace('\n',' ').split(',')
            for i, value in enumerate(text):
                if i < 4: 
                    value = value.split(' ')[-1]
                    if '/' in value:
                        value = value.split('/')
                        poke_dict['Capability List'][0].append(value[0])
                        poke_dict['Capability List'][0].append(value[1])
                    else:
                        poke_dict['Capability List'][0].append(value)
                else:
                    # Dont save pg numbers to string
                    if value.strip().isdigit(): continue
                    poke_dict['Capability Extra'][0]+=f'{value.strip()},'
        
        # Now we need to find the Skill list
        match = re.search(r"Skill List(.*?)Move List", data, re.DOTALL)
        if match:
            text = match.group(1).strip().replace('-\n','').replace('\n',' ').split(',')
            for skill in text:
                skill = skill.strip().split(' ')
                if len(skill[0]) == 0: continue
                poke_dict['Skill List'][0].append(skill_to_attr[skill[0]])
                roll = skill[1].split('+')
                if len(roll) == 1: roll[0].split('-')
                roll[0] = roll[0].split('d')[0]
                if len(roll) == 1:
                    poke_dict['Skill List'][1].append(roll[0])
                    poke_dict['Skill List'][2].append(0)
                else:
                    poke_dict['Skill List'][1].append(roll[0])
                    poke_dict['Skill List'][2].append(roll[1])

        # Now we need to find the move list
        match = re.search(r"Level Up Move List(.*?)TM/HM Move List", data, re.DOTALL)
        if match:
            text = match.group(1).strip().replace('\n',',').split(',')
            for move in text:
                # Remove type
                dindex = move.rindex('-')
                move = move[:dindex]
                index = move.index(' ')
                # Seperate move name and level learned
                poke_dict['Move List'][0].append(move[index+1:].strip())
                poke_dict['Move List'][1].append(int(move[:index]))
        # Remove placeholder ability keys
        del poke_dict['Adv Ability'], poke_dict['Basic Ability'], poke_dict['High Ability']
        return poke_dict
    
    pokedex = {}
    with open(index_path, 'r') as opf:
        lines = opf.readlines()
    for line in lines:
        line = line.split()
        pokedex[line[0].lower()] = int(line[1])

    with pdfplumber.open(pokedex_path) as pdf:
        page = pdf.pages[pokedex[pokemon['Name'].lower()]]
        # Get the page width and height to determine column coordinates
        page_width = page.width
        page_height = page.height

        # Define bounding boxes for left and right columns (adjust these values as needed)
        left_bbox = (0, 0, page_width / 2, page_height)  # (x0, y0, x1, y1)
        right_bbox = ((page_width / 2) - 5, 0, page_width, page_height)

        # Extract text for left column
        left_text = page.within_bbox(left_bbox).extract_text()

        # Extract text for right column
        right_text = page.within_bbox(right_bbox).extract_text()

    # Merge str data and parse it
    data = f'{left_text}\n{right_text}'
    poke_dict = read_pokedex_data(data)
    # After we have parsed pokemon data fill the fields on roll20
    chromium.name = pokemon['Name']
    chromium.find_roll20()
    chromium.find_input("attr_character_name", pokemon['Name'])
    chromium.find_input("attr_species", pokemon['Name'])
    chromium.find_input("attr_level", pokemon['Level'])
    for key in poke_dict.keys():
        print(f'Starting: {key}')

        # Loop through moves
        if key == 'Move List': 
            values, levels, attr = poke_dict[key]
            below_target = [num for num in levels if num < pokemon['Level']][-6:]
            for level in below_target:
                index = levels.index(level)
                move = values[index]
                chromium.find_button('repeating_moves')
                parent = chromium.find_move_parent()
                chromium.search_parent(parent, attr[0], move)
                for si, skey in enumerate(moves[move]):
                    chromium.search_parent(parent, attr[si+1], moves[move][skey])
            continue

        # Loop through abilities
        if key == 'Abilities':
            values, attr = poke_dict[key]
            for value in values:
                chromium.find_button('repeating_abilities')
                parent = chromium.find_ability_parent()
                chromium.search_parent(parent, attr[0], value)
                for index, skey in enumerate(abilities[f' {value}']):
                    svalue = abilities[f' {value}'][skey]
                    chromium.search_parent(parent, attr[index+1], svalue)
                chromium.find_button('repeating_abilities')
            continue

        # Loop through the skill list
        if key == 'Skill List':
            attr, roll, bonus = poke_dict[key]
            for index, value in enumerate(attr):
                chromium.find_input(value, roll[index])
                chromium.find_input(f'{value}_bonus', bonus[index])
            continue
        value, attr = poke_dict[key]
        if key == 'Capability Extra':
            chromium.find_textarea(attr, value)
        if type(value) == str:
            chromium.find_input(attr, value)
            pass
        else:
            for index, subvalue in enumerate(value):
                chromium.find_input(attr[index], subvalue)

if __name__ == "__main__":
    # Import the selenium browser
    chromium = chromium()
    read_pokedex_pdf(chromium)
    chromium.close()