from flask import Blueprint, request, jsonify
from application.controllers.clients_controller import ClientsController


clients_bp = Blueprint("clients", __name__, url_prefix="/clients")
controller = ClientsController()


@clients_bp.route("/all", methods=["GET"])
def clients_all():
    body = {
        "page": int(request.args.get("page", 1)),
        "per_page": int(request.args.get("per_page", 20))

    }
    return controller.clients_all(body)
