# Use the following commands to open the browser before you run the code
# Linux Command: chromium --remote-debugging-port=9222 
# Windows Command: "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# Pokemon
pokemon = {
    "Name" : "Victreebel",
    "Level" : 58,
}
# If you want the pokemon to have all moves and not just six, set True otherwise False
all_moves = False

# pokedex pdf location
pokedex_path = r"P:\Pokemon\PTU 1.05"

def read_pokedex_pdf(chromium):

    # Load moves
    with open(f'{script_path}/moves.json', 'r') as opf:
        moves = json.load(opf)

    # Load abilities
    with open(f'{script_path}/abilities.json', 'r') as opf:
        abilities = json.load(opf)

    # Load page numbers for pokemon
    with open(f'{script_path}/pokedex.json', 'r') as opf:
        indices = json.load(opf)

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
                    poke_dict['Ability'][0].append(found[index:])
                else:
                    poke_dict['Ability'][0].append(found)
            else:
                poke_dict[key][0] = found
            return poke_dict

        poke_dict = {
            'Name' : [pokemon['Name'],"attr_character_name"],
            'Species' : [pokemon['Name'], "attr_species"],
            'Level' : [pokemon['Level'],"attr_level"],
            'Type' : [[],['attr_type1','attr_type2']],
            'Height' : ['','attr_height'],
            'Weight' : [[],['attr_weight','attr_weightClass']],
            'HP' : ['','attr_base_HP'],
            'Attack' : ['','attr_base_ATK'],
            'Defense' : ['','attr_base_DEF'],
            'Special Attack' : ['','attr_base_SPATK'],
            'Special Defense' : ['','attr_base_SPDEF'],
            'Speed' : ['','attr_base_SPEED'],
            'Ability' : [[],[
                ['attr_Ability_Name','input', None],
                ['attr_Ability_Freq','input', 'Frequency'],
                ['attr_Ability_Trigger','input', 'Trigger'],
                ['attr_Ability_Target','input', 'Target'],
                ['attr_Ability_Info','textarea', 'Effect']
            ]],
            'Capability List' : [[],[]], #Value, attribute
            'Skill List' : [[],[],[]], #Skill, roll, bonus
            # Name, Level, [Attribute, Attribute Type, Key]
            'Move List' : [[],[],
                [['attr_mlName','input', None],
                ['attr_mlFrequency','select', "Frequency"],
                ['attr_mlUses', 'input', "Frequency"],
                ['attr_mlCat','select', "Class"],
                ['attr_mlType', 'select', "Type"],
                ['attr_mlRange','input', "Range"],
                ['attr_mlContestType', 'select', "Contest Type"],
                ['attr_mlAC','input', "AC"],
                ['attr_mlContestEffect', 'input', "Contest Effect"],
                ['attr_mlDB','input', "Damage Base"],
                ['attr_mlEffects', 'textarea', "Effect"]],
            ]
        }

        keys = list(poke_dict.keys())
        for key in keys[3:]:
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
        # Attribute to apply to each string
        attrs = {
            'Overland' : 'attr_Overland',
            'Swim'     : 'attr_Swim',
            'Long'     : 'attr_LJ',
            'High'     : 'attr_HJ',
            'Power'    : 'attr_Power'
            }
        if match:
            s = match.group(1).strip().replace('-\n','').replace('\n',' ')
            # Regular expression to capture "String Int" and "Jump X/Y" formats
            pattern = r'([A-Za-z]+(?:\s[A-Za-z]+)*)\s(\d+(/\d+)?)'
            
            extra_parts = s  # Start with full string and remove matches

            # Extract matches using regex
            matches = re.findall(pattern, s)
            for match in matches:
                key = match[0]  # Capability type
                # Add the attr key to the list to know where to put value
                if key in attrs: 
                    poke_dict['Capability List'][1].append(attrs[key])
                elif key == "Jump":
                    poke_dict['Capability List'][1].append(attrs["Long"])
                    poke_dict['Capability List'][1].append(attrs["High"])
                else:
                    poke_dict['Capability List'][1].append(key)

                value = match[1]  # Value (handles "X/Y" case for Jump)

                if '/' not in value:
                    poke_dict['Capability List'][0].append(value)
                else:
                    poke_dict['Capability List'][0].append(value.split("/")[0])
                    poke_dict['Capability List'][0].append(value.split("/")[1])

                # Remove matched part from extra_parts
                extra_parts = extra_parts.replace(f"{key} {value}", "").strip(", ")

            # Remaining parts are considered "Extra Capabilities"
            if extra_parts:
                poke_dict['Capability List'][0].append(extra_parts.strip(", "))
                poke_dict['Capability List'][1].append('attr_notes')
        
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
        if not match: 
            match = re.search(r"Level Up Move List(.*?)TM Move List", data, re.DOTALL)
        if not match: 
            match = re.search(r"Level Up Move List(.*?)Tutor Move List", data, re.DOTALL)
        if match:
            text = match.group(1).strip().replace('\n',',').split(',')
            for move in text:
                # Remove type
                dindex = move.rindex('-')
                move = move[:dindex]
                index = move.index(' ')
                # Seperate Name and level learned
                poke_dict['Move List'][0].append(move[index+1:].strip())
                try: poke_dict['Move List'][1].append(int(move[:index]))
                except ValueError: poke_dict['Move List'][1].append(pokemon["Level"])
        return poke_dict
    
    pokemon_info = indices[pokemon["Name"].strip().upper()]
    book_path = os.path.join(pokedex_path, pokemon_info["handbook"])
    book_page = pokemon_info["page_number"]

    with pdfplumber.open(book_path) as pdf:
        page = pdf.pages[book_page]
        # Get the page width and height to determine column coordinates
        page_width = page.width
        page_height = page.height - 25 # Chop off bottom of page to remove page numbers

        # Define bounding boxes for left and right columns (adjust these values as needed)
        left_bbox = (0, 0, page_width / 2, page_height)  # (x0, y0, x1, y1)
        right_bbox = ((page_width / 2) - 5, 0, page_width, page_height)

        # Extract text for left column
        left_text = page.within_bbox(left_bbox).extract_text()

        # Extract text for right column
        right_text = page.within_bbox(right_bbox).extract_text()

    # Merge str data and parse it
    data = f'{left_text}\n{right_text}'
    # Remove mega evolution data
    data = data[:data.find("Mega Evolution")]
    poke_dict = read_pokedex_data(data)

    # After we have parsed pokemon data fill the fields on roll20
    chromium.find_roll20()
    for key in poke_dict.keys():
        # Loop through moves
        if key == 'Move List': 
            values, levels, attr = poke_dict[key]
            # Sort by level to account for evolution moves
            values = [x for _, x in sorted(zip(levels, values))]
            levels = sorted(levels)
            # Check how many moves the pokemon should have
            if not all_moves:
                below_target = [i for i in range(len(levels)) if levels[i] <= pokemon['Level']][-6:]
            else:
                below_target = [i for i in range(len(levels))]
            for index in below_target:
                move = values[index]
                # Check if the move is in the json
                if move not in moves.keys():
                    print(f"Unknown move {move} found on {pokemon["Name"]}")
                    continue
                # Add new blank move to sheet
                parent = chromium.add_new_item("repeating_moves")
                # Loop through the attributes of the move
                for params in attr:
                    # If name, no need to access move dict
                    if params[0] == 'attr_mlName':
                        # Parent item, attribute type, attribute name, input
                        chromium.edit_item_element(parent,params[1], params[0], move)
                    elif params[0] == 'attr_mlUses':
                        # Get the data from the move dict using the provided key
                        input_data = moves[move][params[2]].split(" ")
                        if len(input_data) == 1:
                            chromium.edit_item_element(parent,params[1], params[0], 1)
                        else:
                            input_data = input_data[-1].replace("x","").strip()
                            chromium.edit_item_element(parent,params[1], params[0], input_data)
                    else:
                        # Get the data from the move dict using the provided key
                        input_data = moves[move][params[2]]
                        chromium.edit_item_element(parent,params[1], params[0], input_data)
                        # Check to see if the move is stab
                        if params[0] == "attr_mlType" and input_data in poke_dict["Type"][0]:
                            chromium.edit_item_element(parent,"checkbox","attr_mlStab","True")
                        # Check to see if move text specifies a critical hit value
                        if params[0] == "attr_mlEffects" and "Critical Hit on" in input_data:
                            match = re.search(r"Critical Hit on (\d+)", input_data)
                            if match:
                                chromium.edit_item_element(parent,"input","attr_mlCrit",int(match.group(1)))

        # Loop through abilities
        elif key == 'Ability':
            values, attr = poke_dict[key]
            for value in values:
                if f' {value}' not in abilities:
                    print(f'The following ability ({value}) not found!')
                    continue
                parent = chromium.add_new_item("repeating_abilities")
                for params in attr:
                    # If it is the ability name pass the ability key
                    if params[0] == 'attr_Ability_Name':
                        chromium.edit_item_element(parent, params[1], params[0], value)
                    # Else use the provided dict key to fetch data
                    else:
                        svalue = abilities[f' {value}'][params[2]]
                        chromium.edit_item_element(parent, params[1], params[0], svalue)

        elif key == 'Capability List':
            values, attrs = poke_dict[key]
            for index, attr in enumerate(attrs):
                if "attr_" in attr and "notes" not in attr:
                    chromium.find_input(attr,values[index])
                elif "attr_" in attr and "notes" in attr:
                    chromium.find_textarea(attr,values[index])
                else:
                    parent = chromium.add_new_item("repeating_capabilities")
                    chromium.edit_item_element(parent, "input", "attr_Capability", attr)
                    chromium.edit_item_element(parent, "input", "attr_Capability_Rank", values[index])

        # Loop through the skill list
        elif key == 'Skill List':
            attr, roll, bonus = poke_dict[key]
            for index, value in enumerate(attr):
                chromium.find_input(value, roll[index])
                chromium.find_input(f'{value}_bonus', bonus[index])

        # For single input fields
        else:
            value, attr = poke_dict[key]
            if attr in ["attr_notes"]:
                chromium.find_textarea(attr, value)
                continue
            if type(value) == str:
                chromium.find_input(attr, value)
            elif type(value) == int:
                chromium.find_input(attr, value)
            else:
                for index, subvalue in enumerate(value):
                    chromium.find_input(attr[index], subvalue)

if __name__ == "__main__":
    import json
    import os
    import re
    import sys
    import pdfplumber

    # Import the file I wrote to control chrome
    script_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(script_path)
    from chromium import chromium

    # Import the selenium browser
    chromium = chromium()
    read_pokedex_pdf(chromium)
    chromium.close()