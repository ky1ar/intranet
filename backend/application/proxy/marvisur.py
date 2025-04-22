import logging, requests, json

from config import Marvisur as API


class Marvisur:
    def __init__(self):
        self.tracking_url = API.TRACK_URL


    def tracking(self, code1, code2):
        payload = {
            "serie": code1,
            "numero": code2,
            "modo": 1
        }
        response = requests.post(self.tracking_url, json=payload)
        if response.status_code != 200:
            return "Error al consultar Marvisur API", 502
        logging.info(response.json())
        return response.json(), 200
