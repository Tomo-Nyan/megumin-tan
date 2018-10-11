#!/usr/bin/python3
'''
Documentation, License etc.
@package discordbot001
'''
import discord,random, pymysql,os,os.path,json,urllib.request,apscheduler.schedulers.background,string,io,concurrent.futures,time
import Modules.utilfuncs as utils
import Modules.nhentai as nhentai
#import Modules.steam as steam
prefix = ">"

cfg = utils.load("json/bot.cfg")
#speech = utils.load("json/speech/ENG_Megumin_Base.speech")
commands = utils.load("json/help.json")
regionalindicators = utils.load("json/indicators.json")
chants = utils.load("json/chants.json")

#instances
client = discord.Client()
#connection = pymysql.connect(host='localhost',user=cfg["dbUsername"],password=cfg["dbPassword"],db=cfg["dbName"],charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

#Discord Events
@client.event
async def on_ready():
    print(concat(("Logged in as ",client.user)))
    await client.change_presence(activity=discord.Game(name="with my staff"))

@client.event
async def on_raw_reaction_add(payload):
    print("")
    with connection.cursor() as cursor:
        cursor.execute(concat(("SELECT ")))

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
            data = utils.doGETJSON("https://xkcd.com/info.0.json")
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
                strComicData = utils.doGETJSON("".join(("https://xkcd.com/",str(intComicID),"/info.0.json")))
                e = discord.Embed()
                e.set_image(url = strComicData["img"])
                await message.channel.send(embed = e)
                    
        if cmd.startswith("gelbooru"):
            args = rawArguments
            data = utils.doGETJSON("https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1")
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
                    data = utils.doGETJSON(concat(("https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags=","+".join(tags))))
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

#
        if cmd.startswith("nhentai"):
            args = spaceArguments
            if args[0] == "latest":
                await message.channel.send(embed=fetchNHentaiComicFD(nhentai.getLatest(1),0))
            elif args[0] == "random":
                data = nhentai.getLatest(1)
                id = random.randint(1,int(data["result"][0]["id"]))
                await message.channel.send(embed=fetchNHentaiComic(id))
            elif args[0] == "id":
                if int(args[1]) > 0 and int(args[1]) <= int(nhentai.getLatest(1)["result"][0]["id"]) and args[1].isnumeric:
                    await message.channel.send(embed=fetchNHentaiComic(args[1]))
            elif args[0] == "tags":
                tags = rawArguments.split(" ")[1].split(",")
                e = nhentai.search(tags,1)
                if e != None:
                    e = fetchNHentaiComicFD(e,random.randint(0,len(e)-1))
                    await message.channel.send(embed=e)
                else:
                    await message.channel.send(embed=discord.Embed(color=0xff0000,title="Error",description="Invalid tag(s)"))

        #if cmd.startswith("steam"):
            #args = spaceArguments
            #if args[0] == "common":
                #mentions = message.mentions
                #users = []
                #for user in mentions:
                    #print("")
            #if args[0] == "add":
                #print(type(message.channel))
                #if type(message.channel) == discord.TextChannel or type(message.channel) == discord.GroupChannel:
                    #await message.channel.send(embed=discord.Embed(color=0xff0000,title="Error",description="You should do this in A DM.\nPeople are bad."))
                    #return None
                ##with connection.cursor() as cursor:
                    ##cursor.execute("")
                #url = args[1]
                #id = steam.getID(url)
                #if id != None:
                    #user = steam.getUserInfo(id)
                #else:
                    #await message.channel.send(embed=discord.Embed(color=0xff0000,title="Error",description="Invalid URL"))
                    #return None
                #if user != None:
                    #user = user["response"]["players"][0]
                    #e = discord.Embed(color=0x444444)
                    #e.set_author(name="Is this you? (timeout:15s)",icon_url=user["avatar"])
                    #e.add_field(name=user["personaname"],value=concat(("SteamID = ",user["steamid"])))
                    #msg = await message.channel.send(embed=e)
                    #await msg.add_reaction("✅")
                    #await msg.add_reaction("❎")
                    #with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        #future = executor.submit(addSteam,message,msg.id,user["steamid"],15)
                        




                #games = []
                #for game in sharedGames:
                    #games.add(steam.getGameInfo(game)["name"])
                #e = discord.Embed(color=0x444444,title="Common games:",description="\n".join((games)))
                #message.channel.send(embed=e)
        if cmd.startswith("ping"):
            await message.channel.send(concat((client.latency * 1000,"ms")))

        if cmd.startswith("help"):
            embed = discord.Embed(color=0x00e5ff)
            embed.title = "Help:"
            for i in range(0,len(commands[1])):
                embed.add_field(name=commands[1][i],value=commands[0][commands[1][i]],inline=False)
            await message.channel.send(embed=embed)

        if cmd.startswith("info"):
            if len(message.mentions) == 1:
                victim = message.mentions[0]
                embed = discord.Embed(color=0x00e5ff)
                embed.set_author(name="".join(("Info for ",victim.name,":")),icon_url=victim.avatar_url)
                embed.description = "\n".join((concat(("ID: ",victim.id)),concat(("Name: ",victim.name)),concat(("Nick: ",victim.display_name)),concat(("Creation Date: ",victim.created_at)),concat(("Avatar URL: [url](",victim.avatar_url_as(static_format="png"),")"))))
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

        if cmd.startswith("strawpoll"):
            print("")
                
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

