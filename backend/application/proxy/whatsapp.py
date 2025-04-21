import logging, requests, json
from application.handlers import handle_exceptions
from config import WABA as API


class Whatsapp:
    def __init__(self):
        self.token = API.TOKEN
        self.url = API.URL
        self.terms = API.SUPPORT_TERMS


    def post(self, payload):
        url = f"{self.url}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response_data = response.json()
        logging.info(response_data)
        if response.status_code != 200:
            return f"Error {response_data}", response.status_code
        
        return "Mensaje enviado correctamente", 200
    

    @handle_exceptions
    def new_order(self, data, client_name, machine_name):
        notes = data.get("notes")
        phone = data.get("phone")

        parameters = [
            {"type": "text", "parameter_name": "username", "text": client_name},
            {"type": "text", "parameter_name": "machine", "text": machine_name},
            {"type": "text", "parameter_name": "notes", "text": notes},
            {"type": "text", "parameter_name": "terms_link", "text": self.terms},
        ]

        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": "soporte_0_ingreso",
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]
            }
        }
        return self.post(payload)
    

    @handle_exceptions
    def new_order_alert(self, phone, order_number, machine_name):
        parameters = [
            {"type": "text", "parameter_name": "order_number", "text": order_number},
            {"type": "text", "parameter_name": "device_model", "text": machine_name},
        ]

        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": "soporte_0_alert",
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]
            }
        }
        return self.post(payload)
    