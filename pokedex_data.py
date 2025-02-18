import json
import os
import pdfplumber

def pdf_to_name_index(pokemon_dict, book_path, pages, handbook):
    with pdfplumber.open(book_path) as pdf:
        for i in range(pages[0], pages[1]):
            page = pdf.pages[i]
            # Get the page width and height to determine column coordinates
            page_width = page.width
            page_height = page.height

            # Define bounding boxes for left and right columns (adjust these values as needed)
            left_bbox = (0, 0, page_width / 2, page_height)  # (x0, y0, x1, y1)

            # Extract text for left column
            left_text = page.within_bbox(left_bbox).extract_text()

            # Extract words on page, get first index, get text
            name = left_text.split("\n")[0].upper()
            pokemon_dict[name] = {"page_number":i,"handbook":handbook}
    return pokemon_dict

if __name__ == '__main__':
    handbook_path = "/home/josh/Downloads/Pokemon_PDFs/Dex"

    handbook_dexes = {
            'AlolaDex.pdf' : (3,117),
            'GalarDex + Armor_Crown.pdf' : (2,120),
            'HisuiDex.pdf' : (3,30),
            'Pokedex 1.05.pdf' : (11,745)
        }
    
    pokemon_index = {}

    for handbook in handbook_dexes:
        book_path = os.path.join(handbook_path, handbook)
        pages = handbook_dexes[handbook]
        pokemon_index = pdf_to_name_index(pokemon_index, book_path, pages, handbook)
    
    # Convert and write JSON object to file
    file_path = f"{os.path.dirname(os.path.abspath(__file__))}/pokedex.json"
    with open(file_path, "w") as outfile: 
        json.dump(pokemon_index, outfile)