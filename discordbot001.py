#!/usr/bin/python3
'''
Documentation, License etc.
@package discordbot001
'''
import discord,random, pymysql,os,os.path,json,urllib.request,apscheduler.schedulers.background,string,io,concurrent.futures,time
import Modules.utilfuncs as utils
import Modules.nhentai as nhentai
import Modules.strawpoll as strawpoll
import Modules.reddit as reddit
import Modules.mal as mal
#import Modules.steam as steam
prefix = ">"

cfg = utils.load("json/bot.cfg")
#speech = utils.load("json/speech/ENG_Megumin_Base.speech")
commands = utils.load("json/help.json")
regionalindicators = utils.load("json/indicators.json")
chants = utils.load("json/chants.json")
reactions = utils.load("json/imageSource.json")

#instances
client = discord.Client()
menus = {}
#connection = pymysql.connect(host='localhost',user=cfg["dbUsername"],password=cfg["dbPassword"],db=cfg["dbName"],charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

#Discord Events
@client.event
async def on_ready():
    print(concat(("Logged in as ",client.user)))
    await client.change_presence(activity=discord.Game(name="with my staff"))

#@client.event
#async def on_raw_reaction_add(payload):
    #print("")
    #with connection.cursor() as cursor:
        #cursor.execute(concat(("SELECT ")))

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

        if cmd.startswith("reddit"):
            data = reddit.fetchRedditPost(rawArguments)
            embed=discord.Embed(color=0xff0000,title="Error",description="That's not a valid subreddit, baaka~")
            if data["successful"]:
                embed = discord.Embed(color=0xff6e00,title=data["title"],description=data["description"])
                embed.set_footer(text=data["footer"])
                if data["type"] == "image":
                    embed.set_image(url=data["imgurl"])
            await message.channel.send(embed=embed)

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
            title,questions = splitTQ(rawArguments)
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
            embed = discord.Embed(color=0xE4D96F)
            if rawArguments.startswith("create "):
                title,questions = splitTQ(rawArguments.lstrip("create "))
                data = strawpoll.createPoll(title,questions)
                url = "".join(("https://www.strawpoll.me/",str(data["id"])))
            elif rawArguments.startswith("show "):
                identifier = rawArguments.lstrip("show ")
                if "https://" in identifier:
                    data = strawpoll.getPollDetailsFURL(identifier)
                    title = data["title"]
                    questions = data["options"]
                    url = "".join(("https://www.strawpoll.me/",str(data["id"])))
                elif identifier.isnumeric:
                    data = strawpoll.getPollDetailsFID(identifier)
                    title = data["title"]
                    questions = data["options"]
                    url = "".join(("https://www.strawpoll.me/",str(data["id"])))
            embed.title = title
            embed.description = "\n".join((("\n - ".join(["Options:"] + questions)).rstrip("\n - "),"".join(("[[url]](",url,")"))))
            await message.channel.send(embed=embed)

        if cmd.startswith("quickvote"):
            question = rawArguments
            embed = discord.Embed(color=0x00ff7f)
            embed.title = concat(("Quickote by ",message.author,"!"))
            embed.description = question
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")

########################################################################################################################################################
        if cmd.startswith('malqa'):
            await message.channel.send(embed=displayMA('a/' + str(mal.search(' ' + rawArguments,'anime')[1][0][3]),discord.Embed(color=0x2e51a2)))
        if cmd.startswith('malqm'):
            await message.channel.send(embed=displayMA('m/' + str(mal.search(' ' + rawArguments,'manga')[1][0][3]),discord.Embed(color=0x2e51a2)))
        if cmd.startswith("mal "):
            subcommand = rawArguments.split(" ")[0]
            embed = discord.Embed(color=0x2e51a2)
            if subcommand == "id":
                id = rawArguments.split(" ")[1].lower()
                await message.channel.send(embed=displayMA(id,embed))
                await message.delete()
            else: #search
                rawString = ' ' + rawArguments
                searchType = 'anime'
                searchTypeLetter = 'a'
                if 'm/' in rawString.lower() or ' m ' in rawString.lower():
                    searchType = 'manga'
                    searchTypeLetter = 'm'
                    rawString.replace('m/','')
                    rawString.replace(' m ','')
                data = mal.search(rawString,searchType)
                if data[0] == 1:
                    if len(data[1]) > 1:
                        desc = ''
                        ref = {'user': str(message.author.id)}
                        r = len(data[1])
                        if r > 4:
                            r = 4
                        for i in range(0,r):
                            result = data[1][i]
                            desc = f'{desc}{regionalindicators[i]} [{result[1]}][{result[0]}]\n'
                            ref[regionalindicators[i]] = f'{searchTypeLetter}/{result[3]}'
                        embed.description = desc
                        sm = await message.channel.send(embed=embed)
                        menus[str(sm.id)] = ref
                        for i in range(0,r):
                            await sm.add_reaction(regionalindicators[i])
                        await sm.delete(delay=30)
                        await message.delete()
                elif data[0] != 1:
                    if data[0] == 'NR':
                        embed.title = 'Error!'
                        embed.color = 0xff0000
                        embed.description = f'Sorry, there are no results for "{rawString}"! (code `ID` `10` `T`)'
                    else:
                        embed.title = 'Fatal Error!'
                        embed.color = 0xff0000
                        embed.description = f'Sorry, there has been a serious error! (code `{data[0]}`)'
                    await message.channel.send(embed=embed)

        #reactions
        if cmd.startswith("cry"):
            e = discord.Embed(color=0x7af442)
            e.title = "*cries*"
            e.set_image(url=reactions["cry"][random.randint(0,len(reactions["cry"])-1)])
            await message.channel.send(embed=e)
        if cmd.startswith("smug"):
            e = discord.Embed(color=0x7af442)
            e.title = "*smug*"
            e.set_image(url=reactions["smug"][random.randint(0,len(reactions["smug"])-1)])
            await message.channel.send(embed=e)
        if cmd.startswith("dance"):
            e = discord.Embed(color=0x7af442)
            e.title = "*dances*"
            e.set_image(url=reactions["dance"][random.randint(0,len(reactions["dance"])-1)])
            await message.channel.send(embed=e)
        if cmd.startswith("argue"):
            e = discord.Embed(color=0x7af442)
            e.title = "oi"
            e.set_image(url=reactions["argue"][random.randint(0,len(reactions["argue"])-1)])
            await message.channel.send(embed=e)
        if cmd.startswith("aghast"):
            e = discord.Embed(color=0x7af442)
            e.set_image(url=reactions["aghast"][random.randint(0,len(reactions["aghast"])-1)])
            await message.channel.send(embed=e)

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

