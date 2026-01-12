from flask import Blueprint, request
from application.controllers.attendance_controller import AttendanceController
from flask_jwt_extended import jwt_required


attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")
controller = AttendanceController()


@attendance_bp.route("/xls", methods=["POST"])
def xls():
    return controller.attendance_xls(request)