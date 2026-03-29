import discord
import asyncio

from Currentemp.currenttemp import gettemperature
from dcodefr.cipheridentifier import identifycipher
from household_income.income import getincomedata 
from household_income.income import getincomekeys


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
        await message.channel.send(identifycipher(ciphertext))
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


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

#application ID: 1487685826984022087
#Public key: b00006a9a6d636edaedaee0ba3b2906be6f4abf8277a95ff2110ac20089c4789
#Token MTQ4NzY4NTgyNjk4NDAyMjA4Nw.GvZofe.nl4r9YbH52iQkIyPKtZrJ5e1YWo7oFMgRrG2MM
discordToken="MTQ4NzY4NTgyNjk4NDAyMjA4Nw.GvZofe.nl4r9YbH52iQkIyPKtZrJ5e1YWo7oFMgRrG2MM"
client.run(discordToken)