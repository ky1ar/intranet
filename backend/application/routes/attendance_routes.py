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
def period():
    offset = int(request.args.get("offset", 0))
    user_id = int(request.args.get("user_id"))
    data = {
        "offset": offset,
        "user_id": user_id
    }

    return controller.summary_by_offset(data)


@attendance_bp.route("/marks/complete", methods=["POST"])
@jwt_required()
def complete_marks():
    return controller.complete_marks(request.get_json())