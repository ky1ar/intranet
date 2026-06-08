from flask import Blueprint, request
from application.controllers.tracking_controller import TrackingController

tracking_bp = Blueprint("tracking", __name__, url_prefix="/tracking")
controller = TrackingController()


@tracking_bp.route("/add", methods=["POST"])
def add():
    return controller.tracking_add(request.get_json())


@tracking_bp.route("/dashboard", methods=["GET"])
def dashboard():
    return controller.tracking_dashboard()


@tracking_bp.route("/order_id/<order_id>", methods=["GET"])
def get_order_by_id(order_id):
    return controller.tracking_get_order_by_id(order_id)


@tracking_bp.route("/qr_data", methods=["POST"])
def get_qr_data():
    return controller.tracking_get_qr_data(request.get_json())


@tracking_bp.route("/force", methods=["POST"])
def force():
    return controller.tracking_force(request.get_json())


@tracking_bp.route("/shalom", methods=["POST"])
def shalom():
    return controller.tracking_shalom(request.get_json())

    
@tracking_bp.route("/force/all", methods=["POST"])
def force_all():
    return controller.tracking_force_all()


@tracking_bp.route("/client", methods=["POST"])##
def client_list():
    return controller.tracking_client_list(request.get_json())


@tracking_bp.route("/client/order", methods=["POST"])##
def get_order():
    return controller.tracking_get_order(request.get_json())


@tracking_bp.route("/history", methods=["GET"])
def history():
    payload = {
        "page": int(request.args.get("page", 1)),
        "per_page": int(request.args.get("per_page", 12))
    }
    return controller.tracking_history(payload)


@tracking_bp.route("/statistics", methods=["GET"])
def statistics():
    return controller.tracking_statistics()


@tracking_bp.route("/find/<order_number>", methods=["GET"])
def find_order(order_number):
    return controller.tracking_find_order(order_number)