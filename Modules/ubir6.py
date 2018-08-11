#!/usr/bin/python3

import json,urllib.request,requests,base64,aiohttp

appid = "39baebad-39e5-4552-8c25-2c9b919064e2"

class ubiSession:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.platforms = {"uplay":"uplay","xbox":"xbl","playstation":"psn"}

    def _getToken(self,email,password):
        return base64.b64encode((email + ":" + password).encode("utf-8")).decode("utf-8")

    def _getTicket(self,token):
        resp = self.session.post("https://connect.ubi.com/ubiservices/v2/profiles/sessions",headers={"Content-Type":"application/json","Ubi-AppId":appid,"Authorization":"Basic ZnJleS5ueWFuQGdtYWlsLmNvbTpaZXIwRGF5U3VjY2Vzc3Nz"},data=json.dumps({"rememberMe":True}))
        return resp
    
    def getPlayer(self,platform="uplay",name=None,id=None):
        if id != None:
            response = self.session.get("".join(("https://public-ubiservices.ubi.com/v2/profiles?platformType=",self.platforms[platform],"&id=",id)))
            if name != None:
                response = self.session.get("".join(("https://public-ubiservices.ubi.com/v2/profiles?platformType=",self.platforms[platform],"&name=",name)))
        elif name != None:
                response = self.session.get("".join(("https://public-ubiservices.ubi.com/v2/profiles?platformType=",self.platforms[platform],"&name=",name)))
        
