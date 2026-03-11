from flask import Blueprint
from application.controllers.warehouse_controller import WarehouseController
from flask_jwt_extended import jwt_required


warehouse_bp = Blueprint("warehouse", __name__, url_prefix="/warehouse")
controller = WarehouseController()


@warehouse_bp.route("/find/<search>", methods=["GET"])
# @jwt_required()
def find_product(search):
    return controller.warehouse_find_product(search)

