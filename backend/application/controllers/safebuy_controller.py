import logging
from flask import request
from application.handlers import handle_logs_and_exceptions
from application.services.safebuy_service import SafebuyService


class SafebuyController:
    def __init__(self):
        self.service = SafebuyService()

    @handle_logs_and_exceptions
    def get_statuses(self):
        return self.service.get_statuses()

    @handle_logs_and_exceptions
    def dashboard(self):
        return self.service.dashboard()

    @handle_logs_and_exceptions
    def get_request(self, request_id):
        return self.service.get_request(request_id)

    @handle_logs_and_exceptions
    def create_request(self):
        return self.service.create_request()

    @handle_logs_and_exceptions
    def update_status(self, data):
        return self.service.update_status(data)

    @handle_logs_and_exceptions
    def update_request(self, request_id, data):
        return self.service.update_request(request_id, data)

    @handle_logs_and_exceptions
    def apply_credit(self, data):
        return self.service.apply_credit(data)

    @handle_logs_and_exceptions
    def delete_request(self, request_id):
        return self.service.delete_request(request_id)

    # ── Attachments ──

    @handle_logs_and_exceptions
    def attachments_upload(self):
        return self.service.attachments_upload()

    @handle_logs_and_exceptions
    def attachment_stream(self, attachment_id):
        disposition = request.args.get("disposition", "inline")
        return self.service.attachment_stream(attachment_id, disposition)

    @handle_logs_and_exceptions
    def attachment_preview(self, attachment_id):
        return self.service.attachment_preview(attachment_id)

    # ── Chat ──

    @handle_logs_and_exceptions
    def chat(self, data):
        return self.service.chat(data)