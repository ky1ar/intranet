from flask import Blueprint, request, jsonify
from application.controllers.user_controller import UserController
from flask_jwt_extended import jwt_required


user_bp = Blueprint("user", __name__, url_prefix="/user")
controller = UserController()


@user_bp.route("/find", methods=["POST"])
def user_find():
    return controller.user_find(request.get_json())


@user_bp.route("/team", methods=["POST"])
def user_team():
    return controller.user_team(request.get_json())


@user_bp.route("/data/<document>", methods=["GET"])
def user_data_document(document):
    return controller.user_data_document(document)


@user_bp.route("/name/<document>", methods=["GET"])
def user_name(document):
    return controller.user_name(document)


@user_bp.route("/create_pin", methods=["POST"])
def user_create_pin():
    return controller.user_create_pin(request.get_json())


@user_bp.route("/login", methods=["POST"])
def user_login():
    return controller.user_login(request.get_json())


@user_bp.route("/verify", methods=["GET"])
@jwt_required()
def user_verify():
    return jsonify({"message": "Token válido"}), 200


@user_bp.route("/logout", methods=["POST"])
def user_logout():
    return controller.user_logout(request.get_json())