#req = req.read().decode('utf-8')
def fetchBooruPost(postID):
    try:
        data = utils.doGETJSON(concat(("https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&id=",postID)))
        if len(data) > 0:
            post = data[0]
            embed = discord.Embed(color=0xff28fb)
            embed.set_image(url = post["file_url"])
            embed.title = concat(("Post ID:",post["id"]," | Created:",post["created_at"]))
            if post["source"] != "":
                embed.description = "\n".join(("".join(("`","`, `".join(post["tags"].split(" ")),"`")),"".join(("[source](",post["source"],")"))))
            else:
                embed.description = "".join(("`","`, `".join(post["tags"].split(" ")),"`"))
            if len(embed.description) > 4000:
                embed.description = "holy fuck. so many fucking tags."
        else:
            embed = discord.Embed(color=0xff0000,title="Error",description="No posts were returned")
    except:
        embed = discord.Embed(color=0xff0000,title="Error",description="Invalid post ID")
    return embed
def fetchNHentaiComic(comicID):
    comic = nhentai._getGalleryData(comicID)
    imageurls = nhentai.getGalleryURLSFID(comic["id"])
    return formatNHentaiComic(comic,imageurls)

def fetchNHentaiComicFD(data,num):
    comic = data["result"][num]
    imageurls = nhentai.getGalleryURLSFD(nhentai.formatResult(data,num))
    return formatNHentaiComic(comic,imageurls)

def formatNHentaiComic(comic,imageurls):
    embed = discord.Embed(color=0xff28fb)
    if "cover" in imageurls:
        imageurl = imageurls["thumb"]
    else:
        imageurl = imageurls[1]
    embed.set_image(url=imageurl)
    embed.title = concat((comic["id"]," | ",comic["title"]["english"]))
    tags,languages,characters,parodies,artists,groups = [[],[],[],[],[],[]]
    for tag in comic["tags"]:
        if tag["type"] == "tag":
            tags.append(tag["name"])
        elif tag["type"] == "language":
            languages.append(tag["name"].replace("[","").replace("]","").replace("'",""))
        elif tag["type"] == "character":
            characters.append(tag["name"])
        elif tag["type"] == "parody":
            parodies.append(tag["name"])
        elif tag["type"] == "artist":
            artists.append(tag["name"])
        elif tag["type"] == "group":
            groups.append(tag["name"])
    if len(characters) > 0:
        embed.description = "\n".join(("Language: ",ilQuoteArray(languages),"Tags: ",ilQuoteArray(tags),"Character(s): ",ilQuoteArray(characters),concat(("[Link](https://nhentai.net/g/",str(comic["id"]),"/)"))))
    else:
        embed.description = "\n".join(("Language: ",ilQuoteArray(languages),"Tags: ",ilQuoteArray(tags),concat(("[Link](https://nhentai.net/g/",str(comic["id"]),"/)"))))
    if len(artists) > 0:
        if len(groups) > 0:
            embed.set_footer(text=" | ".join((concat(("Artist(s): ",", ".join((artists)))),concat(("Group(s): ",", ".join((groups)))))))
        else:
            embed.set_footer(text=concat(("Artist(s): ",", ".join((artists)))))
    elif len(groups) > 0:
        embed.set_footer(text=concat(("Group(s): ",", ".join((groups)))))
    return embed

def ilQuoteArray(input):
    if len(input) > 1:
        return concat(("`","`, `".join(input),"`"))
    elif len(input) == 1:
        return concat(("`",input,"`"))
    else:
        return None

#def addSteam(message,msg,steamid,timeout):
    #timeout = time.time() + timeout
    #userid = message.author.id
    #while True:
        #print("loop!")
        #if time.time() >= timeout:
            #return False
        #time.sleep(1)
        #print(reactions)
        #if len(reactions) > 2:
            #for reaction in reactions:
                #if reaction.emoji.name == "negative_squared_cross_mark" and reaction.count == 2:
                    #return False
                #if reaction.emoji.name == "white_check_mark" and reaction.count == 2:
                    #with connection.cursor() as cursor:
                        #cursor.execute(concat(("INSERT INTO tblSteamUser (steamID) VALUES (",steamid,");")))
                        #cursor.execute(concat(("INSERT INTO tblSUU (userID,steamID) VALUES (",userid,",",steamid,");")))
                    #connection.commit()
                    #print("Added!")
                    #message.channel.send("Your steam ID has been added!")
                    #return True

client.run(cfg["bottoken"])
















