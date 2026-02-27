import os, logging, uuid
from flask import Blueprint, request, send_from_directory
from werkzeug.utils import secure_filename
from application.controllers.logistic_controller import LogisticController
from config import Config
from PIL import Image


logistic_bp = Blueprint("logistic", __name__, url_prefix="/logistic")
controller = LogisticController()


@logistic_bp.route("/dashboard/week", methods=["GET"])
def logistic_dashboard_week():
    offset = request.args.get('offset', None)
    return controller.logistic_dashboard_week(offset)


@logistic_bp.route("/dashboard/day", methods=["GET"])
def logistic_dashboard_day():
    offset = request.args.get('offset', None)
    return controller.logistic_dashboard_day(offset)


@logistic_bp.route("/pending", methods=["GET"])
def logistic_pendings():
    return controller.logistic_pendings()


@logistic_bp.route("/order_number/<number>", methods=["GET"])
def logistic_order_number(number):
    return controller.logistic_order_number(number)


@logistic_bp.route("/shipping_order_id/<shipping_order_id>", methods=["GET"])
def logistic_shipping_order_by_id(shipping_order_id):
    return controller.logistic_shipping_order_by_id(shipping_order_id)


@logistic_bp.route("/set", methods=["POST"])
def logistic_set():
    return controller.logistic_set(request.get_json())


@logistic_bp.route("/process", methods=["POST"])
def logistic_process():
    return controller.logistic_process(request.get_json())


@logistic_bp.route("/delete", methods=["POST"])
def logistic_delete():
    return controller.logistic_delete(request.get_json())


@logistic_bp.route("/upload_proof", methods=["POST"])
def logistic_upload_proof():
    image = request.files["image"]
    order_number = request.form.get("order_number")
    shipping_order_id = request.form.get("shipping_order_id")
    user_id = request.form.get("user_id")

    if image.filename == "":
        return {"error": "Nombre de archivo vacío"}, 400

    filename = secure_filename(f"order_{order_number}_{shipping_order_id}.jpg")
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

    img = Image.open(image)
    img = img.convert("RGB")
    img.save(filepath, "JPEG", quality=90)

    data = {
        "shipping_order_id": shipping_order_id,
        "proof_photo": filename,
        "user_id": user_id,
    }
    return controller.logistic_upload_proof(data)


@logistic_bp.route("/history", methods=["GET"])
def history():
    payload = {
        "page": int(request.args.get("page", 1)),
        "per_page": int(request.args.get("per_page", 12))
    }
    return controller.logistic_history(payload)


@logistic_bp.route("/statistics", methods=["GET"])
def statistics():
    return controller.logistic_statistics()


@logistic_bp.route("/find/<order_number>", methods=["GET"])
def logistic_find_order(order_number):
    return controller.logistic_find_order(order_number)


@logistic_bp.post("/pdf")
def extract_picking():
    file = request.files["file"]
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Archivo no válido"}, 400

    original_name = file.filename
    token = uuid.uuid4().hex
    source_filename = f"{token}_{original_name}"

    source_path = os.path.join(Config.UPLOAD_PICKING_FOLDER, source_filename)
    file.save(source_path)
    data = {
        "source_path": source_path,
        "original_name": original_name,
    }
    return controller.logistic_extract_picking(data)


@logistic_bp.post("/qr/pdf")
def logistic_qr_pdf():
    return controller.logistic_qr_pdf(request.get_json() or {})