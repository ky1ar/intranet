import logging, requests, json

from config import Olva as API


class Olva:
    def __init__(self):
        self.tracking_url = API.TRACK_URL
        self.api_key = API.API_KEY


    def tracking(self, code1, code2):
        params = {
            'tracking': code1,
            'emision': code2,
            'apikey': self.api_key,
            'details': 1
        }
            
        response = requests.get(self.tracking_url, params=params)
        if response.status_code != 200:
            return "Error al consultar Olva API", response.status_code
        logging.info(response.json())
        return response.json(), 200
