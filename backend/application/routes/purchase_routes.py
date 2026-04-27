from flask import Blueprint, request
from application.controllers.purchase_controller import PurchaseController
from flask_jwt_extended import jwt_required


purchase_bp = Blueprint("purchase", __name__, url_prefix="/purchases")
controller = PurchaseController()


@purchase_bp.route("/options/type", methods=["GET"])
#@jwt_required()
def type_options():
    return controller.purchase_type_options()


@purchase_bp.route("/options/urgency", methods=["GET"])
#@jwt_required()
def urgency_options():
    return controller.purchase_urgency_options()


@purchase_bp.route("/requests", methods=["GET"])
@jwt_required()
def requests():
    return controller.purchase_requests()


@purchase_bp.route("/<int:purchase_id>", methods=["GET"])
@jwt_required()
def get_purchase(purchase_id):
    return controller.purchase_get(purchase_id)


@purchase_bp.route("/<int:purchase_id>", methods=["PUT"])
@jwt_required()
def update_purchase(purchase_id):
    data = request.get_json()
    data["purchase_id"] = purchase_id
    return controller.purchase_update(data)


@purchase_bp.route("/process", methods=["POST"])
@jwt_required()
def process():
    return controller.purchase_process(request.get_json())


@purchase_bp.route("/find/<string:query>", methods=["GET"])
@jwt_required()
def find_purchases(query):
    return controller.purchase_find(query)


@purchase_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    page = max(1, request.args.get("page", 1, type=int))
    return controller.purchase_history(page)


@purchase_bp.route("/<int:purchase_id>/chat", methods=["POST"])
@jwt_required()
def send_chat(purchase_id):
    data = request.get_json() or {}
    data["purchase_id"] = purchase_id
    return controller.purchase_send_chat(data)