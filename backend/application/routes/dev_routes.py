import logging
from flask import Blueprint, request
from application import redis_client
from flask_socketio import emit
from application import socketio


dev_bp = Blueprint("dev", __name__, url_prefix="/dev")


@dev_bp.route("/", methods=["GET"])
def health():
    return {"message": "Krear 3D Backend API UP"}, 200


@dev_bp.route("/flush-redis", methods=["GET"])
def user_find():
    redis_client.flushall()
    return {"message": 'Redis flushed'}, 200


@socketio.on("connect")
def handle_connect():
    logging.info("Cliente conectado")
    emit("server_response", {"message": "Conectado al servidor"})


@socketio.on("disconnect")
def handle_disconnect():
    logging.info("Cliente desconectado")


@socketio.on("support_dashboard_update")
def handle_update(data):
    #controller.send_message(data)
    emit("support_dashboard_update", {}, broadcast=True)