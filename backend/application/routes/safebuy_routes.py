from flask import Blueprint, request
from application.controllers.safebuy_controller import SafebuyController
from flask_jwt_extended import jwt_required, get_jwt_identity

safebuy_bp = Blueprint("safebuy", __name__, url_prefix="/safebuy")
controller = SafebuyController()


@safebuy_bp.route("/statuses", methods=["GET"])
def statuses():
    return controller.get_statuses()


@safebuy_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    return controller.dashboard()


@safebuy_bp.route("/request/<int:request_id>", methods=["GET"])
@jwt_required()
def get_request(request_id):
    return controller.get_request(request_id)


@safebuy_bp.route("/request", methods=["POST"])
def create_request():
    return controller.create_request()


@safebuy_bp.route("/request/<int:request_id>/status", methods=["PUT"])
@jwt_required()
def update_status(request_id):
    data = request.get_json()
    data["request_id"] = request_id
    data["user_id"] = int(get_jwt_identity())
    return controller.update_status(data)


@safebuy_bp.route("/request/<int:request_id>", methods=["PUT"])
@jwt_required()
def update_request(request_id):
    return controller.update_request(request_id, request.get_json())


@safebuy_bp.route("/request/<int:request_id>/credit", methods=["POST"])
@jwt_required()
def apply_credit(request_id):
    data = request.get_json()
    data["request_id"] = request_id
    data["applied_by"] = int(get_jwt_identity())
    return controller.apply_credit(data)


@safebuy_bp.route("/request/<int:request_id>", methods=["DELETE"])
@jwt_required()
def delete_request(request_id):
    return controller.delete_request(request_id)


# ── Attachments ──

@safebuy_bp.route("/attachments", methods=["POST"])
@jwt_required()
def attachments_upload():
    return controller.attachments_upload()


@safebuy_bp.route("/attachment/<int:attachment_id>", methods=["GET"])
def attachment_stream(attachment_id):
    return controller.attachment_stream(attachment_id)


@safebuy_bp.route("/attachment/<int:attachment_id>/preview", methods=["GET"])
@jwt_required()
def attachment_preview(attachment_id):
    return controller.attachment_preview(attachment_id)


# ── Chat ──

@safebuy_bp.route("/chat/<int:request_id>", methods=["POST"])
@jwt_required()
def chat(request_id):
    data = request.get_json() or {}
    data["request_id"] = request_id
    return controller.chat(data)