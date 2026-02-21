from flask import Blueprint, request
from application.controllers.attendance_controller import AttendanceController
from flask_jwt_extended import jwt_required


attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")
controller = AttendanceController()


@attendance_bp.route("/xls", methods=["POST"])
def xls():
    return controller.attendance_xls(request)


@attendance_bp.route("/options/duration", methods=["GET"])
def duration():
    return controller.attendance_duration()


@attendance_bp.route("/options/leave", methods=["GET"])
def leave():
    return controller.attendance_leave()


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


@attendance_bp.route("/leave/<int:leave_id>", methods=["GET"])
@jwt_required()
def get_attendance_leave(leave_id):
    return controller.attendance_get_leave(leave_id)


@attendance_bp.route("/leave/requests", methods=["GET"])
@jwt_required()
def leave_requests():
    return controller.attendance_leave_requests()


@attendance_bp.route("/leave/request", methods=["POST"])
@jwt_required()
def leave_request():
    return controller.leave_request(request.get_json())


@attendance_bp.route("/leave/<int:leave_id>", methods=["PUT"])
@jwt_required()
def update_leave(leave_id):
    data = request.get_json()
    data["leave_id"] = leave_id
    return controller.leave_update(data)
