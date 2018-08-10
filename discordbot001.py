#!/usr/bin/python3
'''
Documentation, License etc.
@package discordbot001
'''
import discord,random,spice_api, pymysql,os,os.path,json,urllib.request,apscheduler.schedulers.background,string
import Modules.utilfuncs as utils

prefix = ">"

def job():
    return None

scheduler = apscheduler.schedulers.background.BackgroundScheduler()
scheduler.add_job(job, 'interval', seconds = 10)
scheduler.start()

cfg = utils.load("json/bot.cfg")
commands = utils.load("json/help.json")
regionalindicators = utils.load("json/indicators.json")
chants = utils.load("json/chants.json")

#instances
client = discord.Client()

#Discord Events
@client.event
async def on_ready():
    print(concat(("Logged in as ",client.user)))
    await client.change_presence(activity=discord.Game(name="with my staff"))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(prefix):
        cmd = message.content.lstrip(prefix)
        rawArguments = cmd.lstrip(cmd.split(" ")[0]).lstrip(" ")
        spaceArguments = rawArguments.split(" ")
        commaArguments = rawArguments.split(",")
        mentions = message.mentions

        if cmd.startswith("test"):
            print(dir(r6))
        if cmd.startswith("hello"):
            await message.channel.send("Hello, " + message.author.mention + "!")
            
        if cmd.startswith("coinflip"):
            result = ["Heads","Tails"]
            embed = discord.Embed(color=0x770075)
            embed.title = concat((message.author.name," flips a coin!"))
            embed.description = concat((message.author.name," got ",result[random.randint(0,1)]))
            await message.channel.send(embed=embed)
                
        if cmd.startswith("dice"):
            embed = discord.Embed(color=0x770075)
            embed.title = concat((message.author.name," rolls a die!"))
            embed.description = concat((message.author.name," rolled ",str(random.randint(1,int(cmd.split(" ")[1])))))
            await message.channel.send(embed=embed)

        if cmd.startswith("chant"):
            await message.channel.send(embed=chant())
        
        if cmd.startswith("userlist"):
            members = []
            names = []
            maxNameLength = 0
            members = utils.getAllRealServerUsers(message.guild)
            for user in members:
                names.append(user.name)
                if len(user.name) > maxNameLength:
                    maxNameLength = len(user.name)
            embed = discord.Embed(color=0xff0000)
            embed.title = concat(("Real users of guild \"",message.guild.name,"\":"))
            embed.description = "\n".join(names)
            await message.channel.send(embed=embed)
        
        if cmd.startswith("botlist"):
            members = []
            names = []
            members = utils.getAllBotServerUsers(message.guild)
            for user in members:
                names.append(user.name)
            embed = discord.Embed(color=0xff0000)
            embed.title = concat(("Bot users of guild \"",message.guild.name,"\":"))
            embed.description = "\n".join(names)
            await message.channel.send(embed=embed)
        
        if cmd.startswith("serverlist"):
            guilds1 = []
            for guild in client.guilds:
                guilds1.append(guild.name)
            embed = discord.Embed(color=0xff0000)
            embed.title = concat(("All connected servers:"))
            embed.description = "\n".join(guilds1)
            await message.channel.send(embed=embed)
            
        if cmd.startswith("xkcd"):
            arg = spaceArguments[0]
            with urllib.request.urlopen("https://xkcd.com/info.0.json") as req:
                data = json.load(req)
            intLatestComicID = data["num"]
            boolValid = True
            if arg == "random":
                intComicID = random.randint(0,intLatestComicID)
            elif arg == "latest":
                intComicID = intLatestComicID
            elif (int(arg) > 0) and (int(arg) <= intLatestComicID):
                intComicID = arg
            else:
                boolValid = False
                await message.channel.send("".join(("\"",arg,"\" is not a valid xkcd ID, baaka~")))
            if boolValid:
                with urllib.request.urlopen("".join(("https://xkcd.com/",str(intComicID),"/info.0.json"))) as req:
                    strComicData = json.load(req)
                    e = discord.Embed()
                    e.set_image(url = strComicData["img"])
                    await message.channel.send(embed = e)
                    
        if cmd.startswith("gelbooru"):
            args = rawArguments
            with urllib.request.urlopen("https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1") as req:
                    data = json.load(req)
            embed = discord.Embed(color=0xff0000,title="Error",description="baaka, you need to specify a subcommand. desu.")
            if args == "random":
                post = data[random.randint(0,len(data)-1)]["id"]
                embed = fetchBooruPost(post)
            if args == "latest":
                post = data[0]["id"]
                embed = fetchBooruPost(post)
            if args.startswith("tags"):
                tags = args.split(" ")[1].split(",")
                try:
                    with urllib.request.urlopen(concat(("https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags=","+".join(tags)))) as req:
                        data = json.load(req)
                    post = data[random.randint(0,len(data)-1)]["id"]
                    embed = fetchBooruPost(post)
                except:
                    embed = discord.Embed(color=0xff0000,title="Error",description="I could not find that. Sorry~!")
            if args.startswith("id"):
                id = args.split(" ")[1]
                if int(id) <= data[0]["id"] and int(id) > 0:
                    embed = fetchBooruPost(id)
                else:
                    embed = discord.Embed(color=0xff0000,title="Error",description="Invalid post ID")
            await message.channel.send(embed=embed)

        if cmd.startswith("nhentai"):
            print("")

        if cmd.startswith("help"):
            embed = discord.Embed(color=0x00e5ff)
            embed.title = "Help:"
            for i in range(0,len(commands[1])):
                embed.add_field(name=commands[1][i],value=commands[0][commands[1][i]],inline=False)
            await message.channel.send(embed=embed)
        
        if cmd.startswith("vote"):
            argfull = rawArguments
            quotes = argfull.count("\"")
            colons = argfull.count(":")
            title = concat(("Vote by ",message.author,"!"))
            questions = []
            if colons == 1:
                split = argfull.split(":")
                argfull = "".join(split[1:])
                title = split[0]
            if quotes%2 == 0:
                qsplit = argfull.split("\"")
                for q in qsplit:
                    if q != " " and q != ",":
                        questions.append(q)
            if colons == 1:
                questions = questions[1:]
            embed = discord.Embed(color=0x00ff7f)
            embed.title = title
            if len(questions) < 27 and len(questions) > 1:
                for i in range(0,len(questions)-1,1):
                    embed.add_field(name=concat(("Question ",string.ascii_uppercase[i]," (:regional_indicator_",string.ascii_lowercase[i],":)")),value=questions[i],inline=False)
                msg = await message.channel.send(embed=embed)
                for i in range(0,len(questions)-1,1):
                    await msg.add_reaction(regionalindicators[i])
            else:
                await message.channel.send("Enter between 2 and 26 options. Desu.")
                
        if cmd.startswith("quickvote"):
            question = rawArguments
            embed = discord.Embed(color=0x00ff7f)
            embed.title = concat(("Quickote by ",message.author,"!"))
            embed.description = question
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")

        if cmd.startswith("stickerlist"):
            path1 = os.path.abspath(cfg["absstickerpath"])
            files = []
            for f in os.listdir(path1):
                if os.path.exists:
                    files.append(f)
            await message.channel.send(", ".join(files))

        if cmd.startswith("sticker") and not cmd.startswith("stickerlist"):
            if len(cmd) > 8:
                stickername = concat((cfg["absstickerpath"],cmd.split(" ")[1],".png"))
                try:
                    await message.channel.send(file=discord.File(stickername))
                except FileNotFoundError:
                    await message.channel.send("That isn't a sticker yet, baaka~")
                    print("".join(("Could not find sticker \"",stickername,"\"!")))
            else:
                await message.channel.send("Enter an actual sticker name or I'll explode you!")
                
        if cmd.startswith("kick"):
            if message.channel.permissions_for(message.author).kick_members:
                victims = message.mentions
                await message.channel.send(embed=chant())
                for victim in victims:
                    try:
                        await message.guild.kick(victim)
                        await message.channel.send(concat(("Kicked ",victim.name,"!")))
                    except e as exception:
                        await message.channel.send(concat(("Failed to kick",victim.name)))
            else:
                await message.channel.send("You have insufficient permissions.")
    mm = False
    if len(message.mentions) > 0:
        for mention in message.mentions:
            if mention.id == client.user.id:
                mm = True
    if not message.author.bot:
        if "megumin" in message.content.lower() or mm:
            if "loli" in message.content.lower():
                await message.channel.send("Who are you calling a loli?")
            else:
                await message.channel.send("Hello, I am megumin.")
        if "flat" in message.content.lower():
            await message.channel.send("flat is justice!")
        if "explosion" in message.content.lower():
            await message.channel.send(embed=chant())

