python3 -m venv discordvenv
source discordvenv/bin/activate
pip install -r requirements.txt && playwright install chromium
export discordtoken=$1
python3 -m discord.bot
