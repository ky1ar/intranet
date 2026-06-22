from flask import Blueprint, request, jsonify
from application.controllers.user_controller import UserController
from flask_jwt_extended import jwt_required, get_jwt_identity


user_bp = Blueprint("user", __name__, url_prefix="/user")
controller = UserController()


@user_bp.route("/find", methods=["POST"])
def user_find():
    return controller.user_find(request.get_json())


@user_bp.route("/team/<user_id>", methods=["GET"])
def user_team(user_id):
    return controller.user_team(user_id)


@user_bp.route("/attendance_team/<user_id>", methods=["GET"])
def user_attendance_team(user_id):
    return controller.user_attendance_team(user_id)


@user_bp.route("/create_pin", methods=["POST"])
def user_create_pin():
    return controller.user_create_pin(request.get_json())


@user_bp.route("/login", methods=["POST"])
def user_login():
    return controller.user_login(request.get_json())


@user_bp.route("/verify", methods=["GET"])
@jwt_required()
def user_verify():
    return controller.user_verify()


@user_bp.route("/logout", methods=["POST"])
def user_logout():
    return controller.user_logout(request.get_json())


@user_bp.route("/send_otp", methods=["POST"])
def user_send_otp():
    return controller.user_send_otp(request.get_json())


@user_bp.route("/validate_otp", methods=["POST"])
def user_validate_otp():
    return controller.user_validate_otp(request.get_json())


@user_bp.route("/register_device", methods=["POST"])
@jwt_required()
def user_register_device():
    return controller.register_device(request.get_json())


@user_bp.route("/upload_avatar", methods=["POST"])
@jwt_required()
def upload_avatar():
    from application.services.user_service import UserService
    from application.response import Response
    user_id = int(get_jwt_identity())
    file = request.files.get("avatar")
    if not file:
        return jsonify({"success": False, "data": "Archivo requerido"}), 400
    result, code = UserService().upload_avatar(user_id, file)
    fmt = Response()
    if code != 200:
        return fmt.error(result, code)
    return fmt.success(result)