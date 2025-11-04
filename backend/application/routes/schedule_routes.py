from flask import Blueprint, request, jsonify
from application.controllers.schedule_controller import ScheduleController
from flask_jwt_extended import jwt_required


schedule_bp = Blueprint("schedule", __name__, url_prefix="/schedule")
controller = ScheduleController()


@schedule_bp.route("/month", methods=["GET"])
def get_month():
    offset = request.args.get('offset', None)
    return controller.schedule_get_month(offset)


@schedule_bp.route("/process", methods=["POST"])
def process():
    return controller.schedule_process(request.get_json())


@schedule_bp.route("/delete", methods=["POST"])
def delete():
    return controller.schedule_delete(request.get_json())


@schedule_bp.route("/event/<event_id>", methods=["GET"])
def data(event_id):
    return controller.schedule_data(event_id)


@schedule_bp.route("/options/visibility", methods=["GET"])
def get_visibility():
    return controller.schedule_get_visibility()


@schedule_bp.route("/options/repeat", methods=["GET"])
def get_repeat():
    return controller.schedule_get_repeat()


@schedule_bp.route("/options/notify", methods=["GET"])
def get_notify():
    return controller.schedule_get_notify()