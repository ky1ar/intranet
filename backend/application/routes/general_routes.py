from flask import Blueprint, request
from application.controllers.general_controller import GeneralController

general_bp = Blueprint("general", __name__, url_prefix="/general")
controller = GeneralController()


@general_bp.route("/service_status", methods=["GET"])
def service_status():
    return controller.general_service_status()


@general_bp.route("/service_methods", methods=["GET"])
def service_methods():
    return controller.general_service_methods()


@general_bp.route("/technicians", methods=["GET"])
def general_technicians():
    return controller.general_technicians()


@general_bp.route("/tracking_agencies", methods=["GET"])
def tracking_agencies():
    return controller.general_tracking_agencies()