from flask import send_file
from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.guide_service import GuideService


class GuideController:
    def __init__(self):
        self.service = GuideService()

    @handle_logs_and_exceptions
    def create_request(self, data):
        if validation := validate_request(data, {"wp_user_id", "machine_id", "email", "phone", "dni"}):
            return validation, 400
        return self.service.create_request(data)

    @handle_logs_and_exceptions
    def get_my_guides(self, data):
        if validation := validate_request(data, {"wp_user_id"}):
            return validation, 400
        return self.service.get_my_guides(data["wp_user_id"])

    @handle_logs_and_exceptions
    def get_content(self, data):
        if validation := validate_request(data, {"wp_user_id", "machine_id"}):
            return validation, 400
        return self.service.get_content(data["wp_user_id"], data["machine_id"])

    def serve_media(self, filename, wp_user_id, machine_id):
        filepath, err = self.service.serve_media(filename, wp_user_id, machine_id)
        if not filepath:
            return {"error": err}, 403
        return send_file(filepath)

    @handle_logs_and_exceptions
    def get_content_admin(self, data):
        if validation := validate_request(data, {"machine_id"}):
            return validation, 400
        return self.service.get_content_admin(data["machine_id"])

    @handle_logs_and_exceptions
    def list_requests(self, data):
        return self.service.list_requests(data.get("status"))

    @handle_logs_and_exceptions
    def save_content(self, data):
        if validation := validate_request(data, {"machine_id"}):
            return validation, 400
        return self.service.save_content(data)

    @handle_logs_and_exceptions
    def upload_media(self, data):
        return self.service.upload_media()

    def serve_voucher(self, filename):
        filepath = self.service.serve_voucher(filename)
        if not filepath:
            return {"error": "Archivo no encontrado"}, 404
        return send_file(filepath)
