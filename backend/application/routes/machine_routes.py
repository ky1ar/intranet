from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from application.controllers.machine_controller import MachineController


machine_bp = Blueprint("machine", __name__, url_prefix="/machine")
controller = MachineController()


# ---------------------------------------------------------------- búsqueda
@machine_bp.route("/find/<machine_name>", methods=["GET"])
def machine_find_machines(machine_name):
    return controller.machine_find_machines(machine_name)


# ----------------------------------------------------------------- listado
@machine_bp.route("/list", methods=["GET"])
@jwt_required()
def list_machines():
    payload = {
        "page": int(request.args.get("page", 1)),
        "per_page": int(request.args.get("per_page", 12)),
        "q": request.args.get("q") or None,
        "category_id": request.args.get("category_id", type=int),
        "brand_id": request.args.get("brand_id", type=int),
    }
    return controller.list_machines(payload)


# -------------------------------------------------------------- categorías
@machine_bp.route("/categories", methods=["GET"])
@jwt_required()
def list_categories():
    return controller.list_categories()


@machine_bp.route("/categories", methods=["POST"])
@jwt_required()
def create_category():
    return controller.create_category(request.get_json() or {})


@machine_bp.route("/categories/<int:category_id>", methods=["PUT"])
@jwt_required()
def update_category(category_id):
    data = request.get_json() or {}
    data["id"] = category_id
    return controller.update_category(data)


# ------------------------------------------------------------------ marcas
@machine_bp.route("/brands", methods=["GET"])
@jwt_required()
def list_brands():
    return controller.list_brands()


@machine_bp.route("/brands", methods=["POST"])
@jwt_required()
def create_brand():
    return controller.create_brand(request.get_json() or {})


@machine_bp.route("/brands/<int:brand_id>", methods=["PUT"])
@jwt_required()
def update_brand(brand_id):
    data = request.get_json() or {}
    data["id"] = brand_id
    return controller.update_brand(data)


# ----------------------------------------------------------------- machine
@machine_bp.route("", methods=["POST"])
@machine_bp.route("/", methods=["POST"])
@jwt_required()
def create_machine():
    data = request.form.to_dict()
    data["image_file"] = request.files.get("image")
    return controller.create_machine(data)


@machine_bp.route("/<int:machine_id>", methods=["GET"])
@jwt_required()
def get_machine(machine_id):
    return controller.get_machine(machine_id)


@machine_bp.route("/<int:machine_id>", methods=["PUT"])
@jwt_required()
def update_machine(machine_id):
    data = request.form.to_dict()
    data["image_file"] = request.files.get("image")
    data["id"] = machine_id
    return controller.update_machine(data)
