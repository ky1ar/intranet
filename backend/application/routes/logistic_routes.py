import os, logging
from flask import Blueprint, request, send_from_directory
from werkzeug.utils import secure_filename
from application.controllers.logistic_controller import LogisticController
from config import Config
from PIL import Image


logistic_bp = Blueprint("logistic", __name__, url_prefix="/logistic")
controller = LogisticController()


@logistic_bp.route("/dashboard/week", methods=["GET"])
def order_schedule():
    offset = request.args.get('offset', None)
    return controller.order_schedule(offset)


@logistic_bp.route("/dashboard/day", methods=["GET"])
def shipping_day():
    offset = request.args.get('offset', None)
    return controller.shipping_day(offset)


@logistic_bp.route("/pending", methods=["GET"])
def order_get_pending():
    return controller.order_get_pending()


@logistic_bp.route("/order_number/<number>", methods=["GET"])
def order_get_by_number(number):
    return controller.order_get_by_number(number)


@logistic_bp.route("/set", methods=["POST"])
def order_set():
    return controller.order_set(request.get_json())


@logistic_bp.route("/process", methods=["POST"])
def order_process():
    return controller.order_process(request.get_json())


@logistic_bp.route("/delete", methods=["POST"])
def order_delete():
    return controller.order_delete(request.get_json())



@logistic_bp.route("/upload_proof", methods=["POST"])
def photo_upload():
    image = request.files["image"]
    order_number = request.form.get("order_number")
    user_id = request.form.get("user_id")

    if image.filename == "":
        return {"error": "Nombre de archivo vacío"}, 400

    filename = secure_filename(f"order_{order_number}.jpg")
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

    img = Image.open(image)
    img = img.convert("RGB")
    img.save(filepath, "JPEG", quality=90)

    data = {
        "order_number": order_number,
        "proof_photo": filename,
        "user_id": user_id,
    }
    return controller.photo_upload(data)
































@logistic_bp.route("/uploads/machines/<filename>")
def uploads_machines(filename):
    return send_from_directory(Config.UPLOAD_MACHINES_FOLDER, filename)


@logistic_bp.route("/webhook", methods=["GET"])
def webhook():
    return controller.webhook(request.args)


@logistic_bp.route("/webhook", methods=["POST"])
def webhook_data():
    return controller.webhook_data(request.get_json())


@logistic_bp.route("/register_token", methods=["POST"])
def register_token():
    return controller.register_token(request.get_json())




















