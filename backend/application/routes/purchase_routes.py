from flask import Blueprint, request
from application.controllers.purchase_controller import PurchaseController
from flask_jwt_extended import jwt_required


purchase_bp = Blueprint("purchase", __name__, url_prefix="/purchase")
controller = PurchaseController()


@purchase_bp.route("/requests", methods=["GET"])
#@jwt_required()
def requests():
    return controller.purchase_requests()


@purchase_bp.route("/options/type", methods=["GET"])
#@jwt_required()
def type_options():
    return controller.purchase_type_options()


@purchase_bp.route("/options/urgency", methods=["GET"])
#@jwt_required()
def urgency_options():
    return controller.purchase_urgency_options()


@purchase_bp.route("/process", methods=["POST"])
#@jwt_required()
def process():
    return controller.purchase_process(request.get_json())


@purchase_bp.route("/approve", methods=["POST"])
@jwt_required()
def approve():
    return controller.purchase_approve(request.get_json())
