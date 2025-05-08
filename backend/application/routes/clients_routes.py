from flask import Blueprint, request, jsonify
from application.controllers.clients_controller import ClientsController


client_bp = Blueprint("client", __name__, url_prefix="/client")
controller = ClientsController()


@client_bp.route("/data/<document>", methods=["GET"])
def user_data_document(document):
    return controller.user_data_document(document)


@client_bp.route("/name/<document>", methods=["GET"])
def user_name(document):
    return controller.user_name(document)


@client_bp.route("/all", methods=["GET"])
def clients_all():
    body = {
        "page": int(request.args.get("page", 1)),
        "per_page": int(request.args.get("per_page", 20))

    }
    return controller.clients_all(body)


@client_bp.route("/order_number/<order_number>", methods=["GET"])
def get_user_order(order_number):
    return controller.order_get_user_order(order_number)