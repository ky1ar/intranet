import logging
from flask import Blueprint, request
from config import Wordpress
from application.controllers.wordpress_controller import WordpressController


wordpress_bp = Blueprint("wordpress", __name__, url_prefix="/wordpress")
controller = WordpressController()


def _authorized():
    """Valida el secreto compartido con WordPress. Solo se exige si WP_WEBHOOK_SECRET
    está configurado, de modo que el webhook de checkout siga operando mientras se
    despliega el plugin actualizado en producción."""
    expected = Wordpress.WEBHOOK_SECRET
    if not expected:
        return True
    return request.headers.get("X-K3D-Secret") == expected


@wordpress_bp.route("/order-complete", methods=["POST"])
def order_complete():
    if not _authorized():
        return {"data": {"message": "No autorizado"}, "success": False}, 401
    return controller.wordpres_order_complete(request.get_json())


@wordpress_bp.route("/order-status", methods=["POST"])
def order_status():
    if not _authorized():
        return {"data": {"message": "No autorizado"}, "success": False}, 401
    return controller.wordpress_order_status(request.get_json())
