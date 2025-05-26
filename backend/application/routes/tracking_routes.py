from flask import Blueprint, request
from application.controllers.tracking_controller import TrackingController

tracking_bp = Blueprint("tracking", __name__, url_prefix="/tracking")
controller = TrackingController()


@tracking_bp.route("/add", methods=["POST"])
def add():
    return controller.tracking_add(request.get_json())


@tracking_bp.route("/client", methods=["POST"])
def client_list():
    return controller.tracking_client_list(request.get_json())


@tracking_bp.route("/all", methods=["POST"])
def all_list():
    return controller.tracking_all_list()


@tracking_bp.route("/order", methods=["POST"])
def get_order():
    return controller.tracking_get_order(request.get_json())


@tracking_bp.route("/qr_data", methods=["POST"])
def get_qr_data():
    return controller.tracking_get_qr_data(request.get_json())


@tracking_bp.route("/force", methods=["POST"])
def force():
    return controller.tracking_force(request.get_json())