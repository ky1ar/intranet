import logging

from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.general_service import GeneralService
from flask import g


class GeneralController:
    def __init__(self):
        self.general_service = GeneralService() 


    @handle_logs_and_exceptions
    def general_service_status(self):
        return self.general_service.service_status()
    

    @handle_logs_and_exceptions
    def general_service_methods(self):
        return self.general_service.service_methods()
    

    @handle_logs_and_exceptions
    def general_technicians(self):
        return self.general_service.get_technicians()
    

    @handle_logs_and_exceptions
    def general_tracking_agencies(self):
        return self.general_service.get_tracking_agencies()


    @handle_logs_and_exceptions
    def general_tracking_status(self):
        return self.general_service.get_tracking_status()
    

    @handle_logs_and_exceptions
    def general_drivers(self):
        return self.general_service.get_drivers()
    

    @handle_logs_and_exceptions
    def general_vendors(self):
        return self.general_service.get_vendors()
    

    @handle_logs_and_exceptions
    def general_districts(self):
        return self.general_service.get_districts()
    

    @handle_logs_and_exceptions
    def general_shipping_types(self):
        return self.general_service.get_shipping_types()
    

    

    
