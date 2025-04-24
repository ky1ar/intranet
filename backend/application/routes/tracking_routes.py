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


@tracking_bp.route("/id/<tracking_order_id>", methods=["GET"])
def get_order(tracking_order_id):
    return controller.tracking_get_order(tracking_order_id)