import logging
from flask import request
from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.complaint_service import ComplaintService


class ComplaintController:
    def __init__(self):
        self.complain_service = ComplaintService() 


    @handle_logs_and_exceptions
    def complaint_status(self):
        return self.complain_service.status()
    

    @handle_logs_and_exceptions
    def complaint_dashboard(self):
        return self.complain_service.dashboard()
    
    
    @handle_logs_and_exceptions
    def complaint_view(self, complaint_id):
        return self.complain_service.view(complaint_id)
    
    
    @handle_logs_and_exceptions
    def complaint_new(self, data):
        return self.complain_service.new(data)
    

    @handle_logs_and_exceptions
    def complaint_move(self, data):
        return self.complain_service.move(data)
    

    @handle_logs_and_exceptions
    def attachments_list(self, complaint_id):
        return self.complain_service.attachments_list(complaint_id)


    @handle_logs_and_exceptions
    def attachments_upload(self, complaint_id):
        return self.complain_service.attachments_upload(complaint_id)


    @handle_logs_and_exceptions
    def attachment_stream(self, attachment_id):
        disposition = request.args.get("disposition", "inline")
        return self.complain_service.attachment_stream(attachment_id, disposition)


    @handle_logs_and_exceptions
    def attachment_preview(self, attachment_id):
        return self.complain_service.attachment_preview(attachment_id)


    @handle_logs_and_exceptions
    def complaint_options_type(self):
        return self.complain_service.options_type()
    

    @handle_logs_and_exceptions
    def complaint_options_consumption(self):
        return self.complain_service.options_consumption()


    @handle_logs_and_exceptions
    def complaint_options_category(self):
        return self.complain_service.options_categories()
    

    @handle_logs_and_exceptions
    def complaint_chat(self, data):
        return self.complain_service.chat(data)

