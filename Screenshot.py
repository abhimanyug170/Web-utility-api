import urllib.parse
import requests
from dotenv import load_dotenv
import os
from base64 import b64encode

from PIL import Image

# for BytesIO wrapper to convert bytes-image to file pointer
import io

# load .env file environments at the time of import
load_dotenv()


class Screenshot:
    def __init__(self):
        # accessing variables from .env file
        self.ACCESS_KEY = os.getenv('ACCESS_KEY')
        
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
        
        try:
            os.mkdir("./downloaded_image")
        except:
            pass
        
        # response = (json if error, image if succcess)
        try:
            return response.json()
        except:
            with open(os.path.join('./downloaded_image/image.png'), 'wb') as f:
                f.write(response.content)
            # image = Image.open(io.BytesIO(response.content), mode="r")
            # image.save(os.path.join('./downloaded_image/image_downsize.png'), quality = 50, optimize = True)



            return {
                'image': b64encode(response.content).decode('utf-8')   # converting to base64 bytes -> then string to make it JSON sereliazable
            }