from flask import Blueprint, request
from application.controllers.attendance_controller import AttendanceController
from flask_jwt_extended import jwt_required, get_jwt_identity


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


@attendance_bp.route("/options/department_team/<user_id>", methods=["GET"])
def department_team(user_id):
    return controller.attendance_department_team(user_id)


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


# ── Salary ─────────────────────────────────────────────────────

@attendance_bp.route("/salary/stats/calculate", methods=["POST"])
@jwt_required()
def salary_calculate_stats():
    data = request.get_json() or {}
    data["editor_user_id"] = int(get_jwt_identity())
    return controller.salary_calculate_stats(data)


@attendance_bp.route("/salary/calculate", methods=["POST"])
@jwt_required()
def salary_calculate():
    data = request.get_json() or {}
    data["editor_user_id"] = int(get_jwt_identity())
    return controller.salary_calculate(data)


@attendance_bp.route("/salary/recalculate/<int:salary_id>", methods=["POST"])
@jwt_required()
def salary_recalculate_single(salary_id):
    data = {
        "salary_id": salary_id,
        "editor_user_id": int(get_jwt_identity()),
    }
    return controller.salary_recalculate_single(data)


@attendance_bp.route("/salary/period/<int:period_id>", methods=["GET"])
@jwt_required()
def salary_get_period(period_id):
    return controller.salary_get_period(period_id)


@attendance_bp.route("/salary/user/<int:user_id>/period/<int:period_id>", methods=["GET"])
@jwt_required()
def salary_get_user(user_id, period_id):
    data = {
        "user_id": user_id,
        "period_id": period_id
    }
    return controller.salary_get_user(data)


@attendance_bp.route("/salary/config", methods=["POST"])
@jwt_required()
def salary_config_save():
    return controller.salary_config_save(request.get_json())


@attendance_bp.route("/salary/config/<int:user_id>", methods=["GET"])
@jwt_required()
def salary_config_get(user_id):
    return controller.salary_config_get(user_id)


@attendance_bp.route("/salary/bank-account/<int:user_id>", methods=["GET"])
@jwt_required()
def bank_account_get(user_id):
    return controller.bank_account_get(user_id)


@attendance_bp.route("/salary/bank-account", methods=["POST"])
@jwt_required()
def bank_account_save():
    return controller.bank_account_save(request.get_json())


@attendance_bp.route("/salary/approve/rrhh", methods=["POST"])
@jwt_required()
def salary_approve_rrhh():
    data = request.get_json() or {}
    data["approved_by"] = int(get_jwt_identity())
    return controller.salary_approve_rrhh(data)


@attendance_bp.route("/salary/approve/mgr", methods=["POST"])
@jwt_required()
def salary_approve_mgr():
    data = request.get_json() or {}
    data["approved_by"] = int(get_jwt_identity())
    return controller.salary_approve_mgr(data)


@attendance_bp.route("/salary/factor", methods=["POST"])
@jwt_required()
def salary_set_factor():
    data = request.get_json() or {}
    return controller.salary_set_factor(data)


@attendance_bp.route("/salary/adjustment", methods=["POST"])
@jwt_required()
def salary_set_adjustment():
    data = request.get_json() or {}
    data["adjusted_by"] = int(get_jwt_identity())
    return controller.salary_set_adjustment(data)


@attendance_bp.route("/salary/generate", methods=["POST"])
@jwt_required()
def salary_generate_file():
    return controller.salary_generate_file(request.get_json())


@attendance_bp.route("/salary/generate/bbva", methods=["POST"])
@jwt_required()
def salary_generate_bbva():
    return controller.salary_generate_bbva_cash(request.get_json())


# ── Leave Balance ──────────────────────────────────────────────

@attendance_bp.route("/leave/balance/<int:user_id>/period/<int:period_id>", methods=["GET"])
@jwt_required()
def leave_balance_get(user_id, period_id):
    return controller.leave_balance_get({"user_id": user_id, "period_id": period_id})


@attendance_bp.route("/leave/balance/adjust", methods=["POST"])
@jwt_required()
def leave_balance_adjust():
    data = request.get_json() or {}
    data["adjusted_by"] = int(get_jwt_identity())
    return controller.leave_balance_adjust(data)


# ── Medical Leave (Descanso Médico) ────────────────────────────

@attendance_bp.route("/leave/medical", methods=["POST"])
@jwt_required()
def medical_leave_request():
    return controller.medical_leave_request(request)


@attendance_bp.route("/leave/<int:leave_id>/attachments", methods=["GET"])
@jwt_required()
def leave_attachments(leave_id):
    return controller.get_leave_attachments(leave_id)


@attendance_bp.route("/leave/<int:leave_id>/attachments", methods=["POST"])
@jwt_required()
def add_leave_attachments(leave_id):
    return controller.add_leave_attachments(request)


@attendance_bp.route("/leave/attachment/<int:attachment_id>", methods=["GET"])
def leave_attachment_file(attachment_id):
    disposition = request.args.get("disposition", "inline")
    return controller.get_leave_attachment_file(attachment_id, disposition)


@attendance_bp.route("/leave/attachment/<int:attachment_id>/preview", methods=["GET"])
@jwt_required()
def leave_attachment_preview(attachment_id):
    return controller.attachment_preview(attachment_id)


@attendance_bp.route("/leave/attachment/<int:attachment_id>", methods=["DELETE"])
@jwt_required()
def delete_leave_attachment(attachment_id):
    return controller.delete_leave_attachment(attachment_id)