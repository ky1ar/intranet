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
    def tracking_client_list(self, data):
        if validation_error := validate_request(data, {"document"}):
            return validation_error, 400
        document = data.get("document")
        
        return self.tracking.client_list(document)
    

    @handle_logs_and_exceptions
    def tracking_all_list(self):
        return self.tracking.all_list()
    

    @handle_logs_and_exceptions
    def tracking_get_order(self, data):
        if validation_error := validate_request(data, {"order_id", "agency_id"}):
            return validation_error, 400
        return self.tracking.get_order(data)
    

    @handle_logs_and_exceptions
    def tracking_get_qr_data(self, data):
        if validation_error := validate_request(data, {"ose_id"}):
            return validation_error, 400
        ose_id = data.get("ose_id")
        return self.tracking.get_qr_data(ose_id)

