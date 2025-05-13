import logging
from flask import Blueprint, request
from application import redis_client
from flask_socketio import emit
from application import socketio


dev_bp = Blueprint("dev", __name__, url_prefix="/dev")

connected_users = {}

@dev_bp.route("/", methods=["GET"])
def health():
    return {"message": "Krear 3D Backend API UP"}, 200


@dev_bp.route("/flush-redis", methods=["GET"])
def user_find():
    redis_client.flushall()
    return {"message": 'Redis flushed'}, 200


@socketio.on("connect")
def handle_connect():
    user_id = request.args.get('user_id')
    sid = request.sid
    logging.info(f"Usuario {user_id} conectado: SID {sid}")

    if user_id:
        connected_users.setdefault(user_id, []).append(sid)
        logging.info(f"Total conexiones activas para {user_id}: {len(connected_users[user_id])}")
    #emit("server_response", {"message": "Conectado al servidor"})


@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    for user_id, sids in connected_users.items():
        if sid in sids:
            sids.remove(sid)
            logging.info(f'🛑 Desconectado SID {sid} de user {user_id}')
            if not sids:
                del connected_users[user_id]
            break


@socketio.on("support_dashboard_update")
def handle_update(data):
    #controller.send_message(data)
    emit("support_dashboard_update", {}, broadcast=True)