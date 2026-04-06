from flask import Blueprint, request
from application.controllers.module_controller import ModuleController
from flask_jwt_extended import jwt_required, get_jwt_identity

module_bp = Blueprint("modules", __name__, url_prefix="/modules")
controller = ModuleController()


# ── Usuario autenticado ────────────────────────────────────────────────────

@module_bp.route("/me", methods=["GET"])
@jwt_required()
def get_my_modules():
    user_id = int(get_jwt_identity())
    return controller.get_my_modules(user_id)


@module_bp.route("/me/default", methods=["PUT"])
@jwt_required()
def set_default():
    data = request.get_json()
    data['user_id'] = int(get_jwt_identity())
    return controller.set_default(data)


@module_bp.route("/me/sort", methods=["PUT"])
@jwt_required()
def update_sort_order():
    data = request.get_json()
    data['user_id'] = int(get_jwt_identity())
    return controller.update_sort_order(data)


@module_bp.route("/me/pin", methods=["PUT"])
@jwt_required()
def toggle_pin():
    data = request.get_json()
    data['user_id'] = int(get_jwt_identity())
    return controller.toggle_pin(data)


# ── Admin ──────────────────────────────────────────────────────────────────

@module_bp.route("/catalog", methods=["GET"])
@jwt_required()
def get_all_modules():
    return controller.get_all_modules()


@module_bp.route("/admin/access", methods=["POST"])
@jwt_required()
def set_user_access():
    return controller.set_user_access(request.get_json())


@module_bp.route("/admin/permissions", methods=["POST"])
@jwt_required()
def set_user_permissions():
    return controller.set_user_permissions(request.get_json())