@client.event
async def on_raw_reaction_add(payload):
    idMessage = str(payload.message_id)
    idChannel = payload.channel_id
    idUser = payload.user_id
    emoji = payload.emoji.name
    if str(idUser) == str(menus[idMessage]['user']):
        if emoji in menus[idMessage]:
            embed = discord.Embed(color=0x2e51a2)
            channel = client.get_channel(idChannel)
            await channel.send(embed=displayMA(str(menus.pop(idMessage)[emoji]),embed))
            message = await channel.fetch_message(idMessage)
            await message.delete()

@client.event
async def on_raw_message_delete(payload):
    if payload.message_id in menus:
        menus.pop(idMessage)

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

############################################################################################################################################################################
def displayMA(id,embed):
    print(f'id = "{id}"')
    if id.startswith('a/'):
        data = mal.fetchAnime(id.lstrip('a/'))
    elif id.startswith('m/'):
        data = mal.fetchManga(id.lstrip('m/'))
    else:
        data = mal.fetchAnime(id)
        if int(data['request_status']) != 1:
            data = mal.fetchManga(id)
    embed.title = 'fuckin error m8'
    embed.description = 'get shat on'
    print(f'[DEBUG] status code = "{data["request_status"]}"')
    if data['request_status'] == 1:
        if 'title_formatted' in data:
            embed.title = data['title_formatted']
        if 'synopsis' in data:
            if len(data['synopsis']) > 600:
                short = data['synopsis'][0:599]
                embed.description = f'[[url]]({data["page_url"]})\n```\n{short}...\n```'
            else:
                embed.description = f'[[url]]({data["page_url"]})\n```\n{data["synopsis"]}\n```'
        if 'thumb_url' in data:
            embed.set_thumbnail(url=data['thumb_url'])
        if 'genres' in data:
            name = 'Genre'
            if len(data['genres']) > 1:
                name = 'Genres'
            embed.add_field(name=name,value=''.join(('`','`,`'.join(data['genres']),'`')),inline=False)
        if 'episodes' in data:
            embed.add_field(name='Episodes',value=data['episodes'],inline=True)
        if 'chapters' in data:
            embed.add_field(name='Chapters',value=data['chapters'],inline=True)
        if 'airing_status' in data:
            embed.add_field(name='Airing Status',value=data['airing_status'],inline=True)
        if 'publishing_status' in data:
            embed.add_field(name='Publishing Status',value=data['publishing_status'],inline=True)
        if 'origin' in data:
            embed.add_field(name='Origin',value=data['origin'],inline=True)
        if 'licensors' in data:
            name = 'Licensor'
            if len(data['licensors']) > 1:
                name = 'Licensors'
            embed.add_field(name=name,value=''.join(('`','`,`'.join(data['licensors']),'`')),inline=True)
        if 'studios' in data:
            name = 'Studio'
            if len(data['studios']) > 1:
                name = 'Studios'
            embed.add_field(name=name,value=''.join(('`','`,`'.join(data['studios']),'`')),inline=True)
        if 'authors' in data:
            name = 'Author'
            if len(data['authors']) > 1:
                name = 'Authors'
            embed.add_field(name=name,value=''.join(('`','`,`'.join(data['authors']),'`')),inline=True)
    elif data['request_status'] == 4:
        embed.title = 'Error!'
        embed.color = 0xff0000
        embed.description = 'Sorry, that can\'t be found!'
    else:
        embed.title = 'Fatal Error!'
        embed.color = 0xff0000
        embed.description = f'Sorry, there has been a serious error! (code `{data["request_status"]}`)'
    return embed

def ilQuoteArray(input):
    if len(input) > 1:
        return concat(("`","`, `".join(input),"`"))
    elif len(input) == 1:
        return concat(("`",input,"`"))
    else:
        return None

def splitTQ(argfull):
    #argfull = rawArguments
    quotes = argfull.count("\"")
    colons = argfull.count(":")
    questions = []
    if colons > 0:
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
    return [title,questions]

client.run(cfg["bottoken"])
