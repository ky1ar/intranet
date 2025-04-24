import logging, requests, json
from datetime import datetime
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
        if response.status_code == 404:
            return "Tracking no encontrado", 404

        if response.status_code != 200:
            return "Error al consultar Olva API", 502
        
        olva_response = response.json()
        #logging.info(olva_response)

        data = olva_response.get('data')
        general = data.get('general')
        details = data.get('details')
        agency_at = None
        onway_at = None
        delivered_at = None
        last_status_id = None

        for item in details:
            if item.get('estado_tracking') == "RECEPCION TIENDA":
                agency_at = item.get('fecha_creacion')
                last_status_id = 1
                break
        
        for item in details:
            if item.get('estado_tracking') == "ASIGNADO":
                onway_at = item.get('fecha_creacion')
                last_status_id = 2
                break

        for item in details:
            if item.get('estado_tracking') == "ENTREGADO":
                delivered_at = item.get('fecha_creacion')
                last_status_id = 3
                break

        return {
            "origin_agency": general.get('origen').title(),
            "destination_agency": general.get('destino').title(),
            "status_data": {
                "agency_at": datetime.fromisoformat(agency_at) if agency_at else None,
                "onway_at": datetime.fromisoformat(onway_at) if onway_at else None,
                "delivered_at": datetime.fromisoformat(delivered_at) if delivered_at else None,
            },
            "last_status_id": last_status_id
        }, 200
    