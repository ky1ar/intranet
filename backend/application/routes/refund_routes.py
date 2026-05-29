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
    ct = request.content_type or ""
    if "multipart" in ct or "application/x-www-form-urlencoded" in ct:
        data = {k: v for k, v in request.form.items()}
        try:
            data["status_id"] = int(data["status_id"])
        except (KeyError, ValueError):
            pass
    else:
        data = request.get_json() or {}
    data["refund_id"] = refund_id
    return controller.update_status(data)


@refund_bp.route("/<int:refund_id>/order_number", methods=["PATCH"])
@jwt_required()
def edit_order_number(refund_id):
    return controller.edit_order_number(refund_id)


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


# ── Links ──

@refund_bp.route("/link", methods=["POST"])
@jwt_required()
def create_link():
    return controller.create_link()


@refund_bp.route("/link_history", methods=["GET"])
@jwt_required()
def link_history():
    return controller.link_history()


@refund_bp.route("/link/<int:link_id>", methods=["DELETE"])
@jwt_required()
def delete_link(link_id):
    return controller.delete_link(link_id)


@refund_bp.route("/link_verify", methods=["POST"])
def link_verify():
    return controller.verify_link(request.get_json() or {})


@refund_bp.route("/link_process", methods=["POST"])
def link_process():
    return controller.link_process(request.get_json() or {})


# ── Chat ──

@refund_bp.route("/chat/<int:refund_id>", methods=["POST"])
@jwt_required()
def chat(refund_id):
    data = request.get_json() or {}
    data["refund_id"] = refund_id
    return controller.chat(data)
