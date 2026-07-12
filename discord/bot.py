import discord
import asyncio

from Currentemp.currenttemp import gettemperature
from dcodefr.cipheridentifier import identifycipher
from household_income.income import getincomedata 
from household_income.income import getincomekeys
from localimagebot.localimage import generateimage
from housefind.redfin import redfincityjson
from housefind.redfin import findcityInfo
from gemenichat.localchat import GemmaAnalyzer
from aiohttp import web
import os


intents = discord.Intents.default()
intents.message_content= True
client = discord.Client(intents=intents)

analyzer = GemmaAnalyzer(discord=True)

@client.event
async def on_message(message):
    # Prevent bot from responding to itself
    if message.author == client.user:
        return

    # Process message content safely
    content = message.content.strip()
    parts = content.split(" ")
    command = parts[0]
    # ---- 0. Help Command ----
    if command == "help":
        embed = discord.Embed(
            title="🤖 Bot Command Directory",
            description="Here is a list of available commands and how to use them:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🌡️ Weather & Temperature",
            value="`temperature [location]`\nChecks if you should open/close windows.\n*Example:* `temperature Grass Valley`",
            inline=False
        )
        embed.add_field(
            name="🕵️ Cipher Identifier",
            value="`cipher [ciphertext]`\nAnalyzes and identifies unknown encrypted strings.\n*Example:* `cipher U3VwcmlzZQ==`",
            inline=False
        )
        embed.add_field(
            name="💰 CA Household Income Data",
            value="`household [size] [county]`\n`householdkey [size] [county]`\nFetches California HCD income brackets.\n*Example:* `household 4 Santa Cruz`",
            inline=False
        )
        embed.add_field(
            name="🎨 AI Image Generation",
            value="`image [prompt]`\nGenerates an image from your text description.\n*Example:* `image a retro futuristic kitchen`",
            inline=False
        )
        embed.add_field(
            name="🏠 Redfin Real Estate Analytics",
            value="`redfinaverage [bedrooms] [city]`\n`redfintable`\n`redfinkey`\nAnalyzes local listings and gives market metrics.\n*Example:* `redfinaverage 2 Grass Valley`",
            inline=False
        )
        embed.add_field(
            name="🧠 Gemma 4 Multi-Turn Chat",
            value="`!chat [your message]`\nTalk to Gemma 4. It remembers previous turns!\n`!clearchat`\nResets the conversation history.",
            inline=False
        )
        embed.add_field(
            name="💻 Static Code Analysis",
            value="`!analyze [code snippet]`\nRuns deep reasoning static analysis to find bugs and vulnerabilities.",
            inline=False
        )
        
        embed.set_footer(text="Tip: Make sure to check your spelling and provide all parameters!")
        await message.channel.send(embed=embed)
    # ---- NEW COMMAND: Multi-turn Chat ----
    elif command == "!chat":
        if len(parts) < 2:
            return await message.channel.send("Please provide a prompt. Example: `!chat Tell me a joke.`")
        
        user_prompt = content.split(" ", 1)[1]
        
        # Alert the user that the model is processing on CPU
        async with message.channel.typing():
            # Crucial: Run in a separate thread so it doesn't freeze the entire Discord bot
            reply = await asyncio.to_thread(analyzer.chat_turn, user_prompt)
        
        # Send response (Discord has a 2000 character limit, Gemma outputs are typically safe)
        await message.channel.send(reply[:2000])

    # ---- NEW COMMAND: Clear Chat History ----
    elif command == "!clearchat":
        analyzer.clear_history()
        await message.channel.send("🧹 Gemma chat history has been successfully reset!")

    # ---- NEW COMMAND: Static Code Analysis ----
    elif command == "!analyze":
        code_snippet = ""
        
        # Check if the user attached a file instead of raw text
        if message.attachments:
            async with message.channel.typing():
                attachment = message.attachments[0]
                # Read file directly into string memory
                file_bytes = await attachment.read()
                code_snippet = file_bytes.decode("utf-8")
        elif len(parts) >= 2:
            # Strip code block markdown ticks if the user wrapped their snippet in them
            code_snippet = content.split(" ", 1)[1].strip("`").strip("python").strip("js")
        else:
            return await message.channel.send("Usage: `!analyze [code snippet]` OR upload a code file with `!analyze` in the comment.")

        async with message.channel.typing():
            # Pass snippet through reasoning analyzer in a non-blocking background thread
            analysis_result = await asyncio.to_thread(analyzer.analyze_code, code_snippet=code_snippet)
        
        # If the result is longer than 2000 characters, Discord will reject it. 
        # Break it up or write it out to a file if it exceeds limits.
        if len(analysis_result) > 2000:
            with open("analysis_report.md", "w", encoding="utf-8") as f:
                f.write(analysis_result)
            with open("analysis_report.md", "rb") as f:
                await message.channel.send(content="📄 Analysis report exceeded character limits. Here is the full markdown report file:", file=discord.File(f))
            os.remove("analysis_report.md")
        else:
            await message.channel.send(analysis_result)
    # ---- 1. Temperature Command ----
    elif command == "temperature":
        if len(parts) < 2:
            return await message.channel.send("Please provide a location. Example: `temperature New York`")
        location = content.split(" ", 1)[1]
        temperature = gettemperature(location)
        await message.channel.send(temperature)

    # ---- 2. Cipher Command ----
    elif command == "cipher":
        if len(parts) < 2:
            return await message.channel.send("Please provide text to decipher.")
        ciphertext = content.split(" ", 1)[1]
        result = await identifycipher(ciphertext)
        await message.channel.send(result)

    # ---- 3. Household Command ----
    elif command == "household":
        if len(parts) < 3:
            return await message.channel.send("Usage: `household [num] [County Name]`")
        numofhousehold = parts[1]
        county = " ".join(parts[2:])
        await message.channel.send(getincomedata(numofhousehold, county))

    # ---- 4. Household Key Command ----
    elif command == "householdkey":
        if len(parts) < 3:
            return await message.channel.send("Usage: `householdkey [num] [County Name]`")
        numofhousehold = parts[1]
        county = " ".join(parts[2:])
        await message.channel.send(getincomekeys(numofhousehold, county))

    # ---- 5. Image Generation Command ----
    elif command == "image":
        if len(parts) < 2:
            return await message.channel.send("Please provide a prompt. Example: `image a cool cat`")
        text = " ".join(parts[1:])
        
        # Note: If generateimage is synchronous and slow, it blocks the bot.
        generateimage(text, "discord") 
        
        if os.path.exists("output.png"):
            with open("output.png", "rb") as f:
                picture = discord.File(f)
                await message.channel.send(file=picture)
        else:
            await message.channel.send("Failed to generate image.")

    # ---- 6. Redfin Key Command ----
    elif command == "redfinkey":
        if len(parts) > 2:
            # Usage: redfinkey [city] [link]
            city_text = parts[1:]
            await message.channel.send(redfincityjson({city_text[0].strip(): city_text[1].strip()}, "discord"))
        else:
            await message.channel.send(redfincityjson(discord="discord"))

    # ---- 7. Redfin Average Command ----
    elif command == "redfinaverage":
        if len(parts) < 3:
            return await message.channel.send("Usage: `redfinaverage [bedrooms] [City]`")
        bedroom = parts[1]
        city = " ".join(parts[2:]) # Handles multi-word cities like "Santa Cruz" safely
        await message.channel.send(findcityInfo(city, bedroom, "discord"))

    elif command == "redfintable":  # <-- Added the missing "d" here
        if os.path.exists("redfin_properties.csv"):
            with open("redfin_properties.csv", "rb") as f:
                table = discord.File(f)
                await message.channel.send(content="📊 Here is your requested Redfin properties table:", file=table)
        else:
            await message.channel.send("❌ No data table found. Run `redfinaverage` first to generate the spreadsheet!")

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