from flask import Blueprint, request
from application.controllers.complaint_controller import ComplaintController
from flask_jwt_extended import jwt_required


complaint_bp = Blueprint("complaint", __name__, url_prefix="/complaint")
controller = ComplaintController()


@complaint_bp.route("/status", methods=["GET"])
#@jwt_required()
def status():
    return controller.complaint_status()


@complaint_bp.route("/view/<complaint_id>", methods=["GET"])
@jwt_required()
def view(complaint_id):
    return controller.complaint_view(complaint_id)


@complaint_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    return controller.complaint_dashboard()


@complaint_bp.route("/new", methods=["POST"])
# @jwt_required()
def new():
    return controller.complaint_new(request.get_json())


@complaint_bp.route("/move", methods=["POST"])
@jwt_required()
def move():
    return controller.complaint_move(request.get_json())


@complaint_bp.route("/attachments/<int:complaint_id>", methods=["GET"])
@jwt_required()
def attachments_list(complaint_id):
    return controller.attachments_list(complaint_id)


@complaint_bp.route("/attachments/<int:complaint_id>", methods=["POST"])
@jwt_required()
def attachments_upload(complaint_id):
    return controller.attachments_upload(complaint_id)


@complaint_bp.route("/attachment/<int:attachment_id>", methods=["GET"])
# @jwt_required()
def attachment_stream(attachment_id):
    return controller.attachment_stream(attachment_id)


@complaint_bp.route("/attachment/<int:attachment_id>/preview", methods=["GET"])
@jwt_required()
def attachment_preview(attachment_id):
    return controller.attachment_preview(attachment_id)


@complaint_bp.route("/options/type", methods=["GET"])
# @jwt_required()
def options_type():
    return controller.complaint_options_type()


@complaint_bp.route("/options/consumption", methods=["GET"])
# @jwt_required()
def options_consumption():
    return controller.complaint_options_consumption()


@complaint_bp.route("/options/category", methods=["GET"])
# @jwt_required()
def options_category():
    return controller.complaint_options_category()


@complaint_bp.route("/chat/<int:complaint_id>", methods=["POST"])
@jwt_required()
def chat(complaint_id):
    data = request.get_json() or {}
    data["complaint_id"] = complaint_id
    return controller.complaint_chat(data)