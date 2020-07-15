import urllib.parse
import requests
from dotenv import load_dotenv
from os import path, getenv
from base64 import b64encode

# load .env file environments at the time of import
load_dotenv()


class Screenshot:
    def __init__(self):
        # accessing variables from .env file
        self.ACCESS_KEY = getenv('ACCESS_KEY')
        
    def take_screenshot(self, url):
        args = {
            'access_key': self.ACCESS_KEY,
            'url': url,
            # 'fullpage': '1',
            'viewport': '1920x1080',
            'format': 'PNG',
            'accept_lang': 'en'
            }
        query = urllib.parse.urlencode(args)
        response = requests.get(f"https://api.screenshotlayer.com/api/capture?{query}")

        with open(path.join('/Projects/firstFlaskApp/downloaded_image/image.png'), 'wb') as f:
            f.write(response.content)

        # response = (json if error, image if succcess)
        try:
            return response.json()
        except:
            return {
                'image': b64encode(response.content).decode('utf-8')   # converting to base64 bytes -> then string to make it JSON sereliazable
            }