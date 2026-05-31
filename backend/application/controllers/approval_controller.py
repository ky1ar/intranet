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
        if validation := validate_request(data, {"wp_user_id", "type_slug", "email", "phone", "dni"}):
            return validation, 400
        return self.service.create_request(data)

    @handle_logs_and_exceptions
    def get_all_requests(self, data):
        status_filter = data.get("status") if data else None
        return self.service.get_all_requests(status_filter)

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
