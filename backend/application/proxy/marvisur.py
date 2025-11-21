import logging, requests, json
from datetime import datetime
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
        
        marvisur_response = response.json()
        logging.info(marvisur_response)

        if marvisur_response.get('success') == False:
            return "Códigos de tracking incorrectos", 404
        
        origin_agency = ''
        destination_agency = ''
        agency_at = None
        onway_at = None
        delivered_at = None
        last_status_id = None

        marvisur_data = marvisur_response.get('data').get('Table')
        for item in marvisur_data:
            if item.get('COMENTARIO') == "RECEPCION":
                origin_agency = item.get('DEPORIGEN', '').title()
                destination_agency = item.get('DEPDESTINO', '').title()
                agency_at = item.get('FECEVENTO')
                last_status_id = 1
                break
        
        for item in marvisur_data:
            if item.get('COMENTARIO') == "EN RUTA":
                onway_at = item.get('FECEVENTO')
                last_status_id = 2
                break

        for item in marvisur_data:
            if item.get('COMENTARIO') == "ENTREGADO":
                delivered_at = item.get('FECEVENTO')
                last_status_id = 3
                break


        return {
            "origin_agency": origin_agency,
            "destination_agency": destination_agency,
            "status_data": {
                "agency_at": datetime.fromisoformat(agency_at) if agency_at else None,
                "onway_at": datetime.fromisoformat(onway_at) if onway_at else None,
                "delivered_at": datetime.fromisoformat(delivered_at) if delivered_at else None,
            },
            "last_status_id": last_status_id
        }, 200