import logging

from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.tracking_service import TrackingService
from flask import g


class TrackingController:
    def __init__(self):
        self.tracking = TrackingService() 


    @handle_logs_and_exceptions
    def tracking_add(self, data):
        if validation_error := validate_request(data, {"order_number", "agency_id", "code1", "code2"}):
            return validation_error, 400

        return self.tracking.add(data)


    @handle_logs_and_exceptions
    def tracking_list(self, data):
        if validation_error := validate_request(data, {"document"}):
            return validation_error, 400
        document = data.get("document")
        
        return self.tracking.list(document)
    

    @handle_logs_and_exceptions
    def tracking_get_order(self, order_number):
        return self.tracking.get_order(order_number)