@client.event
async def on_member_join(member):
    print(concat((member.name," has joined guild ",member.guild.name,"!")))
    for channel in member.guild.text_channels:
        if "general" in channel.name:
            await channel.send(concat(("Welcome to ",member.guild.name,", ",member.mention,"!")))

@client.event
async def on_member_remove(member):
    print(concat((member.name," has left guild ",member.guild.name,"!")))
    for channel in member.guild.text_channels:
        if "general" in channel.name:
            await channel.send(concat(("Goodbye, ",member.name,"!")))

@client.event
async def on_member_ban(guild,user):
    for channel in guild.text_channels:
        if "general" in channel.name:
            await channel.send(concat((user.name," has been banned!")))

@client.event
async def on_member_unban(guild,user):
    for channel in guild.text_channels:
        if "general" in channel.name:
            await channel.send(concat((user.name," has been unbanned!")))

def concat(array,*args):
    if len(args) < 1:
        type = str
    else:
        type = args[0]
    convArray = map(type,array)
    concat = "".join(convArray)
    return concat

def chant():
    embed = discord.Embed(color=0xff9000)
    embed.title = concat(("Megumin casts explosion!"))
    embed.description = chants[random.randint(0,len(chants)-1)]
    return embed

def fetchBooruPost(postID):
    try:
        with urllib.request.urlopen(concat(("https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&id=",postID))) as req:
            data = json.load(req)
        if len(data) > 0:
            post = data[0]
            embed = discord.Embed(color=0xff28fb)
            embed.set_image(url = post["file_url"])
            embed.title = concat(("Post ID:",post["id"]," | Created:",post["created_at"]))
            if post["source"] != "":
                embed.description = "\n".join((", ".join(post["tags"].split(" ")),post["source"]))
            else:
                embed.description = ", ".join(post["tags"].split(" "))
        else:
            embed = discord.Embed(color=0xff0000,title="Error",description="No posts were returned")
    except:
        embed = discord.Embed(color=0xff0000,title="Error",description="Invalid post ID")
    return embed
client.run(cfg["bottoken"])
















