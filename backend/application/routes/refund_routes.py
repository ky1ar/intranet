from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from application.controllers.refund_controller import RefundController

refund_bp = Blueprint("refund", __name__, url_prefix="/refund")
controller = RefundController()


@refund_bp.route("/statuses", methods=["GET"])
def statuses():
    return controller.get_statuses()


@refund_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    return controller.dashboard()


@refund_bp.route("/<int:refund_id>", methods=["GET"])
@jwt_required()
def get_refund(refund_id):
    return controller.get_refund(refund_id)


@refund_bp.route("/", methods=["POST"])
@jwt_required()
def create():
    return controller.create()


@refund_bp.route("/<int:refund_id>/status", methods=["PUT"])
@jwt_required()
def update_status(refund_id):
    data = request.get_json() or {}
    data["refund_id"] = refund_id
    return controller.update_status(data)


@refund_bp.route("/<int:refund_id>/penalty", methods=["PATCH"])
@jwt_required()
def update_penalty(refund_id):
    return controller.update_penalty(refund_id)


@refund_bp.route("/<int:refund_id>", methods=["DELETE"])
@jwt_required()
def delete(refund_id):
    return controller.delete(refund_id)


# ── Attachments ──

@refund_bp.route("/attachments", methods=["POST"])
@jwt_required()
def attachments_upload():
    return controller.attachments_upload()


@refund_bp.route("/attachment/<int:attachment_id>", methods=["GET"])
def attachment_stream(attachment_id):
    return controller.attachment_stream(attachment_id)


@refund_bp.route("/attachment/<int:attachment_id>/preview", methods=["GET"])
@jwt_required()
def attachment_preview(attachment_id):
    return controller.attachment_preview(attachment_id)


@refund_bp.route("/attachment/<int:attachment_id>", methods=["DELETE"])
@jwt_required()
def delete_attachment(attachment_id):
    return controller.delete_attachment(attachment_id)


# ── Chat ──

@refund_bp.route("/chat/<int:refund_id>", methods=["POST"])
@jwt_required()
def chat(refund_id):
    data = request.get_json() or {}
    data["refund_id"] = refund_id
    return controller.chat(data)
