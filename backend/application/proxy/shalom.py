import logging, requests, json
from datetime import datetime
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

        shalom_response = response.json()
        #logging.info(shalom_response)

        if shalom_response.get('success') == False:
            return "Códigos de tracking incorrectos", 404
        
        shalom_data = shalom_response.get('data')
        shalom_origin = shalom_data.get('origen')
        shalom_destination = shalom_data.get('destino')
        external_id = shalom_data.get('ose_id')

        result = {
            "origin_agency": f"{shalom_origin.get('nombre')}, {shalom_origin.get('departamento')}".title(),
            "destination_agency": f"{shalom_destination.get('nombre')}, {shalom_destination.get('departamento')}".title(),
            "external_id": external_id
        }
        tracking_status, tracking_code = self.tracking_status(external_id)
        if tracking_code != 200:
            return "Error al consultar Shalom API", 502
        result.update(tracking_status)
        return result, 200


    def tracking_status(self, external_id):
        payload = {
            'ose_id': external_id
        }
            
        response = requests.post(self.state_url, data=payload)
        if response.status_code != 200:
            return "Error al consultar Shalom API", 502
        
        olva_response = response.json()
        #logging.info(olva_response)

        data = olva_response.get('data')
        origen = data.get('origen')
        transito = data.get('transito')
        entregado = data.get('entregado')

        agency_at = None
        onway_at = None
        delivered_at = None
        last_status_id = None

        if origen:
            agency_at = origen.get('fecha')
            last_status_id = 1
        
        if transito:
            onway_at = transito.get('fecha')
            last_status_id = 2

        if entregado:
            delivered_at = entregado.get('fecha')
            last_status_id = 3

        return {
            "status_data": {
                "agency_at": datetime.strptime(agency_at, "%Y-%m-%d %H:%M:%S") if agency_at else None,
                "onway_at": datetime.strptime(onway_at, "%Y-%m-%d %H:%M:%S") if onway_at else None,
                "delivered_at": datetime.strptime(delivered_at, "%Y-%m-%d %H:%M:%S") if delivered_at else None,
            },
            "last_status_id": last_status_id
        }, 200
    