from flask import Blueprint, request
from application.controllers.attendance_controller import AttendanceController
from flask_jwt_extended import jwt_required


attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")
controller = AttendanceController()


@attendance_bp.route("/xls", methods=["POST"])
def xls():
    return controller.attendance_xls(request)


@attendance_bp.route("/period", methods=["GET"])
@jwt_required()
def logistic_dashboard_day():
    offset = request.args.get("offset", "0")
    return controller.summary_by_offset(int(offset))