import logging, requests, json

from config import Shalom as API


class Shalom:
    def __init__(self):
        self.tracking_url = API.TRACK_URL
        self.state_url = API.STATE_URL


    def tracking(self, code1, code2):
        payload = {
            "numero": code1,
            "codigo": code2,
        }
        response = requests.post(self.tracking_url, data=payload)

        if response.status_code != 200:
            return "Error al consultar Shalom API", 502
        logging.info(response.json())
        return response.json(), 200
