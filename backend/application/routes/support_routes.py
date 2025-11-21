import os, logging
from flask import Blueprint, request
from werkzeug.utils import secure_filename
from application.controllers.support_controller import SupportController
from config import Config
from PIL import Image


support_bp = Blueprint("support", __name__, url_prefix="/support")
controller = SupportController()


@support_bp.route("/dashboard", methods=["GET"])
def dashboard():
    user_id = request.args.get("user_id")
    return controller.support_dashboard(user_id)


@support_bp.route("/ready", methods=["GET"])
def ready():
    return controller.support_ready()


@support_bp.route("/order_number/<number>", methods=["GET"])
def service_order_by_number(number):
    return controller.support_service_order_by_number(number)


@support_bp.route("/order/prev", methods=["POST"])
def service_order_prev():
    return controller.support_service_order_prev(request.get_json())


@support_bp.route("/order/update", methods=["POST"])
def service_order_update():
    return controller.support_service_order_update(request.get_json())


@support_bp.route("/process", methods=["POST"])
def service_process():
    return controller.support_service_process(request.get_json())


@support_bp.route("/link_process", methods=["POST"])
def service_link_process():
    return controller.support_service_link_process(request.get_json())


@support_bp.route("/consult", methods=["POST"])
def order_consult():
    return controller.support_order_consult(request.get_json())


@support_bp.route("/history", methods=["GET"])
def history():
    payload = {
        "page": int(request.args.get("page", 1)),
        "per_page": int(request.args.get("per_page", 12))
    }
    return controller.support_history(payload)


@support_bp.route("/order/next", methods=["POST"])
def service_order_next():
    images = request.files.getlist("images[]")
    order_number = request.form.get("order_number")
    send = request.form.get("send")
    send_bool = send.lower() == "true" if send else False
    user_id = request.form.get("user_id")
    notes = request.form.get("notes")
    status_id = request.form.get("status_id")

    saved_files = []
    for idx, image in enumerate(images):
        if image.filename == "":
            continue

        safe_name = secure_filename(f"support_{order_number}_{status_id}_{idx}.jpg")
        filepath = os.path.join(Config.UPLOAD_FOLDER, safe_name)

        img = Image.open(image)
        img = img.convert("RGB")
        img.save(filepath, "JPEG", quality=90)

        saved_files.append(safe_name)

    data = {
        "send": send_bool,
        "order_number": order_number,
        "filenames": saved_files,
        "user_id": user_id,
        "notes": notes,
    }
    return controller.support_service_order_next(data)


@support_bp.route("/finish", methods=["POST"])
def finish():
    image = request.files["image"]
    order_number = request.form.get("order_number")
    service_order_id = request.form.get("service_order_id")
    user_id = request.form.get("user_id")
    notes = request.form.get("notes")

    if image.filename == "":
        return {"error": "Nombre de archivo vacío"}, 400

    filename = secure_filename(f"support_{order_number}_{service_order_id}.jpg")
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

    img = Image.open(image)
    img = img.convert("RGB")
    img.save(filepath, "JPEG", quality=90)

    data = {
        "service_order_id": service_order_id,
        "order_number": order_number,
        "filename": filename,
        "user_id": user_id,
        "notes": notes,
    }
    return controller.support_finish(data)


@support_bp.route("/statistics", methods=["GET"])
def statistics():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    data = {
        "start_date": start_date,
        "end_date": end_date,
    }
    return controller.support_statistics(data)


@support_bp.route("/find/<order_number>", methods=["GET"])
def support_find_order(order_number):
    return controller.support_find_order(order_number)


@support_bp.route("/pdf/<order_number>", methods=["GET"])
def pdf(order_number):
    return controller.support_pdf(order_number)


@support_bp.route("/link", methods=["POST"])
def support_link():
    return controller.support_create_link(request.get_json())


@support_bp.route("/link_token", methods=["POST"])
def link_token():
    return controller.support_link_token(request.get_json())


@support_bp.route("/link_delete", methods=["POST"])
def link_delete():
    return controller.support_link_delete(request.get_json())


@support_bp.route("/link_history", methods=["GET"])
def link_history():
    payload = {
        "page": int(request.args.get("page", 1)),
        "per_page": int(request.args.get("per_page", 12))
    }
    return controller.support_link_history(payload)


@support_bp.route("/link/pdf/<order_number>", methods=["GET"])
def link_pdf(order_number):
    return controller.support_link_pdf(order_number)

