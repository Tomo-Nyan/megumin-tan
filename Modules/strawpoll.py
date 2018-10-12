#!/usr/bin/python3

import json,urllib.request,requests

def getPollDetailsFID(id):
    response = requests.get("".join(("https://www.strawpoll.me/api/v2/polls/",str(id))))
    return response.json()

def getPollDetailsFURL(url):
    response = requests.get("".join(("https://www.strawpoll.me/api/v2/polls/",url.lstrip("https://www.strawpoll.me/"))))
    return response.json()

def createPoll(title,options,multi="false",dupcheck="normal",captcha="true"):
    data = {"title":title,"options":options,"multi":multi,"dupcheck":dupcheck,"captcha":captcha}
    response = requests.post("https://www.strawpoll.me/api/v2/polls",headers={"Content-Type":"application/json"},data=json.dumps(data))
    return response.json()
