from flask import Blueprint, request
from application.controllers.conversation_controller import ConversationController

conversation_bp = Blueprint("conversations", __name__, url_prefix="/conversations")
controller = ConversationController()


@conversation_bp.route("", methods=["GET"])
def get_conversations():
    return controller.get_conversations({})


@conversation_bp.route("/<wa_id>/messages", methods=["GET"])
def get_messages(wa_id):
    return controller.get_messages({"wa_id": wa_id})


@conversation_bp.route("/reply", methods=["POST"])
def send_reply():
    return controller.send_reply(request.get_json())
