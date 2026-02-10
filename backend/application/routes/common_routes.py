
from flask import Blueprint
from application.controllers.common_controller import CommonController


common_bp = Blueprint("common", __name__, url_prefix="/common")
controller = CommonController()


@common_bp.route("/workers", methods=["GET"])
def workers():
    return controller.common_workers()


@common_bp.route("/vendors", methods=["GET"])
def vendors():
    return controller.common_vendors()


@common_bp.route("/departments", methods=["GET"])
def departments():
    return controller.common_departments()


@common_bp.route("/provinces/<department_id>", methods=["GET"])
def provinces(department_id):
    return controller.common_provinces(department_id)


@common_bp.route("/districts/<province_id>", methods=["GET"])
def districts(province_id):
    return controller.common_districts(province_id)