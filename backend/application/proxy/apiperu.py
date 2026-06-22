import logging, requests, json

from application import redis_client
from config import ApiPeru as API


class ApiPeru:
    def __init__(self):
        self.token = API.TOKEN
        self.url = API.URL


    def post(self, path, data):
        url = f"{self.url}{path}"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        logging.info(headers)
        logging.info(data)

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            logging.info(response.json())
            return response.json().get("data"), 200
        return None, 400


    def get_name(self, type, document):
        key = f"{type}:{document}"
        cache = redis_client.get(key)
        if cache:
            logging.info('User data loaded from cache')
            return {"name": cache}, 200
        
        if type == 'dni':
            consult_dni, consult_status = self.post("dni", {"dni": document})
            if consult_status != 200:
                return consult_dni, consult_status
            
            name = (f"{consult_dni.get('nombres')} {consult_dni.get('apellido_paterno')} {consult_dni.get('apellido_materno')}").title()
            redis_client.set(key, name)
            return {"name": name}, 200

        consult_ruc, consult_status = self.post("ruc", {"ruc": document})
        if consult_status != 200:
            return consult_ruc, consult_status
        
        name = consult_ruc.get("nombre_o_razon_social").title()
        redis_client.set(key, name)
        return {"name": name}, 200


    