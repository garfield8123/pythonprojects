# Python Projects

## Build docs
```shell
pip install -r requirements.txt && playwright install chromium
```

## run bot
```shell
python -m discord.bot
```

## Docker build
```shell
docker build --build-arg DISCORD_TOKEN="your_actual_bot_token_here" -t discord-bot .
docker run -d --name my-discord-bot discord-bot
```