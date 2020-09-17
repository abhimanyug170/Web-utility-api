from flask import Flask, jsonify, request, send_from_directory, current_app, redirect
from flask_restful import Api, Resource, abort
from pymongo import MongoClient
from hashlib import sha256

# retreive .env file
from dotenv import load_dotenv
import os

import random
import base64
import json

# handle cors error
from flask_cors import CORS

# import required classes
import Screenshot

app = Flask(__name__)
CORS(app)
api = Api(app)

client = MongoClient("mongodb://localhost:27017")
db = client["urlDB"]
urlMap = db["urlMap"]


class GetShortUrl(Resource):
    def post(self):
        postedData = request.get_json()
        longUrl = postedData["longUrl"]
        shortUrl = 0

        # generate short-url for url provided
        # by hashing
        hashedUrl = sha256(longUrl.encode()).hexdigest()
        shortUrl = base64.b64encode(hashedUrl.encode())[-6:-2].decode().replace("=", "-").replace("/", "_")
        # last 1 or 2 characters are always going to be '=' padding

        # put if absent (atomic instruction)
        urlMap.update_one({"_id": shortUrl}, {"$set": {"longUrl": longUrl}}, upsert = True)
        
        returnUrl = request.host_url + "g/" + shortUrl
        return jsonify({"shortUrl": returnUrl, "status": 200})


class GetLongUrl(Resource):
    def get(self, shortUrl):
        # find if this shortUrl exist
        arr = urlMap.find_one({"_id": shortUrl})
        if not arr:
            # return error msg
            return jsonify({"msg": "URL not found in DataBase", "status": 404})
        else:
            longUrl = arr["longUrl"]
            if(longUrl[:4] != "http"):
                longUrl = "http://" + longUrl
            return redirect(longUrl, code=303)


class GetScreenshot(Resource):
    # download image
    def get(self):
        try:
            return send_from_directory(
                os.path.join("./downloaded_image/"),  #os.path.join("/Projects/web-utility/server/downloaded_image/"),
                "image.png",
                as_attachment=True,
            )
        except:
            abort(404, description = "File not found")

    # return thumbnail
    def post(self):
        postedData = request.get_json()
        url = postedData["url"]

        result = Screenshot.Screenshot().take_screenshot(url)
        
        if "error" in result:
            return jsonify({
                "msg": result["error"]["info"], 
                "status": result["error"]["code"]
            })
        else:
            return jsonify({
                "image": result['image'],
                "status": 200
            })


api.add_resource(GetShortUrl, "/get-short-url")
api.add_resource(GetLongUrl, "/g/<shortUrl>")
api.add_resource(GetScreenshot, "/get-screenshot")


if __name__ == "__main__":
    app.run(port=5000)
