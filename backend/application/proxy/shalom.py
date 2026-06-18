import logging, requests, time, hmac, hashlib, uuid, base64, json, unicodedata
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from config import Shalom as API


WEB_HEADERS = {
    "Origin": "https://shalom.com.pe",
    "Referer": "https://shalom.com.pe/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/148.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
}

SHALOM_AES_KEY = base64.b64decode("uQn/bQ94PXBEfId70zjN+VE1hSU7kh9VBXTOUd68Ssc=")

class Shalom:
    def __init__(self):
        self.tracking_url = API.TRACK_URL
        self.state_url = API.STATE_URL


    def get_token(self):
        secret = b".Ov3rsku112024l4r43l."
        u = str(uuid.uuid4())
        exp = int(time.time()) + 30

        base = f"web-{u}@{exp}"
        sig = hmac.new(secret, base.encode("utf-8"), hashlib.sha256).hexdigest()

        return f"{base}@{sig}"


    def _headers(self):
        return {**WEB_HEADERS, "Authorization": f"Bearer {self.get_token()}"}


    @staticmethod
    def _decrypt(data_b64):
        raw = base64.b64decode(data_b64)
        iv, ciphertext = raw[:16], raw[16:]
        decryptor = Cipher(algorithms.AES(SHALOM_AES_KEY), modes.CBC(iv)).decryptor()
        padded = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = PKCS7(128).unpadder()
        plaintext = unpadder.update(padded) + unpadder.finalize()
        logging.info(f"[DECRYPT] {plaintext.decode()}")
        return json.loads(plaintext)


    @classmethod
    def _envelope(cls, shalom_response):
        """Devuelve la respuesta completa ({success, message, data}), descifrándola si viene cifrada.

        Shalom puede anidar el cifrado (el texto plano vuelve a ser un sobre
        {encrypted, data}); se descifra en bucle hasta llegar al envelope real.
        """
        while isinstance(shalom_response, dict) and shalom_response.get("encrypted"):
            shalom_response = cls._decrypt(shalom_response.get("data"))
        return shalom_response


    def tracking(self, code1, code2):
        payload = {
            "numero": code1,
            "codigo": code2,
        }
        response = requests.post(self.tracking_url, data=payload, headers=self._headers())
        if response.status_code != 200:
            return "Error al consultar Shalom API", 502

        shalom_response = response.json()
        envelope = self._envelope(shalom_response)
        if envelope.get('success') == False:
            return "Códigos de tracking incorrectos", 404

        shalom_data = envelope.get('data') or {}
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


    def tracking_ose_id(self, ose_id):
        payload = {
            "ose_id": ose_id
        }
        response = requests.post(self.tracking_url, data=payload, headers=self._headers())
        if response.status_code != 200:
            return "Error al consultar Shalom API", 502

        shalom_response = response.json()
        logging.info(shalom_response)

        envelope = self._envelope(shalom_response)
        if envelope.get('success') == False:
            return "Códigos de tracking incorrectos", 404

        data = envelope.get('data') or {}
        result = {
            "client_document": data.get("destinatario", {}).get("documento"),
            "numero_orden": data.get("numero_orden"),
            "codigo_orden": data.get("codigo_orden"),
            "agency": "1",
        }
        return result, 200


    def tracking_status(self, external_id):
        payload = {
            'ose_id': external_id
        }
        response = requests.post(self.state_url, data=payload, headers=self._headers())
        if response.status_code != 200:
            return "Error al consultar Shalom API", 502

        shalom_response = response.json()
        envelope = self._envelope(shalom_response)
        data = envelope.get('data') or {}

        origen = data.get('origen')
        transito = data.get('transito')
        destino = data.get('destino')
        entregado = data.get('entregado')
        
        agency_at = None
        onway_at = None
        arrived_at = None
        delivered_at = None
        last_status_id = None

        if origen:
            agency_at = origen.get('fecha')
            last_status_id = 1
        
        if transito:
            onway_at = transito.get('fecha')
            last_status_id = 2

        if destino:
            arrived_at = destino.get('fecha')
            last_status_id = 3

        if entregado:
            delivered_at = entregado.get('fecha')
            last_status_id = 4

        return {
            "status_data": {
                "agency_at": datetime.strptime(agency_at, "%Y-%m-%d %H:%M:%S") if agency_at else None,
                "onway_at": datetime.strptime(onway_at, "%Y-%m-%d %H:%M:%S") if onway_at else None,
                "arrived_at": datetime.strptime(arrived_at, "%Y-%m-%d %H:%M:%S") if arrived_at else None,
                "delivered_at": datetime.strptime(delivered_at, "%Y-%m-%d %H:%M:%S") if delivered_at else None,
            },
            "last_status_id": last_status_id
        }, 200
    