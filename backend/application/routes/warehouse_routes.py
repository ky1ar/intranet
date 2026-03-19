from flask import Blueprint, request
from application.controllers.warehouse_controller import WarehouseController
from flask_jwt_extended import jwt_required

warehouse_bp = Blueprint("warehouse", __name__, url_prefix="/warehouse")
controller = WarehouseController()


@warehouse_bp.route("/find/<search>", methods=["GET"])
# @jwt_required()
def find_product(search):
    return controller.warehouse_find_product(search)


@warehouse_bp.route("/location/<label>", methods=["GET"])
# @jwt_required()
def get_location(label):
    return controller.warehouse_location_detail(label)


@warehouse_bp.route("/stock/remove", methods=["POST"])
# @jwt_required()
def remove_stock():
    return controller.warehouse_remove_stock(request.get_json())