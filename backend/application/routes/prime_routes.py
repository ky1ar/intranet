from flask import Blueprint
from application.controllers.prime_controller import PrimeController
from flask_jwt_extended import jwt_required

prime_bp = Blueprint("prime", __name__, url_prefix="/api/prime")
prime_controller = PrimeController()

# --- Rutas Públicas (Webhooks y API para WP) ---

# Endpoint para recibir los eventos de Culqi
@prime_bp.route("/webhook", methods=["POST"])
def webhook():
    return prime_controller.webhook()

# Endpoint para WooCommerce (verificar si un correo es Prime)
@prime_bp.route("/verify", methods=["GET"])
def verify():
    return prime_controller.verify()

# --- Rutas Protegidas (Para el Frontend de la Intranet) ---

# Listar todas las suscripciones (con filtros)
@prime_bp.route("/list", methods=["GET"])
@jwt_required()
def get_all():
    return prime_controller.get_all()
