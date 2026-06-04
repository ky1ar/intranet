import logging, requests, time, hmac, hashlib, uuid, base64, json, unicodedata
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from config import Shalom as API


# Shalom filtra en el edge (HAProxy). Sin estos headers el LB devuelve 503
# "No server is available to handle this request" antes de llegar al backend.
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

# Key AES-256 (base64) extraída del bundle del front (clase rf / EncryptionService).
# Cuando la respuesta trae "encrypted": true, "data" viene como:
#   base64( IV[16 bytes] + ciphertext ), AES-256-CBC, padding PKCS7.
SHALOM_AES_KEY = base64.b64decode("uQn/bQ94PXBEfId70zjN+VE1hSU7kh9VBXTOUd68Ssc=")

# El endpoint /estados ya no devuelve el timeline (origen/transito/destino/...).
# Ahora el estado actual viene en el campo "message" del response. Mapeo a tu
# esquema interno de status_id (1-4). Claves normalizadas (sin acentos, minúsculas).
#   Registrado        -> 1  (aún no en agencia; se mapea al piso = 1)
#   En origen         -> 1
#   En tránsito       -> 2
#   Demora de envíos  -> 2  (demora en tránsito)
#   En destino        -> 3
#   En reparto        -> 3  (reparto a domicilio; tu esquema no tiene paso aparte)
#   Entregado         -> 4
SHALOM_STATUS_MAP = {
    "registrado": 1,
    "en origen": 1,
    "en transito": 2,
    "demora de envios": 2,
    "en destino": 3,
    "en reparto": 3,
    "entregado": 4,
}

# status_id -> campo de fecha en status_data
_STATUS_FIELD = {1: "agency_at", 2: "onway_at", 3: "arrived_at", 4: "delivered_at"}


def _normalize(text):
    text = (text or "").strip().lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


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
        return json.loads(plaintext)


    @classmethod
    def _data(cls, shalom_response):
        """Devuelve el dict 'data', descifrándolo si viene cifrado."""
        data = shalom_response.get("data")
        if shalom_response.get("encrypted"):
            return cls._decrypt(data)
        return data


    def tracking(self, code1, code2):
        payload = {
            "numero": code1,
            "codigo": code2,
        }
        response = requests.post(self.tracking_url, data=payload, headers=self._headers())
        if response.status_code != 200:
            return "Error al consultar Shalom API", 502

        shalom_response = response.json()
        logging.info(shalom_response)

        if shalom_response.get('success') == False:
            return "Códigos de tracking incorrectos", 404

        shalom_data = self._data(shalom_response)
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

        if shalom_response.get('success') == False:
            return "Códigos de tracking incorrectos", 404

        data = self._data(shalom_response)
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
        logging.info(shalom_response)

        # El estado actual viene en "message"; "data" solo trae la fecha del evento.
        message = shalom_response.get('message')
        data = self._data(shalom_response) or {}

        last_status_id = SHALOM_STATUS_MAP.get(_normalize(message))
        if last_status_id is None:
            logging.warning("Estado de Shalom no reconocido: %r", message)
            return f"Estado de Shalom no reconocido: {message}", 502

        fecha = data.get('fecha')
        event_at = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S") if fecha else None

        # Solo hay una fecha (el evento actual). El timeline completo ya no lo
        # entrega Shalom, así que se llena únicamente el campo del estado vigente.
        status_data = {
            "agency_at": None,
            "onway_at": None,
            "arrived_at": None,
            "delivered_at": None,
        }
        status_data[_STATUS_FIELD[last_status_id]] = event_at

        return {
            "status_data": status_data,
            "last_status_id": last_status_id
        }, 200