#!/usr/bin/python3

import json,urllib.request,requests

def _getGalleryData(id):
    return requests.get("".join(("https://nhentai.net/api/gallery/",str(id))),headers={"User-Agent":"Python/Bot"}).json()

def formatResult(data,num):
    if num != None:
        endResult = data["result"][num]
        endResult.update({"num_pages":data["num_pages"]})
        return endResult
    else:
        return None

def getGalleryURLSFD(data):
    pageNumbers = data["num_pages"]
    images = {}
    if data["images"]["pages"][0]["t"] == "p":
        ext = "png"
    elif data["images"]["pages"][0]["t"] == "j":
        ext = "jpg"
    if "cover" in data["images"]:
        images.update({"cover":("".join(map(str,("https://t.nhentai.net/galleries/",data["media_id"],"/cover.",ext))))})
    if "thumbnail" in data["images"]:
        images.update({"thumb":("".join(map(str,("https://t.nhentai.net/galleries/",data["media_id"],"/thumb.",ext))))})

    for i in range(1,pageNumbers+1):
        images.update({i:("".join(map(str,("https://i.nhentai.net/galleries/",data["media_id"],"/",i,".",ext))))})
    return images

def getGalleryURLSFID(id):
    data = _getGalleryData(id)
    pageNumbers = data["num_pages"]
    images = {}
    if data["images"]["pages"][0]["t"] == "p":
        ext = "png"
    elif data["images"]["pages"][0]["t"] == "j":
        ext = "jpg"
    if "cover" in data["images"]:
        images.update({"cover":("".join(map(str,("https://t.nhentai.net/galleries/",data["media_id"],"/cover.",ext))))})
    if "thumbnail" in data["images"]:
        images.update({"thumb":("".join(map(str,("https://t.nhentai.net/galleries/",data["media_id"],"/thumb.",ext))))})

    for i in range(1,pageNumbers+1):
        images.update({i:("".join(map(str,("https://i.nhentai.net/galleries/",data["media_id"],"/",i,".",ext))))})
    return images
def getGalleryTags(id):
    data = _getGalleryData(id)
    return data["tags"]

def search(tags,*args):
    if len(tags) > 0:
        if len(args) > 0:
            page = args[0]
        else:
            page = 1
        print("".join(map(str,("https://nhentai.net/api/galleries/search?query=","+".join(tags),"&page=",page))))
        results = requests.get("".join(map(str,("https://nhentai.net/api/galleries/search?query=","+".join(tags),"&page=",page))),headers={"User-Agent":"Python/Bot"}).json()
        if "error" in results:
            return None
        elif len(results["result"]) == 0:
            return None
        else:
            return results
def searchAllPages(tags):
    if len(tags) > 0:
        maxpage = search(tags,1)["num_pages"]
        results = []
        for i in range(1,maxpage,1):
            res = search(tags,i)
            if res != None:
                results.append(res)
        if len(results) > 0:
            return results
        else:
            return None
def getLatest(*args):
    if len(args) > 0:
        page = args[0]
    else:
        page = 1
    results = requests.get("".join(map(str,("https://nhentai.net/api/galleries/all?page=",page))),headers={"User-Agent":"Python/Bot"}).json()
    if "error" in results:
        return None
    else:
        return results
