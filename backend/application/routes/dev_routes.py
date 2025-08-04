import logging
from flask import Blueprint, request
from application.controllers.dev_controller import DevController
from application import redis_client
from flask_socketio import emit
from application import socketio


dev_bp = Blueprint("dev", __name__, url_prefix="/dev")
controller = DevController()
connected_users = {}


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
def handle_disconnect(e=None):
    sid = request.sid
    for user_id, sids in connected_users.items():
        if sid in sids:
            sids.remove(sid)
            logging.info(f'🛑 Desconectado SID {sid} de user {user_id}')
            if not sids:
                del connected_users[user_id]
            break


@dev_bp.route("/", methods=["GET"])
def health():
    return {"message": "Krear 3D Backend API UP"}, 200


@dev_bp.route("/webhook", methods=["GET"])
def webhook():
    return controller.webhook(request.args)


@dev_bp.route("/webhook", methods=["POST"])
def webhook_data():
    return controller.webhook_data(request.get_json())


@dev_bp.route("/flush-redis", methods=["GET"])
def user_find():
    redis_client.flushall()
    return {"message": 'Redis flushed'}, 200


@dev_bp.route("/confirm_flow", methods=["POST"])
def confirm_flow():
    return controller.dev_confirm_flow(request.get_json())


@dev_bp.route("/confirm_flow/all", methods=["POST"])
def confirm_flow_all():
    return controller.dev_confirm_flow_all()


@dev_bp.route("/confirm_flow/list", methods=["GET"])
def confirm_flow_list():
    return controller.dev_confirm_flow_list()


@dev_bp.route("/confirm_flow/reminder", methods=["POST"])
def confirm_flow_reminder():
    return controller.dev_confirm_flow_reminder()


@dev_bp.route("/confirm_flow/reminder_2", methods=["POST"])
def confirm_flow_reminder_2():
    return controller.dev_confirm_flow_reminder_2()