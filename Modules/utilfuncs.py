#!/usr/bin/python3

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

def debug(string):
    output = "".join(("[DEBUG] "))
