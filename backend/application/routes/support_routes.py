from flask import Blueprint, request
from application.controllers.support_controller import SupportController

support_bp = Blueprint("support", __name__, url_prefix="/support")
controller = SupportController()


@support_bp.route("/dashboard", methods=["GET"])
def dashboard():
    return controller.support_dashboard()


@support_bp.route("/order_number/<number>", methods=["GET"])
def service_order_by_number(number):
    return controller.support_service_order_by_number(number)


@support_bp.route("/order/next", methods=["POST"])
def service_order_next():
    return controller.support_service_order_next(request.get_json())


@support_bp.route("/order/prev", methods=["POST"])
def service_order_prev():
    return controller.support_service_order_prev(request.get_json())


@support_bp.route("/order/update", methods=["POST"])
def service_order_update():
    return controller.support_service_order_update(request.get_json())


@support_bp.route("/process", methods=["POST"])
def service_process():
    return controller.support_service_process(request.get_json())


@support_bp.route("/consult", methods=["POST"])
def order_consult():
    return controller.support_order_consult(request.get_json())


@support_bp.route("/history", methods=["GET"])
def history():
    payload = {
        "page": int(request.args.get("page", 1)),
        "per_page": int(request.args.get("per_page", 12))
    }
    return controller.support_history(payload)
