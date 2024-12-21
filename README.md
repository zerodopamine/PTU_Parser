# PTU_Parser
Parses the PTU pdf and clicks and adds info to roll20

1. Download chrome if you dont already have it
2. Launch chrome with debug: chrome.exe --remote-debugging-port=9222
3. Login to roll20
4. Set the pokemon and level in the read_pdf.py
5. Open a game with PTU character sheets, open one, and try importing data for a pokemon with the script

-don't touch anything while its running (ie don't be messaging people on discord, you will screw up the sheet)

-STAB boxes don't get ticked

-single use per scene moves don't have the uses filled in (probably because the book just says scene instead of scene 1 unlike other moves with limited use)

-sometimes page numbers get parsed (so you see things like underdog 207 or steady performance 412)

-if a move has a special listed at the bottom instead of going in the description box it goes in the contest section

-It will auto pick the 6 most recent moves or however many the pokemon can learn if there are less than 6 available
