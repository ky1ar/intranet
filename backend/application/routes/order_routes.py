from flask import Blueprint, request
from application.controllers.order_controller import OrderController


order_bp = Blueprint("order", __name__, url_prefix="/order")
controller = OrderController()


@order_bp.route("/dashboard", methods=["GET"])
def dashboard():
    return controller.get_dashboard({})


@order_bp.route("/find/<term>", methods=["GET"])
def find(term):
    return controller.search_orders(term)


@order_bp.route("/history", methods=["GET"])
def history():
    payload = {
        "page": int(request.args.get("page", 1)),
        "per_page": int(request.args.get("per_page", 12)),
    }
    return controller.history(payload)


@order_bp.route("/status", methods=["POST"])
def change_status():
    return controller.change_status(request.get_json())


@order_bp.route("/<int:order_id>", methods=["GET"])
def get_detail(order_id):
    return controller.get_order_detail({"order_id": order_id})
