import os, logging

from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from application.controllers.logistic_controller import LogisticController
from flask_jwt_extended import jwt_required
from flask_socketio import emit, join_room, leave_room
from application import socketio
from config import Config
from PIL import Image

logistic_bp = Blueprint("logistic", __name__)
controller = LogisticController()


@logistic_bp.route("/", methods=["GET"])
def health():
    return {"message": "Logistica Backend API UP",}, 200


#@logistic_bp.route("/user/<document>", methods=["GET"])
#def user_get_by_document(document):
#    return controller.user_get_by_document(document)


@logistic_bp.route("/general/drivers", methods=["GET"])
def general_drivers():
    return controller.general_drivers()


@logistic_bp.route("/general/vendors", methods=["GET"])
def general_vendors():
    return controller.general_vendors()


@logistic_bp.route("/general/districts", methods=["GET"])
def general_districts():
    return controller.general_districts()


@logistic_bp.route("/general/shipping_types", methods=["GET"])
def general_shipping_types():
    return controller.general_shipping_types()


@logistic_bp.route("/order/process", methods=["POST"])
def order_process():
    return controller.order_process(request.get_json())


@logistic_bp.route("/order/<number>", methods=["GET"])
def order_get_by_number(number):
    return controller.order_get_by_number(number)


@logistic_bp.route("/order/set", methods=["POST"])
def order_set():
    return controller.order_set(request.get_json())


@logistic_bp.route("/order/delete", methods=["POST"])
def order_delete():
    return controller.order_delete(request.get_json())


@logistic_bp.route("/order/schedule", methods=["GET"])
def order_schedule():
    offset = request.args.get('offset', None)
    return controller.order_schedule(offset)


@logistic_bp.route("/order/pending", methods=["GET"])
def order_get_pending():
    return controller.order_get_pending()


@logistic_bp.route("/shipping/day", methods=["GET"])
def shipping_day():
    offset = request.args.get('offset', None)
    return controller.shipping_day(offset)


@logistic_bp.route("/photo/upload", methods=["POST"])
def photo_upload():
    image = request.files["image"]
    order_number = request.form.get("order_number")

    if image.filename == "":
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    filename = secure_filename(f"order_{order_number}.jpg")
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

    img = Image.open(image)
    img = img.convert("RGB")
    img.save(filepath, "JPEG", quality=90)

    data = {
        "order_number": order_number,
        "proof_photo": filename
    }
    return controller.photo_upload(data)


@logistic_bp.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)


@logistic_bp.route("/uploads/machines/<filename>")
def uploads_machines(filename):
    return send_from_directory(Config.UPLOAD_MACHINES_FOLDER, filename)


@logistic_bp.route("/webhook", methods=["GET"])
def webhook():
    return controller.webhook(request.args)


@logistic_bp.route("/webhook", methods=["POST"])
def webhook_data():
    return controller.webhook_data(request.get_json())


@socketio.on("connect")
def handle_connect():
    logging.info("Cliente conectado")
    emit("server_response", {"message": "Conectado al servidor"})


@socketio.on("disconnect")
def handle_disconnect():
    logging.info("Cliente desconectado")


@socketio.on("update_schedule")
def handle_update(data):
    #controller.send_message(data)
    logging.info("Update_schedule")
    emit("update_schedule", {}, broadcast=True)


"""@socketio.on("on_the_way")
def handle_on_the_way(data):
    controller.send_message(data)"""
    #logging.info(f"Mensaje recibido: {phone}")
    #emit("update_schedule", {}, broadcast=True)


### FIREBASE ###
@logistic_bp.route("/register_token", methods=["POST"])
def register_token():
    return controller.register_token(request.get_json())

