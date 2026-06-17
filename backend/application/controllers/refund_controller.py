from flask import request
from application.handlers import handle_logs_and_exceptions
from application.services.refund_service import RefundService


class RefundController:
    def __init__(self):
        self.service = RefundService()

    @handle_logs_and_exceptions
    def get_statuses(self):
        return self.service.get_statuses()

    @handle_logs_and_exceptions
    def dashboard(self):
        return self.service.dashboard()

    @handle_logs_and_exceptions
    def get_refund(self, refund_id):
        return self.service.get_refund(refund_id)

    @handle_logs_and_exceptions
    def search_requests(self, term):
        return self.service.search_requests(term)

    @handle_logs_and_exceptions
    def history(self, data):
        return self.service.history(data)

    @handle_logs_and_exceptions
    def statistics(self, data):
        return self.service.statistics(data)

    @handle_logs_and_exceptions
    def create(self):
        return self.service.create()

    @handle_logs_and_exceptions
    def update_status(self, data):
        return self.service.update_status(data)

    @handle_logs_and_exceptions
    def edit_order_number(self, refund_id):
        return self.service.edit_order_number(refund_id, request.get_json() or {})

    @handle_logs_and_exceptions
    def update_penalty(self, refund_id):
        return self.service.update_penalty(refund_id, request.get_json() or {})

    @handle_logs_and_exceptions
    def delete(self, refund_id):
        return self.service.delete(refund_id)

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

    @handle_logs_and_exceptions
    def delete_attachment(self, attachment_id):
        return self.service.delete_attachment(attachment_id)

    # ── Links ──

    @handle_logs_and_exceptions
    def create_link(self):
        return self.service.create_link()

    @handle_logs_and_exceptions
    def link_history(self):
        return self.service.link_history()

    @handle_logs_and_exceptions
    def delete_link(self, link_id):
        return self.service.delete_link(link_id)

    @handle_logs_and_exceptions
    def verify_link(self, data):
        return self.service.verify_link(data.get("token", ""))

    @handle_logs_and_exceptions
    def link_process(self, data):
        return self.service.link_process(data)

    # ── Chat ──

    @handle_logs_and_exceptions
    def chat(self, data):
        return self.service.chat(data)
