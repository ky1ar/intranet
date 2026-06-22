from flask import Blueprint, request
from application.controllers.board_controller import BoardController
from flask_jwt_extended import jwt_required


board_bp = Blueprint("board", __name__, url_prefix="/board")
controller = BoardController()


@board_bp.route("/dashboard/<department_id>", methods=["GET"])
def board_dashboard(department_id):
    return controller.board_dashboard(department_id)


@board_bp.route("/issue", methods=["POST"])
def board_issue_add():
    return controller.board_issue_add(request.get_json())


@board_bp.route("/issue/update", methods=["POST"])
@jwt_required()
def board_issue_update():
    return controller.board_issue_update(request.get_json())


@board_bp.route("/issue/delete", methods=["POST"])
def board_issue_delete():
    return controller.board_issue_delete(request.get_json())


@board_bp.route("/issue/id/<issue_id>", methods=["GET"])
def board_issue_data(issue_id):
    return controller.board_issue_data(issue_id)


@board_bp.route("/issue/status", methods=["POST"])
def board_issue_status():
    return controller.board_issue_status(request.get_json())