from flask import Flask, jsonify, request, send_from_directory, current_app
from flask_restful import Api, Resource
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
        while True:
            hashedUrl = sha256(longUrl.encode()).hexdigest()
            shortUrl = (
                "http://"
                + request.remote_addr
                + "/g/"
                + (
                    base64.b64encode(hashedUrl.encode())[-6:-2]
                    .decode()
                    .replace("=", "-")
                    .replace("/", "_")
                )
            )  # last 1 or 2 characters are always going to be '=' padding

            # find if this shortUrl exist and make database entry
            find_result = urlMap.find_one({"_id": shortUrl})

            if not find_result:
                urlMap.insert({"_id": shortUrl, "longUrl": longUrl})
                return jsonify({"shortUrl": shortUrl, "status": 200})
            # if URL calculated previously
            elif find_result["longUrl"] == longUrl:
                return jsonify({"shortUrl": shortUrl, "status": 200})
            # collision occur (same last digits for 2 url hashes)
            else:
                temp_url = longUrl + str(random.randint(0, 10 ** 2))
                hashedUrl = sha256(temp_url.encode()).hexdigest()
                shortUrl = (
                    "http://"
                    + request.remote_addr
                    + "/g/"
                    + (
                        base64.b64encode(hashedUrl.encode())[-6:-2]
                        .decode()
                        .replace("=", "-")
                        .replace("/", "_")
                    )
                )

                # find if this shortUrl exist and make database entry
                find_result = urlMap.find_one({"_id": shortUrl})
                if not find_result:
                    urlMap.insert({"_id": shortUrl, "longUrl": longUrl})
                    return jsonify({"shortUrl": shortUrl, "status": 200})
                # if URL calculated previously
                elif find_result["longUrl"] == longUrl:
                    return jsonify({"shortUrl": shortUrl, "status": 200})


class GetLongUrl(Resource):
    def get(self, shortUrl):
        # find if this shortUrl exist
        arr = urlMap.find_one({"_id": shortUrl})
        if not arr:
            # return error msg
            return jsonify({"msg": "URL not found in DataBase", "status": 404})
        else:
            longUrl = arr[0]["longUrl"]
            # return long url
            return jsonify({"longUrl": longUrl, "status": 200})


class GetScreenshot(Resource):
    # download image
    def get(self):
        return send_from_directory(
            os.path.join("/Projects/firstFlaskApp/downloaded_image/"),
            "image.png",
            as_attachment=True,
        )

    # return thumbnail
    def post(self):
        postedData = request.get_json()
        url = postedData["url"]

        result = Screenshot.Screenshot().take_screenshot(url)
        if "error" in result:
            return jsonify(
                {"msg": result["error"]["info"], "status": result["error"]["code"]}
            )
        else:
            return jsonify({"image": 1234, "status": 200})  # result['image'],


api.add_resource(GetShortUrl, "/get-short-url")
api.add_resource(GetLongUrl, "/g/<string:shortUrl>")
api.add_resource(GetScreenshot, "/get-screenshot")


if __name__ == "__main__":
    app.run(port=5000)
