from flask import Blueprint, request
from application.controllers.tracking_controller import TrackingController

tracking_bp = Blueprint("tracking", __name__, url_prefix="/tracking")
controller = TrackingController()


@tracking_bp.route("/add", methods=["POST"])
def add():
    return controller.tracking_add(request.get_json())


@tracking_bp.route("/list", methods=["POST"])
def list():
    return controller.tracking_list(request.get_json())


@tracking_bp.route("/order_number/<order_number>", methods=["GET"])
def get_order(order_number):
    return controller.tracking_get_order(order_number)