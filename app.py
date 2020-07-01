from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
from hashlib import sha256
import random
import base64
import json

app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://localhost:27017')
db = client['urlDB']
urlMap = db['urlMap']


class getShortUrl(Resource):
    def post(self):
        postedData = request.get_json()
        longUrl = postedData["longUrl"]
        shortUrl = 0

        # generate short-url for url provided
        # by hashing
        while(True):
            hashedUrl = sha256(longUrl.encode()).hexdigest()
            shortUrl = base64.b64encode(hashedUrl.encode())[-6:-2].decode().replace('=', '-').replace('/', '_')    # last 1 or 2 characters are always going to be '=' padding

            # convert to base 62
            # base_62 = []
            # if(hashedUrl == 0):
            #     shortUrl = 0
            # else:
            #     # while(hashedUrl):
            #     #     base_62.append(hashedUrl % 62)
            #     #     hashedUrl //= 62
            #     shortUrl = hashedUrl[:7]

            # find if this shortUrl exist and make database entry
            find_result = urlMap.find_one({"_id": shortUrl})
            
            if(not find_result):    
                urlMap.insert({
                    "_id": shortUrl,
                    "longUrl": longUrl
                })
                return jsonify({
                    'shortUrl': shortUrl,
                    'status': 200
                })
            # if URL calculated previously
            elif(find_result["longUrl"] == longUrl):
                return jsonify({
                    'shortUrl': shortUrl,
                    'status': 200
                })
            # collision occur (same last digits for 2 url hashes)
            else:
                temp_url = longUrl + str(random.randint(0, 10**2))
                hashedUrl = sha256(temp_url.encode()).hexdigest()
                shortUrl = base64.b64encode(hashedUrl.encode())[-6:-2].decode().replace('=', '-').replace('/', '_')

                # find if this shortUrl exist and make database entry
                find_result = urlMap.find_one({"_id": shortUrl})
                if(not find_result):    
                    urlMap.insert({
                        "_id": shortUrl,
                        "longUrl": longUrl
                    })
                    return jsonify({
                        'shortUrl': shortUrl,
                        'status': 200
                    })
                # if URL calculated previously
                elif(find_result["longUrl"] == longUrl):
                    return jsonify({
                        'shortUrl': shortUrl,
                        'status': 200
                    })


class getLongUrl(Resource):
    def post(self):
        postedData = request.get_json()
        shortUrl = postedData["shortUrl"]

        # find if this shortUrl exist
        arr = list(urlMap.find({"_id": shortUrl}))
        if(not arr):
            # return error msg
            return jsonify({
                "msg": "URL not found in DataBase",
                "status": 404
            })
        else:
            longUrl = arr[0]["longUrl"]
            # return long url
            return jsonify({
                "longUrl": longUrl,
                "status": 200
            })


api.add_resource(getShortUrl, "/getShortUrl")
api.add_resource(getLongUrl, "/getLongUrl")

if(__name__ == "__main__"):
    app.run(port=5000)