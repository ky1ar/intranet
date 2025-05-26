import logging

from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.support_service import SupportService
from flask import g


class SupportController:
    def __init__(self):
        self.support = SupportService() 


    @handle_logs_and_exceptions
    def support_order_consult(self, data):
        if validation := validate_request(data, {"order_number", "document"}):
            return validation, 400
        
        order_number = data.get("order_number")
        document = data.get("document")
        return self.support.order_consult(order_number, document)
    

    @handle_logs_and_exceptions
    def support_service_order_next(self, data):
        if validation := validate_request(data, {"order_number", "notes", "user_id", "send"}):
            return validation, 400
        
        order_number = data.get("order_number")
        user_id = data.get("user_id")
        notes = data.get("notes")
        send = data.get("send")
        return self.support.service_order_next(order_number, user_id, notes, send)
    

    @handle_logs_and_exceptions
    def support_service_order_prev(self, data):
        if validation := validate_request(data, {"order_number", "user_id"}):
            return validation, 400
        
        order_number = data.get("order_number")
        user_id = data.get("user_id")
        return self.support.service_order_prev(order_number, user_id)
    

    @handle_logs_and_exceptions
    def support_service_order_by_number(self, number):
        return self.support.get_service_order_by_number(number)


    @handle_logs_and_exceptions
    def support_service_process(self, data):
        if validation_error := validate_request(data, {"user_id", "machine_id", "notes"}):
            return validation_error, 400

        return self.support.service_order_new(data)
    

    @handle_logs_and_exceptions
    def support_dashboard(self):
        return self.support.support_dashboard()


    @handle_logs_and_exceptions
    def support_service_order_process(self, data):
        if validation_error := validate_request(
            data, 
            {"edit", "order_number", "machine_id", "method_id", "technician_id", "origin_id" ,"status_id" ,"register_at", "paid", "comments"}
        ):
            return validation_error, 400

        return self.support.service_order_process(data)
    

    @handle_logs_and_exceptions
    def support_service_order_update(self, data):
        if validation := validate_request(data, {"order_number", "user_id"}):
            return validation, 400

        return self.support.service_order_update(data)

