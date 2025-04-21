import logging

from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.general_service import GeneralService
from flask import g


class GeneralController:
    def __init__(self):
        self.general = GeneralService() 


    @handle_logs_and_exceptions
    def general_service_status(self):
        return self.general.service_status()
    

    @handle_logs_and_exceptions
    def general_service_methods(self):
        return self.general.service_methods()
    

    @handle_logs_and_exceptions
    def general_technicians(self):
        return self.general.get_technicians()
    

    @handle_logs_and_exceptions
    def general_tracking_agencies(self):
        return self.general.get_tracking_agencies()

    
