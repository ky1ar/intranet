import logging

from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.tracking_service import TrackingService
from flask import g


class TrackingController:
    def __init__(self):
        self.tracking_service = TrackingService() 


    @handle_logs_and_exceptions
    def tracking_add(self, data):
        if validation_error := validate_request(data, {"order_number", "agency_id", "code1", "code2"}):
            return validation_error, 400

        return self.tracking_service.add(data)


    @handle_logs_and_exceptions
    def tracking_dashboard(self):
        return self.tracking_service.dashboard()


    @handle_logs_and_exceptions
    def tracking_get_order_by_id(self, order_id):
        return self.tracking_service.get_order_by_id(order_id)
    

    @handle_logs_and_exceptions
    def tracking_get_qr_data(self, data):
        if validation_error := validate_request(data, {"ose_id"}):
            return validation_error, 400
        ose_id = data.get("ose_id")
        return self.tracking_service.get_qr_data(ose_id)
    

    @handle_logs_and_exceptions
    def tracking_force(self, data):
        if validation_error := validate_request(data, {"order_id"}):
            return validation_error, 400
        order_id = data.get("order_id")
        return self.tracking_service.force(order_id)
    

    @handle_logs_and_exceptions
    def tracking_client_list(self, data):
        if validation_error := validate_request(data, {"document"}):
            return validation_error, 400
        document = data.get("document")
        
        return self.tracking_service.client_list(document)
    

    @handle_logs_and_exceptions
    def tracking_get_order(self, data):
        if validation_error := validate_request(data, {"order_id", "agency_id"}):
            return validation_error, 400
        return self.tracking_service.get_order(data)
    

    @handle_logs_and_exceptions
    def tracking_history(self, data):
        return self.tracking_service.history(data)


    @handle_logs_and_exceptions
    def tracking_statistics(self):
        return self.tracking_service.statistics()


    @handle_logs_and_exceptions
    def tracking_find_order(self, order_number):
        if not order_number:
            return None, 400
        
        return self.tracking_service.find_orders(order_number)
    
