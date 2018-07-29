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
