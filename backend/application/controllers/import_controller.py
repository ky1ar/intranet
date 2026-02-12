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
    def import_dashboard(self):
        return self.import_service.dashboard()
    
    
    @handle_logs_and_exceptions
    def import_options_type(self):
        return self.import_service.options_type()
    

    @handle_logs_and_exceptions
    def import_options_consumption(self):
        return self.import_service.options_consumption()


    @handle_logs_and_exceptions
    def import_options_category(self):
        return self.import_service.options_categories()