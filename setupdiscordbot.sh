python3 venv discordvenv
source discordvenv/bin/activate
pip install -r requirements.txt && playwright install chromium
python3 -m discord.bot
