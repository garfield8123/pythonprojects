import discord
import asyncio
import shutil
from Currentemp.currenttemp import gettemperature
from dcodefr.cipheridentifier import identifycipher
from household_income.income import getincomedata 
from household_income.income import getincomekeys
from localimagebot.localimage import generateimage, load_model
from housefind.redfin import redfincityjson
from housefind.redfin import findcityInfo
from gemenichat.localchat import GemmaAnalyzer
from youtube2mp3.youtube2mp3 import playlist2mp3, youtubevideo2mp3, zipfolder
from aiohttp import web
import os


intents = discord.Intents.default()
intents.message_content= True
client = discord.Client(intents=intents)

analyzer = GemmaAnalyzer(discord=True)


def cleanup_paths(*paths):
    """
    Safely and recursively deletes directories and files passed as arguments.
    """
    for path in paths:
        if not path or not os.path.exists(path):
            continue
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)  # Recursively deletes a folder and all its contents
                print(f"🗑️ Successfully deleted directory: {path}")
            elif os.path.isfile(path):
                os.remove(path)      # Deletes a single file
                print(f"🗑️ Successfully deleted file: {path}")
        except Exception as e:
            print(f"⚠️ Failed to clean up {path}: {e}")

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
        embed.add_field(
            name="🎵 YouTube Downloader",
            value="`!downloadvideo [URL]`\nDownloads a YouTube video as MP3 and sends it directly.\n\n`!downloadplaylist [URL]`\nDownloads a whole playlist, zips it up, and sends it to you.",
            inline=False
        )
        
        embed.set_footer(text="Tip: Make sure to check your spelling and provide all parameters!")
        await message.channel.send(embed=embed)
    # ---- NEW COMMAND: Multi-turn Chat ----
    elif command == "!downloadvideo":
        if len(parts) < 2:
            return await message.channel.send("❌ Please provide a YouTube link! Example: `!downloadvideo https://youtube.com/...`")
        
        url = parts[1]
        # Create a unique download directory for this request
        # In discord/bot.py under !downloadvideo:
        download_dir = os.path.abspath(f"./temp_video_{message.id}")
        os.makedirs(download_dir, exist_ok=True)
        
        await message.channel.send("📥 Fetching your video... Please wait.")
        
        async with message.channel.typing():
            try:
                # Run sync download in a non-blocking thread
                await asyncio.to_thread(youtubevideo2mp3, url, download_dir)
                
                # Locate the downloaded file inside the temp folder
                files = os.listdir(download_dir)
                if not files:
                    raise FileNotFoundError("Failed to download or locate the video file.")
                
                file_to_send = os.path.join(download_dir, files[0])
                
                # Send the file to discord
                await message.channel.send(file=discord.File(file_to_send))
                
            except discord.errors.HTTPException as e:
                await message.channel.send("⚠️ The video was downloaded, but the file size is too large for Discord to upload.")
            except Exception as e:
                await message.channel.send(f"❌ An error occurred: {str(e)}")
            finally:
                # Always clean up the local files
                cleanup_paths(download_dir)

  # ---- NEW COMMAND: Download YouTube Playlist ----
    elif command == "!downloadplaylist":
        if len(parts) < 2:
            return await message.channel.send("❌ Please provide a YouTube playlist link!")
        
        playlist_url = parts[1]
        download_dir = f"./temp_playlist_{message.id}"
        zip_filename = f"music_{message.id}" # Unique name to avoid clashes
        zip_filepath = f"{zip_filename}.zip"
        
        os.makedirs(download_dir, exist_ok=True)
        await message.channel.send("📥 Starting playlist download. This might take a while due to rate limits...")
        
        # We track whether we want to keep the zip file or not
        keep_zip = False 
        
        async with message.channel.typing():
            try:
                # 1. Download playlist
                await asyncio.to_thread(playlist2mp3, playlist_url, download_dir)
                
                # 2. Archive playlist directory
                await asyncio.to_thread(shutil.make_archive, zip_filename, "zip", download_dir)
                
                # 3. Send zip file
                await message.channel.send(
                    content="🎉 Here is your zipped playlist!", 
                    file=discord.File(zip_filepath)
                )
                
            except discord.errors.HTTPException as e:
                # Set flag to true so we do not delete the zip file in the finally block
                keep_zip = True 
                await message.channel.send(f"⚠️ The ZIP file is too large for Discord's upload limit. Saved locally as `{zip_filepath}`.")
            except Exception as e:
                await message.channel.send(f"❌ Failed to download playlist: {str(e)}")
            finally:
                # 4. If keep_zip is True, only delete the folder. Otherwise, delete both.
                if keep_zip:
                    await asyncio.to_thread(cleanup_paths, download_dir)
                else:
                    await asyncio.to_thread(cleanup_paths, download_dir, zip_filepath)
                
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
            return await message.channel.send("❌ Please provide a prompt. Example: `image a cool cat`")
        
        # 1. Safety check to make sure the model is loaded
        if client.image_pipeline is None:
            return await message.channel.send("⏳ The image generator is still loading. Please try again in a moment!")

        text = " ".join(parts[1:])
        
        await message.channel.send("🎨 Generating your image... Please wait.")
        
        async with message.channel.typing():
            try:
                # 2. Run the generator on a separate thread so the bot doesn't freeze
                # This calls your updated: generateimage(client.image_pipeline, text)
                await asyncio.to_thread(generateimage, client.image_pipeline, text)
                
                # 3. Check and send the file
                if os.path.exists("output.png"):
                    with open("output.png", "rb") as f:
                        picture = discord.File(f)
                        await message.channel.send(file=picture)
                    
                    # Optional: Delete output.png after sending to save space
                    try:
                        os.remove("output.png")
                    except Exception:
                        pass
                else:
                    await message.channel.send("❌ Failed to generate image.")
                    
            except Exception as e:
                await message.channel.send(f"❌ An error occurred during generation: {e}")

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
client.image_pipeline = None
localserver = False
if localserver:
    @client.event
    async def on_ready():
        if client.image_pipeline is None:
            # Run synchronous loading in an executor to avoid freezing the Discord bot startup
            loop = asyncio.get_running_loop()
            client.image_pipeline = await loop.run_in_executor(None, load_model, True)
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
        if client.image_pipeline is None:
            # Run synchronous loading in an executor to avoid freezing the Discord bot startup
            loop = asyncio.get_running_loop()
            client.image_pipeline = await loop.run_in_executor(None, load_model, True)
        print(f"Logged in as {client.user}")

    async def main():
        await start_webserver()
        discordToken=os.environ.get("discordtoken")
        await client.start(discordToken)

    asyncio.run(main())