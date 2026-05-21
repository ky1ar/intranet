from flask import Blueprint, request
from application.controllers.guide_controller import GuideController


guide_bp = Blueprint("guide", __name__, url_prefix="/guide")
controller = GuideController()


# ── WP-facing ────────────────────────────────────────────────────────────────

@guide_bp.route("/request", methods=["POST"])
def create_request():
    return controller.create_request(request.form.to_dict())


@guide_bp.route("/my", methods=["GET"])
def my_guides():
    data = {"wp_user_id": request.args.get("wp_user_id", type=int)}
    return controller.get_my_guides(data)


@guide_bp.route("/content/<int:machine_id>", methods=["GET"])
def get_content(machine_id):
    data = {
        "machine_id": machine_id,
        "wp_user_id": request.args.get("wp_user_id", type=int),
    }
    return controller.get_content(data)


@guide_bp.route("/media/<filename>", methods=["GET"])
def serve_media(filename):
    return controller.serve_media(
        filename,
        request.args.get("wp_user_id", type=int),
        request.args.get("machine_id", type=int),
    )


# ── Intranet-facing ──────────────────────────────────────────────────────────

@guide_bp.route("/admin/content/<int:machine_id>", methods=["GET"])
def get_content_admin(machine_id):
    return controller.get_content_admin({"machine_id": machine_id})


@guide_bp.route("/list", methods=["GET"])
def list_requests():
    data = {"status": request.args.get("status")}
    return controller.list_requests(data)


@guide_bp.route("/content/save", methods=["POST"])
def save_content():
    return controller.save_content(request.get_json())


@guide_bp.route("/media/upload", methods=["POST"])
def upload_media():
    return controller.upload_media({})


@guide_bp.route("/voucher/<filename>", methods=["GET"])
def serve_voucher(filename):
    return controller.serve_voucher(filename)
