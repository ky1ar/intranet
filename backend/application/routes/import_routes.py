from flask import Blueprint, request
from application.controllers.import_controller import ImportController
from flask_jwt_extended import jwt_required


import_bp = Blueprint("import", __name__, url_prefix="/imports")
controller = ImportController()


@import_bp.route("/status", methods=["GET"])
def status():
    return controller.import_status()


@import_bp.route("/provider/<provider_id>", methods=["GET"])
def get_provider(provider_id):
    return controller.import_get_provider(provider_id)


@import_bp.route("/view/<import_id>", methods=["GET"])
def view(import_id):
    return controller.import_view(import_id)


@import_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    return controller.import_dashboard()


@import_bp.route("/pending", methods=["GET"])
def pendings():
    return controller.import_pendings()


@import_bp.route("/new", methods=["POST"])
@jwt_required()
def new():
    return controller.import_new(request.get_json())


@import_bp.route("/move", methods=["POST"])
@jwt_required()
def move():
    return controller.import_move(request.get_json())


@import_bp.route("/down", methods=["POST"])
@jwt_required()
def down():
    return controller.import_down(request.get_json())


@import_bp.route("/options/provider", methods=["GET"])
def options_provider():
    return controller.import_options_provider()


@import_bp.route("/options/type", methods=["GET"])
def options_type():
    return controller.import_options_type()


@import_bp.route("/options/business", methods=["GET"])
def options_business():
    return controller.import_options_business()


@import_bp.route("/options/incoterm", methods=["GET"])
def options_incoterm():
    return controller.import_options_incoterm()


@import_bp.route("/options/port", methods=["GET"])
def options_port():
    return controller.import_options_port()


@import_bp.route("/attachments/<int:import_id>", methods=["GET"])
@jwt_required()
def attachments_list(import_id):
    return controller.import_attachments_list(import_id)


@import_bp.route("/attachments", methods=["POST"])
@jwt_required()
def attachments_upload():
    return controller.import_attachments_upload()


@import_bp.route("/attachment/<int:attachment_id>", methods=["GET"])
# @jwt_required()
def attachment_stream(attachment_id):
    return controller.import_attachment_stream(attachment_id)


@import_bp.route("/attachment/<int:attachment_id>/preview", methods=["GET"])
@jwt_required()
def attachment_preview(attachment_id):
    return controller.import_attachment_preview(attachment_id)


@import_bp.route("/chat/<int:import_id>", methods=["POST"])
@jwt_required()
def chat(import_id):
    data = request.get_json() or {}
    data["import_id"] = import_id
    return controller.import_chat(data)


@import_bp.route("/draft/<int:import_id>/agents", methods=["PUT"])
@jwt_required()
def draft_update_agents(import_id):
    data = request.get_json() or {}
    data["import_id"] = import_id
    return controller.import_draft_update_agents(data)


@import_bp.route("/draft/<int:import_id>", methods=["DELETE"])
@jwt_required()
def draft_delete(import_id):
    return controller.import_draft_delete({"import_id": import_id})