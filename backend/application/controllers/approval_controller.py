from flask import send_file
from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.approval_service import ApprovalService


class ApprovalController:
    def __init__(self):
        self.service = ApprovalService()

    @handle_logs_and_exceptions
    def get_wp_profile(self, data):
        wp_user_id = data.get("wp_user_id")
        return self.service.get_wp_profile(wp_user_id)

    @handle_logs_and_exceptions
    def get_request_status(self, data):
        if validation := validate_request(data, {"wp_user_id", "type"}):
            return validation, 400
        return self.service.get_request_status(data["wp_user_id"], data["type"])

    @handle_logs_and_exceptions
    def create_request(self, data):
        if validation := validate_request(data, {"wp_user_id", "type_slug", "email", "phone", "dni", "invoice_number"}):
            return validation, 400
        return self.service.create_request(data)

    @handle_logs_and_exceptions
    def get_all_requests(self, data):
        status_filter = data.get("status") if data else None
        return self.service.get_all_requests(status_filter)

    @handle_logs_and_exceptions
    def get_dashboard(self, data):
        return self.service.dashboard()

    @handle_logs_and_exceptions
    def history(self, data):
        return self.service.history(data)

    @handle_logs_and_exceptions
    def get_request_detail(self, data):
        return self.service.get_request_detail(data.get("request_id"))

    @handle_logs_and_exceptions
    def send_chat(self, data):
        return self.service.send_chat(data)

    @handle_logs_and_exceptions
    def start_review(self, data):
        if validation := validate_request(data, {"request_id", "user_id"}):
            return validation, 400
        return self.service.start_review(data)

    def serve_voucher(self, filename):
        filepath = self.service.serve_voucher(filename)
        if not filepath:
            return {"error": "Archivo no encontrado"}, 404
        return send_file(filepath)

    @handle_logs_and_exceptions
    def approve_request(self, data):
        if validation := validate_request(data, {"request_id", "user_id"}):
            return validation, 400
        return self.service.approve_request(data)

    @handle_logs_and_exceptions
    def reject_request(self, data):
        if validation := validate_request(data, {"request_id", "user_id"}):
            return validation, 400
        return self.service.reject_request(data)
