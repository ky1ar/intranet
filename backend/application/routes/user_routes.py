from flask import Blueprint, request, jsonify
from application.controllers.user_controller import UserController
from flask_jwt_extended import jwt_required


user_bp = Blueprint("user", __name__, url_prefix="/user")
controller = UserController()


@user_bp.route("/find", methods=["POST"])
def user_find():
    return controller.user_find(request.get_json())


@user_bp.route("/team/<user_id>", methods=["GET"])
def user_team(user_id):
    return controller.user_team(user_id)


@user_bp.route("/create_pin", methods=["POST"])
def user_create_pin():
    return controller.user_create_pin(request.get_json())


@user_bp.route("/login", methods=["POST"])
def user_login():
    return controller.user_login(request.get_json())


@user_bp.route("/verify", methods=["GET"])
@jwt_required()
def user_verify():
    return jsonify({
        "app_version": "0.4.0.0f"
    }), 200


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