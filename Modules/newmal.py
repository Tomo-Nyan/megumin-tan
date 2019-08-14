#!/usr/bin/python3
import requests,datetime
from time import sleep
api = 'https://api.jikan.moe/v3'
lastRequest = datetime.datetime.utcnow().timestamp()

class _malResult:
    def __init__(self,type,id):
        self.malID = id
        self.contentType = type
        self.thumbURL = None
        self.pageURL = None
        self.titleEnglish = None
        self.titleJapanese = None
        self.malType = None
        self.number = None
        self.status = None
        self.synopsis = None
        self.genres = None

class finalMalResult:
    def __init__(self):
        self.embedTitle = None
        self.embedDescription = None
        self.embedURL = None
        self.embedFooter = None
        self.fields = None

def RLRequest(url):
    global lastRequest
    while lastRequest == 0:
        sleep(0.5)
    time = datetime.datetime.utcnow().timestamp()
    lr = lastRequest + 2
    lastRequest = 0
    if time < lr:
        sleep(lr - time)
    response = requests.get(url,headers={"User-Agent":"Megumin-Tan/Discord"})
    lastRequest = datetime.datetime.utcnow().timestamp()
    return response

def fetchAnime(id,embed):
    response = RLRequest(f'{api}/anime/{id}')
    result = malResult('anime',id)

    if response.status_code == 200:
        data = response.json()
        result = {}
        result = _fetchAMShared(data,result)
        result['request_status'] = 1
        aStatus = False
        if 'title' in result:
            title = result['title']
        elif 'title_ja' in result:
            title = result['title_ja']
        if 'type_mal' in result and title != None:
            result['title_formatted'] = f'[A/{id}][{result['type_mal']}][{title}]'
        if "airing" in data:
            result['airing'] = data["airing"]
            if data["airing"] and result['status']:
                final['airing_status'] = result['status']
                aStatus = True
            elif data["airing"]:
                final['airing_status'] = 'unknown'
                aStatus = True
        if "aired" in data:
            if "from" in data["aired"]:
                final['started'] = data["aired"]["from"].split("T")[0]
            if "to" in data["aired"]:
                final['ended'] = data["aired"]["to"].split("T")[0]
            if aStatus == False and data["airing"] == False:
                if result['started']:
                    if result['ended']:
                        final['airing_status'] = f'Aired {data['started']} to {data['ended']}'
                    else:
                        final['airing_status'] = f'Started Airing {data['started']}'
                else:
                    final['airing_status'] = data['status']
        if 'licensors' in data:
            result['licensors'] = []
            for licensor in data['licensors']:
                result['licensors'].append(licensor['name'])
        if 'studios' in data:
            result['studios'] = []
            for studio in data['studios']:
                result['studios'].append(studio['name'])
        if 'source' in data:
            result['origin'] = data['source']
    else:
        result['request_status'] = _responseParse(response)

def _responseParse(response):
    if response.status_code == 400: #invalid request
        print("[ERROR][mal.py] 400 Invalid Request")
        return 3
    elif response.status_code == 404: #mal not found
        print("[ERROR][mal.py] 404 Not Found")
        return 4
    elif response.status_code == 405: #invalid request
        print("[ERROR][mal.py] 405 Invalid Request")
        return 5
    elif response.status_code == 429: #rate limited
        print("[ERROR][mal.py] 429 Rate Limited")
        return 6
    elif response.status_code == 500: #cunt's fucked
        print("[ERROR][mal.py] 500 Internal Server Error")
        return 7
    else:
        return 0

def fetchManga(id):
    response = RLRequest(f'{api}/manga/{id}/')
    result = _malResult('manga',id)
    if response.status_code == 200:
        data = response.json()
        result = _fetchAMShared(data,result)
        result.requestStatus = 1
        if "publishing" in data:
            result.publishing = data["publishing"]
        if "published" in data:
            if "from" in data["published"]:
                if data["published"]["from"]:
                    result.started = data["published"]["from"].split("T")[0]
            if "to" in data["published"]:
                if data["published"]["to"]:
                    result.ended = data["published"]["to"].split("T")[0]
        if "authors" in data:
            authors = []
            for author in data["authors"]:
                authors.append(author["name"])
            result.authors = authors
    else:
        result.requestStatus = _responseParse(response)
    return result

def _fetchAMShared(data,initialResult): #this sets the properties that both anime and manga pages use, to save space.
    result = initialResult
    if "url" in data:
        result['page_url'] = data["url"]
    if "image_url" in data:
        result['thumb_url'] = data["image_url"]
    if "title" in data:
        result['title'] = data["title"]
    if "title_japanese" in data:
        result['title_ja'] = data["title_japanese"]
    if "type" in data:
        result['type_mal'] = data["type"]
    if "episodes" in data:
        result['episodes'] = data["episodes"]
    elif "chapters" in data:
        result['chapters'] = data["chapters"]
    if "status" in data:
        result['status'] = data["status"]
    if "synopsis" in data:
        result['synopsis'] = data["synopsis"]
    if "genres" in data:
        genres = []
        for genre in data["genres"]:
            genres.append(genre["name"])
        result['genres'] = genres
    return result

def search(query,type):
    query = requests.utils.quote(query,safe='')
    response = RLRequest(f'{api}/search/{type}?q={query}&page=1&limit=4')
    result = []
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            if len(data["results"]) > 0:
                for searchResult in data["results"]:
                    result.append([searchResult['title'],searchResult['type'],searchResult['image_url'],searchResult['mal_id']])
        result = [1,result]
    else:
        result = _responseParse(response)
    return result
