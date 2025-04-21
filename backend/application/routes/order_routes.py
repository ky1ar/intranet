from flask import Blueprint, request
from application.controllers.order_controller import OrderController

order_bp = Blueprint("order", __name__, url_prefix="/order")
controller = OrderController()


@order_bp.route("/id/<order_number>", methods=["GET"])
def get_user_order(order_number):
    return controller.order_get_user_order(order_number)