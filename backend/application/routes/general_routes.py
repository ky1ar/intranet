
from flask import Blueprint
from application.controllers.general_controller import GeneralController


general_bp = Blueprint("general", __name__, url_prefix="/general")
controller = GeneralController()


@general_bp.route("/service_status", methods=["GET"])
def service_status():
    return controller.general_service_status()


@general_bp.route("/service_methods", methods=["GET"])
def service_methods():
    return controller.general_service_methods()


@general_bp.route("/service_origin", methods=["GET"])
def service_origin():
    return controller.general_service_origin()


@general_bp.route("/technicians", methods=["GET"])
def general_technicians():
    return controller.general_technicians()


@general_bp.route("/tracking_agencies", methods=["GET"])
def tracking_agencies():
    return controller.general_tracking_agencies()


@general_bp.route("/tracking_status", methods=["GET"])
def tracking_status():
    return controller.general_tracking_status()


@general_bp.route("/drivers", methods=["GET"])
def general_drivers():
    return controller.general_drivers()


@general_bp.route("/vendors", methods=["GET"])
def general_vendors():
    return controller.general_vendors()


@general_bp.route("/districts", methods=["GET"])
def general_districts():
    return controller.general_districts()


@general_bp.route("/shipping_types", methods=["GET"])
def general_shipping_types():
    return controller.general_shipping_types()


@general_bp.route("/board_priority", methods=["GET"])
def general_board_priority():
    return controller.general_board_priority()


@general_bp.route("/board_statuses", methods=["GET"])
def general_board_statuses():
    return controller.general_board_statuses()


@general_bp.route("/questions", methods=["GET"])
def general_questions():
    return controller.general_questions()