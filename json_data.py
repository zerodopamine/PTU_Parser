import json
import re
import os
import pdfplumber
handbook_path = '/home/josh/Downloads/Pokemon Tabletop United 1.05 Core.pdf'

'''Read the playerhand book for ability and move data'''
def parse_findall(output):
    '''Check if output exists, if not return N/A'''
    if output: output = output[0].replace('\n',' ').strip()
    else: output = 'N/A'
    return output

def pdf_ability_to_json():
    adata = {}
    abilities = [310,337]
    with pdfplumber.open(handbook_path) as pdf:
        for i in range(abilities[0], abilities[1]):
            page = pdf.pages[i]

            # Get the page width and height to determine column coordinates
            page_width = page.width
            page_height = page.height

            # Define bounding boxes for left and right columns (adjust these values as needed)
            left_bbox = (0, 0, page_width / 2, page_height)  # (x0, y0, x1, y1)
            right_bbox = (page_width / 2, 0, page_width, page_height)

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
    # Convert and write JSON object to file
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/abilities.json", "w") as outfile: 
        json.dump(adata, outfile)

def pdf_moves_to_json():
    moves = [345,436]
    adata = {}
    with pdfplumber.open(handbook_path) as pdf:
        for i in range(moves[0], moves[1]):
            page = pdf.pages[i]

            # Get the page width and height to determine column coordinates
            page_width = page.width
            page_height = page.height

            # Define bounding boxes for left and right columns (adjust these values as needed)
            left_bbox = (0, 0, page_width / 2, page_height)  # (x0, y0, x1, y1)
            right_bbox = (page_width / 2, 0, page_width, page_height)

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
            # Convert and write JSON object to file
            with open(f"{os.path.dirname(os.path.abspath(__file__))}/moves.json", "w") as outfile: 
                json.dump(adata, outfile)

if __name__ == '__main__':
    pdf_ability_to_json()
    pdf_moves_to_json()