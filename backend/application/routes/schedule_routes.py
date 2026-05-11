import logging

from flask import Blueprint, request, jsonify
from application.controllers.schedule_controller import ScheduleController
from flask_jwt_extended import jwt_required, get_jwt_identity


schedule_bp = Blueprint("schedule", __name__, url_prefix="/schedule")
controller = ScheduleController()


@schedule_bp.route("/month", methods=["GET"])
@jwt_required()
def get_month():
    logging.info("tes")
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


@schedule_bp.route("/options/colors", methods=["GET"])
def get_colors():
    return controller.schedule_get_colors()


@schedule_bp.route("/notifications/upcoming", methods=["POST"])
def notify_upcoming():
    return controller.schedule_notify_upcoming()


@schedule_bp.route("/options/users", methods=["GET"])
def get_users():
    return controller.schedule_get_users()


@schedule_bp.route("/options/departments", methods=["GET"])
def get_departments():
    return controller.schedule_get_departments()


@schedule_bp.route("/room", methods=["POST"])
@jwt_required()
def room_process():
    data = request.get_json() or {}
    return controller.schedule_room_process(data)


@schedule_bp.route("/room/<int:booking_id>", methods=["DELETE"])
@jwt_required()
def room_delete(booking_id):
    user_id = int(get_jwt_identity())
    return controller.schedule_room_delete(booking_id, user_id)