import logging
from flask import Blueprint, request
from application.controllers.wordpress_controller import WordpressController


wordpress_bp = Blueprint("wordpress", __name__, url_prefix="/wordpress")
controller = WordpressController()


@wordpress_bp.route("/order-complete", methods=["POST"])
def order_complete():
    return controller.wordpres_order_complete(request.get_json())

