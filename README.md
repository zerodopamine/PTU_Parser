# PTU_Parser
Parses the PTU pdf and clicks and adds info to roll20

1. Change the directories found in the read_pdf.py
2. Download chrome if you dont already have it
4. Launch chrome with debug: chrome.exe --remote-debugging-port=9222
   - If chrome.exe is not recognized use: "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
   - On linux use: chromium --remote-debugging-port=9222 
6. Login to roll20
7. Set the pokemon and level in the read_pdf.py
8. Open a game with PTU character sheets, open one, and try running read_pdf.py, if it cant find a character sheet it should complain

-don't touch anything while its running (ie don't be messaging people on discord, you will screw up the sheet)

-if a move has a special listed at the bottom instead of going in the description box it goes in the contest section

-It will auto pick the 6 most recent moves or however many the pokemon can learn if there are less than 6 available
