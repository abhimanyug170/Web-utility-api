from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
from hashlib import sha256
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
        shortUrl = None
        # return jsonify({
        #     'shortUrl': longUrl
        # })
        # generate short-url for url provided
        # hashing
        ret = []
        while(True):
            hashedUrl = sha256(longUrl.encode()).hexdigest()
            # convert to base 62
            base_62 = [1,2,3,4,5,5,67,7,8]
            if(hashedUrl == 0):
                shortUrl = 0
            else:
                # while(hashedUrl):
                #     base_62.append(hashedUrl % 62)
                #     hashedUrl //= 62
                shortUrl = "".join(map(str, base_62[:7]))

            # find if this shortUrl exist
            arr = urlMap.find({"_id": shortUrl})
            
            # unique url generated
            # make database entry
            res = [i for i in arr]
            if(not res):    
                urlMap.insert({
                    "_id": shortUrl,
                    "longUrl": longUrl
                })
                return jsonify({
                    'shortUrl': shortUrl,
                    'status': 200
                })

class getLongUrl(Resource):
    def get(self):
        postedData = request.get_json()
        shortUrl = postedData["shortUrl"]

        # find if this shortUrl exist
        arr = urlMap.find({"_id": shortUrl})
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
    app.run()





"""
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDatabase
users = db["Users"]

class Register(Resource):
    def post(self):
        #Step 1 is to get posted data by the user
        postedData = request.get_json()

        #Get the data
        username = postedData["username"]
        password = postedData["password"] #"123xyz"


        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        #Store username and pw into the database
        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Sentence": "",
            "Tokens":6
        })

        retJson = {
            "status": 200,
            "msg": "You successfully signed up for the API"
        }
        return jsonify(retJson)

def verifyPw(username, password):
    hashed_pw = users.find({
        "Username":username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def countTokens(username):
    tokens = users.find({
        "Username":username
    })[0]["Tokens"]
    return tokens

class Store(Resource):
    def post(self):
        #Step 1 get the posted data
        postedData = request.get_json()

        #Step 2 is to read the data
        username = postedData["username"]
        password = postedData["password"]
        sentence = postedData["sentence"]

        #Step 3 verify the username pw match
        correct_pw = verifyPw(username, password)

        if not correct_pw:
            retJson = {
                "status":302
            }
            return jsonify(retJson)
        #Step 4 Verify user has enough tokens
        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status": 301
            }
            return jsonify(retJson)

        #Step 5 store the sentence, take one token away  and return 200OK
        users.update({
            "Username":username
        }, {
            "$set":{
                "Sentence":sentence,
                "Tokens":num_tokens-1
                }
        })

        retJson = {
            "status":200,
            "msg":"Sentence saved successfully"
        }
        return jsonify(retJson)

class Get(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        #Step 3 verify the username pw match
        correct_pw = verifyPw(username, password)
        if not correct_pw:
            retJson = {
                "status":302
            }
            return jsonify(retJson)

        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status": 301
            }
            return jsonify(retJson)

        #MAKE THE USER PAY!
        users.update({
            "Username":username
        }, {
            "$set":{
                "Tokens":num_tokens-1
                }
        })



        sentence = users.find({
            "Username": username
        })[0]["Sentence"]
        retJson = {
            "status":200,
            "sentence": str(sentence)
        }

        return jsonify(retJson)




api.add_resource(Register, '/register')
api.add_resource(Store, '/store')
api.add_resource(Get, '/get')


if __name__=="__main__":
    app.run(host='0.0.0.0')
"""