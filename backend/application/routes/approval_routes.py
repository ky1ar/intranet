from flask import Blueprint, request
from application.controllers.approval_controller import ApprovalController


approval_bp = Blueprint("approval", __name__, url_prefix="/approval")
controller = ApprovalController()


@approval_bp.route("/wp_profile/<int:wp_user_id>", methods=["GET"])
def get_wp_profile(wp_user_id):
    return controller.get_wp_profile({"wp_user_id": wp_user_id})


@approval_bp.route("/status", methods=["GET"])
def get_status():
    data = {
        "wp_user_id": request.args.get("wp_user_id", type=int),
        "type": request.args.get("type"),
    }
    return controller.get_request_status(data)


@approval_bp.route("/request", methods=["POST"])
def create_request():
    return controller.create_request(request.get_json())


@approval_bp.route("/list", methods=["GET"])
def list_requests():
    data = {"status": request.args.get("status")}
    return controller.get_all_requests(data)


@approval_bp.route("/approve", methods=["POST"])
def approve():
    return controller.approve_request(request.get_json())


@approval_bp.route("/reject", methods=["POST"])
def reject():
    return controller.reject_request(request.get_json())
