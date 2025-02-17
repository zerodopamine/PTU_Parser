import json
import re
import os
import pdfplumber

'''Read the playerhand book for ability and move data'''
def parse_findall(output):
    '''Check if output exists, if not return N/A'''
    if output: output = output[0].replace('\n',' ').strip()
    else: output = 'N/A'
    return output

def save_json(data, file_name):
    file_path = f"{os.path.dirname(os.path.abspath(__file__))}/{file_name}.json"
    # Check if file exists, if it does append to it
    if os.path.isfile(file_path):
        with open(file_path, "r") as outfile: 
            current_data = json.load(outfile)
            current_data.update(data)
            data = dict(sorted(current_data.items()))

    # Convert and write JSON object to file
    with open(file_path, "w") as outfile: 
        json.dump(data, outfile)

def pdf_ability_to_json(load_path,pages):
    adata = {}
    with pdfplumber.open(load_path) as pdf:
        for i in range(pages[0], pages[1]):
            page = pdf.pages[i]

            # Get the page width and height to determine column coordinates
            page_width = page.width
            page_height = page.height

            # Define bounding boxes for left and right columns (adjust these values as needed)
            left_bbox = (0, 0, page_width / 2, page_height - 20)  # (x0, y0, x1, y1)
            right_bbox = (page_width / 2, 0, page_width, page_height - 20)

            # Extract text for left column
            left_text = page.within_bbox(left_bbox).extract_text()

            # Extract text for right column
            right_text = page.within_bbox(right_bbox).extract_text()

            data = f'{left_text}\n{right_text}'
            matches = re.findall(r"(Ability:\s.*?)(?=\nAbility:|\Z)", data, re.DOTALL)
            for match in matches:
                name = re.findall(r"Ability:(.*?)\n", match, re.DOTALL)[0]
                frequency = match.split('\n')[1]
                trigger = re.findall(r"Trigger:(.*?)Effect:", match, re.DOTALL)
                trigger = parse_findall(trigger)
                target = re.findall(r"Target:(.*?)Effect:", match, re.DOTALL)
                target = parse_findall(target)
                effect = re.findall(r"Effect:(.*?)\Z", match, re.DOTALL)
                effect = parse_findall(effect)
                adata[name] = {
                    'Frequency' : frequency,
                    'Trigger' : trigger,
                    'Target' : target,
                    'Effect' : effect
                }

    adata = dict(sorted(adata.items()))
    save_json(adata, "abilities")

def pdf_moves_to_json(load_path, pages):
    adata = {}
    with pdfplumber.open(load_path) as pdf:
        for i in range(pages[0], pages[1]):
            page = pdf.pages[i]

            # Get the page width and height to determine column coordinates
            page_width = page.width
            page_height = page.height

            # Define bounding boxes for left and right columns (adjust these values as needed)
            left_bbox = (0, 0, page_width / 2, page_height - 20)  # (x0, y0, x1, y1)
            right_bbox = (page_width / 2, 0, page_width, page_height - 20)

            # Extract text for left column
            left_text = page.within_bbox(left_bbox).extract_text()

            # Extract text for right column
            right_text = page.within_bbox(right_bbox).extract_text()

            data = f'{left_text}\n{right_text}'
            matches = re.findall(r"(Move:\s.*?)(?=\nMove:|\Z)", data, re.DOTALL)
            for match in matches:
                move    = re.findall(r"Move:(.*?)\n", match, re.DOTALL)
                move    = parse_findall(move)
                mtype   = re.findall(r"Type:(.*?)\n", match, re.DOTALL)
                mtype   = parse_findall(mtype)
                freq    = re.findall(r"Frequency:(.*?)\n", match, re.DOTALL)
                freq    = parse_findall(freq)
                ac      = re.findall(r"AC:(.*?)\n", match, re.DOTALL)
                ac      = parse_findall(ac)
                db      = re.findall(r"Damage Base(.*?):", match, re.DOTALL)
                db      = parse_findall(db)
                mclass  = re.findall(r"Class:(.*?)\n", match, re.DOTALL)
                mclass  = parse_findall(mclass)
                mrange  = re.findall(r"Range:(.*?)\n", match, re.DOTALL)
                mrange  = parse_findall(mrange)
                effect  = re.findall(r"Effect:(.*?)Contest Type:", match, re.DOTALL)
                effect  = parse_findall(effect)
                ctype   = re.findall(r"Contest Type:(.*?)\n", match, re.DOTALL)
                ctype   = parse_findall(ctype)
                ceffect = re.findall(r"Contest Effect:(.*?)\Z", match, re.DOTALL)
                ceffect = parse_findall(ceffect)
                adata[move] = {
                    'Type' : mtype,
                    'Frequency' : freq,
                    'AC' : ac,
                    'Damage Base' : db,
                    'Class' : mclass,
                    'Range' : mrange,
                    'Effect' : effect,
                    'Contest Type' : ctype,
                    'Contest Effect' : ceffect
                }
            adata = dict(sorted(adata.items()))
            save_json(adata, "moves")

if __name__ == '__main__':
    handbook_path = '/home/josh/Downloads/Pokemon_PDFs/'
    handbook_abilities = {
        'Arceus References.pdf' : (0,1),
        'SuMo References-1.pdf' : (0,5),
        'SwSh + Armor_Crown References.pdf' : (0,5),
        'Pokemon Tabletop United 1.05 Core.pdf' : (311,337)
    }
    handbook_moves = {
        'Arceus References.pdf' : (1,17),
        'SuMo References-1.pdf' : (7,23),
        'SwSh + Armor_Crown References.pdf' : (7,26),
        'Pokemon Tabletop United 1.05 Core.pdf' : (346,436)
    }
    # Update abilities json
    for handbook in handbook_abilities:
        book_path = os.path.join(handbook_path, handbook)
        pages = handbook_abilities[handbook]
        pdf_ability_to_json(book_path, pages)
    #Update move json
    for handbook in handbook_moves:
        book_path = os.path.join(handbook_path, handbook)
        pages = handbook_moves[handbook]
        pdf_moves_to_json(book_path, pages)