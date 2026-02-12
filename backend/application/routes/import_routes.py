from flask import Blueprint, request
from application.controllers.import_controller import ImportController
from flask_jwt_extended import jwt_required


import_bp = Blueprint("import", __name__, url_prefix="/import")
controller = ImportController()


@import_bp.route("/status", methods=["GET"])
def status():
    return controller.import_status()


@import_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    return controller.import_dashboard()


@import_bp.route("/options/type", methods=["GET"])
def options_type():
    return controller.import_options_type()


@import_bp.route("/options/consumption", methods=["GET"])
def options_consumption():
    return controller.import_options_consumption()


@import_bp.route("/options/category", methods=["GET"])
def options_category():
    return controller.import_options_category()
