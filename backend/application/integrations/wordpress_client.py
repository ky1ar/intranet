import logging
import requests
from config import Wordpress


class WordpressClient:
    """Cliente ligero para consultar WordPress/WooCommerce bajo demanda. Usa un
    endpoint REST propio del plugin (k3d/v1/order-status), protegido con el secreto
    compartido, en lugar de la WooCommerce REST API (no requiere consumer keys)."""

    def __init__(self):
        self.base_url = (Wordpress.BASE_URL or "").rstrip("/")
        self.secret = Wordpress.WEBHOOK_SECRET

    def get_order_status(self, wc_order_id):
        """Devuelve (status, 200) o (mensaje, código) ante error."""
        if not self.base_url:
            return "WordPress no está configurado", 503
        url = f"{self.base_url}/wp-json/k3d/v1/order-status/{wc_order_id}"
        headers = {"Accept": "application/json"}
        if self.secret:
            headers["X-K3D-Secret"] = self.secret
        try:
            resp = requests.get(url, headers=headers, timeout=12)
        except requests.RequestException:
            logging.exception("Error consultando estado en WordPress para %s", wc_order_id)
            return "No se pudo conectar con WordPress", 502
        if resp.status_code == 404:
            return "Pedido no encontrado en WordPress", 404
        if resp.status_code != 200:
            logging.error("WordPress devolvió %s para el pedido %s", resp.status_code, wc_order_id)
            return "WordPress devolvió un error", 502
        try:
            data = resp.json()
        except ValueError:
            return "Respuesta inválida de WordPress", 502
        status = data.get("status")
        if not status:
            return "WordPress no devolvió el estado", 502
        return status, 200
