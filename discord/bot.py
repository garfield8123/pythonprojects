import discord
import asyncio

from Currentemp.currenttemp import gettemperature
from dcodefr.cipheridentifier import identifycipher
from household_income.income import getincomedata 
from household_income.income import getincomekeys
from localimagebot.localimage import generateimage
from aiohttp import web
import os


intents = discord.Intents.default()
intents.message_content= True
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    #---- Checks if the message username is the same as the client username ----
    if message.author == client.user:
        return
    if message.content.startswith("temperature"):
        location = message.content.split(" ", 1)[1]
        await message.channel.send(gettemperature(location))
    if message.content.startswith("cipher"):
        ciphertext = message.content.split(" ", 1)[1]
        await message.channel.send(await identifycipher(ciphertext))
    if message.content.startswith("household"):
        numofhousehold = message.content.split(" ")[1]
        County = message.content.split(" ")[2:len(message.content.split(" "))]
        County = " ".join(County)
        await message.channel.send(getincomedata(numofhousehold, County))
    if message.content.startswith("householdkey"):
        numofhousehold = message.content.split(" ")[1]
        County = message.content.split(" ")[2:len(message.content.split(" "))]
        County = " ".join(County)
        await message.channel.send(getincomekeys(numofhousehold, County))
    if message.content.startswith("image"):
        text = message.content.split(" ")[1:len(message.content.split(" "))]
        text = " ".join(text)
        generateimage(text, "discord")
        with open("output.png", "rb") as f:
            picture = discord.File(f)
        await message.channel.send(file=picture)
localserver = False
if localserver:
    @client.event
    async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

    import os
    discordToken=os.environ.get("discordtoken")
    client.run(discordToken)
else:
    async def handle(request):
        return web.Response(text="Bot alive")

    async def start_webserver():
        app = web.Application()
        app.router.add_get("/", handle)
        runner = web.AppRunner(app)
        await runner.setup()
        port = int(os.environ.get("PORT", 8080))
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()

    @client.event
    async def on_ready():
        print(f"Logged in as {client.user}")

    async def main():
        await start_webserver()
        discordToken=os.environ.get("discordtoken")
        await client.start(discordToken)

    asyncio.run(main())