import logging
from flask import request
from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.import_service import ImportService


class ImportController:
    def __init__(self):
        self.import_service = ImportService() 


    @handle_logs_and_exceptions
    def import_status(self):
        return self.import_service.status()
    

    @handle_logs_and_exceptions
    def import_get_provider(self, provider_id):
        return self.import_service.get_provider(provider_id)


    @handle_logs_and_exceptions
    def import_view(self, import_id):
        return self.import_service.view(import_id)


    @handle_logs_and_exceptions
    def import_dashboard(self):
        return self.import_service.dashboard()
    

    @handle_logs_and_exceptions
    def import_pendings(self):
        return self.import_service.get_by_status(status_id=1)
    
    
    @handle_logs_and_exceptions
    def import_options_provider(self):
        return self.import_service.options_provider()
    

    @handle_logs_and_exceptions
    def import_options_business(self):
        return self.import_service.options_business()


    @handle_logs_and_exceptions
    def import_options_type(self):
        return self.import_service.options_type()
    

    @handle_logs_and_exceptions
    def import_options_incoterm(self):
        return self.import_service.options_incoterm()


    @handle_logs_and_exceptions
    def import_options_port(self):
        return self.import_service.options_port()


    @handle_logs_and_exceptions
    def import_new(self, data):
        return self.import_service.new(data)
    

    @handle_logs_and_exceptions
    def import_move(self, data):
        return self.import_service.move(data)


    @handle_logs_and_exceptions
    def import_down(self, data):
        return self.import_service.down(data)


    @handle_logs_and_exceptions
    def import_attachments_list(self, import_id):
        return self.import_service.attachments_list(import_id)


    @handle_logs_and_exceptions
    def import_attachments_upload(self):
        return self.import_service.attachments_upload()
    

    @handle_logs_and_exceptions
    def import_attachment_stream(self, attachment_id):
        disposition = request.args.get("disposition", "inline")
        return self.import_service.attachment_stream(attachment_id, disposition)


    @handle_logs_and_exceptions
    def import_attachment_preview(self, attachment_id):
        return self.import_service.attachment_preview(attachment_id)
    

    @handle_logs_and_exceptions
    def import_chat(self, data):
        return self.import_service.chat(data)