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
@jwt_required()
def remove_stock():
    return controller.warehouse_remove_stock(request.get_json())


@warehouse_bp.route("/stock/add", methods=["POST"])
@jwt_required()
def add_stock():
    return controller.warehouse_add_stock(request.get_json())


@warehouse_bp.route("/stock/move", methods=["POST"])
@jwt_required()
def move_stock():
    return controller.warehouse_move_stock(request.get_json())


@warehouse_bp.route("/machines/search", methods=["GET"])
# @jwt_required()
def search_machines():
    return controller.warehouse_search_machines(request.args.get("q", ""))


@warehouse_bp.route("/load", methods=["POST"])
@jwt_required()
def load_excel():
    file = request.files.get("file")
    if not file:
        return "No se recibió ningún archivo", 400
    return controller.warehouse_load_excel(file.read())


@warehouse_bp.route("/logs", methods=["GET"])
@jwt_required()
def get_logs():
    page = request.args.get("page", 1, type=int)
    return controller.warehouse_get_logs(page)


@warehouse_bp.route("/statistics", methods=["GET"])
@jwt_required()
def statistics():
    return controller.warehouse_statistics()


@warehouse_bp.route("/locations/occupied", methods=["GET"])
def get_occupied_locations():
    return controller.warehouse_get_occupied_locations()


@warehouse_bp.route("/picking", methods=["GET"])
def picking_plan():
    return controller.warehouse_picking_plan(request.args.get("number"))


@warehouse_bp.route("/picking/complete", methods=["POST"])
@jwt_required()
def picking_complete():
    return controller.warehouse_complete_picking(request.get_json())