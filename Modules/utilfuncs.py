#!/usr/bin/python3

import json

def getAllRealServerUsers(server):
    nbusers = []
    for user in server.members:
        if not user.bot:
            nbusers.append(user)
    return nbusers
    
def getAllBotServerUsers(server):
    busers = []
    for user in server.members:
        if user.bot:
            busers.append(user)
    return busers

def load(file):
    with open(file,"r") as h:
        return json.load(h)

def debug(string):
    output = "".join(("[DEBUG] "))

def serverExistsDB(connection,serverID):
    with connection.cursor() as cursor:
        cursor.execute("".join(("SELECT serverID FROM tblServer WHERE serverID = ",str(serverID))))
        res = cursor.fetchone()
        if res == None:
            return False
        else:
            return True

def feedExistsDB(connection,feedURL):
    with connection.cursor() as cursor:
        cursor.execute("".join(("SELECT feedID FROM tblFeed WHERE strFeedURL = ",str(feedURL))))
        res = cursor.fetchone()
        if res == None:
            return False
        else:
            return True

def serverFeedExistsDB(connection,serverID,feedID):
    with connection.cursor() as cursor:
        cursor.execute("".join(("SELECT feedID FROM tblFeed WHERE feedID = ",str(feedID)," AND serverID = ",str(serverID))))
        res = cursor.fetchone()
        if res == None:
            return False
        else:
            return True

def addServerDB(connection,serverID,prefix,feedChannelID):
    with connection.cursor() as cursor:
        if prefix == None or len(prefix) == 0 or prefix == "":
            cursor.execute("".join(("INSERT INTO tblServer (serverID) VALUES (",str(serverID),");")))
            connection.commit()
            return True
        elif len(prefix) < 9:
            cursor.execute("".join(("INSERT INTO tblServer (serverID,strPrefix) VALUES (",str(serverID),",",str(prefix),");")))
            connection.commit()
            return True
        else:
            return False

def addFeedDB(connection,feedURL):
    with connection.cursor() as cursor:
        if feedURL == None or len(feedURL) == 0 or feedURL == "":
            return False
        else:
            cursor.execute("".join(("INSERT INTO tblFeed (strFeedURL) VALUES (",str(feedURL),");")))
            connection.commit()
            return True

def addServerFeedDB(connection,serverID,feedID):
    with connection.cursor() as cursor:
        cursor.execute("".join(("INSERT INTO tblServerFeed (feedID,serverID) VALUES (",str(feedID),",",str(serverID),");")))
        connection.commit()

def fetchFeedID(connection,feedURL):
    with connection.cursor() as cursor:
        cursor.execute("".join(("SELECT feedID FROM tblFeed WHERE strFeedURL = ",feedURL,";")))
        return cursor.fetchone()["feedID"]

def fetchFeedURL(connection,serverID):
    with connection.cursor() as cursor:
        cursor.execute("".join(("SELECT tblFeed.strFeedURL FROM tblFeed,tblServerFeed WHERE tblServerFeed.serverID = ",str(serverID),";")))
        return getDictionaryListValues(cursor.fetchall(),"strFeedURL")

def fetchFeeds(connection):
    with connection.cursor() as cursor:
        cursor.execute("SELECT feedID,strFeedURL,strLastTime FROM tblFeed")
        return cursor.fetchall()

def fetchFeedServers(connection,feedID):
    with connection.cursor() as cursor:
        cursor.execute("".join(("SELECT tblServer.serverID,tblServer.feedChannelID FROM tblServer,tblServerFeed WHERE tblServerFeed.feedID = ",str(feedID))))
        return cursor.fetchall()

def getDictionaryListValues(dictList,key):
    result = []
    for dict in dictList:
        result.append(dict[key])
    return result
















