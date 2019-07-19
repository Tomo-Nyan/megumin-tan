#!/usr/bin/python3
import requests,datetime
lastRequest = datetime.datetime.utcnow().timestamp() #this is for rate limiting.
api = 'https://api.jikan.moe/v3/'

class malResult:
    def __init__(self,type,id):
        self.malID = id
        self.contentType = type
        self.requestStatus = 0
        self.thumbURL = None
        self.pageURL = None
        self.titleEnglish = None
        self.titleJapanese = None
        self.malType = None
        self.number = None
        self.airing = None
        self.status = None
        self.started = None
        self.ended = None
        self.synopsis = None
        self.genres = None #this will be an array
        self.broadcast = None
        self.licensors = None #array
        self.studios = None
        self.origin = None
        self.publishing = None
        self.authors = None #array

def fetchAnime(id):
    response = requests.get(f'{api}/anime/{id}/')
    result = malResult('anime',id)
    if response.status_code == 200:#all good
        data = response.json()
        result = _fetchAMShared(data,result)
        result.requestStatus = 1
        if "airing" in data:
            result.airing = data["airing"]
        if "aired" in data:
            if "from" in data["aired"]:
                result.started = data["aired"]["from"].split("T")[0]
            if "to" in data["aired"]:
                result.ended = data["aired"]["to"].split("T")[0]
        if "broadcast" in data:
            result.broadcast = data["broadcast"]
        if "licensors" in data:
            licensors = []
            for licensor in data["licensors"]:
                licensors.append(licensor["name"])
            result.licensors = licensors
        if "studios" in data:
            studios = []
            for studio in data["studios"]:
                studios.append(studio["name"])
            result.studios = studios
        if "source" in data:
            result.origin = data["source"]
        #wow this is fucking messy.
        return result

def fetchManga(id):
    response = requests.get(f'{api}/manga/{id}/')
    result = malResult('manga',id)
    if response.status_code == 200:
        data = response.json()
        result = _fetchAMShared(data,result)
        result.requestStatus = 1
        if "publishing" in data:
            result.publishing = data["publishing"]
        if "published" in data:
            if "from" in data["published"]:
                result.started = data["published"]["from"]
            if "to" in data["published"]:
                result.ended = data["published"]["to"]
        if "authors" in data:
            authors = []
            for author in data["authors"]:
                authors.append(author["name"])
            result.authors = authors
        return result

def _fetchAMShared(data,initialResult): #this sets the properties that both anime and manga pages use, to save space.
    result = initialResult
    if "url" in data:
        result.pageURL = data["url"]
    if "image_url" in data:
        result.thumbURL = data["image_url"]
    if "title" in data:
        result.titleEnglish = data["title"]
    if "title_japanese" in data:
        result.titleJapanese = data["title_japanese"]
    if "type" in data:
        result.malType = data["type"]
    if "episodes" in data:
        result.number = data["episodes"]
    elif "chapters" in data:
        result.number = data["chapters"]
    if "status" in data:
        result.status = data["status"]
    if "synopsis" in data:
        result.synopsis = data["synopsis"]
    if "genres" in data:
        genres = []
        for genre in data["genres"]:
            genres.append(genre["name"])
        result.genres = genres
    return result
