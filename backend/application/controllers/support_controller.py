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
    def support_service_link_process(self, data):
        if validation_error := validate_request(data, {"machine_id", "notes"}):
            return validation_error, 400

        return self.support.service_link_order_new(data)


    @handle_logs_and_exceptions
    def support_dashboard(self, user_id):
        return self.support.support_dashboard(user_id)


    @handle_logs_and_exceptions
    def support_ready(self):
        return self.support.ready_list()
    

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


    @handle_logs_and_exceptions
    def support_history(self, data):
        return self.support.history(data)

    
    @handle_logs_and_exceptions
    def support_service_order_next(self, data):
        order_number = data.get("order_number")
        user_id = data.get("user_id")
        notes = data.get("notes")
        send = data.get("send")
        filenames = data.get("filenames")
        return self.support.service_order_next(order_number, user_id, notes, send, filenames)
    

    @handle_logs_and_exceptions
    def support_finish(self, data):  
        service_order, service_order_status = self.support.service_by_id(data.get("service_order_id"))
        if service_order_status != 200:
            return service_order, service_order_status
        
        return self.support.finish(service_order, data)
    

    @handle_logs_and_exceptions
    def support_create_link(self, data):
        if validation := validate_request(data, {"user_id"}):
            return validation, 400

        user_id = data.get("user_id")
        return self.support.create_link(user_id)
    

    @handle_logs_and_exceptions
    def support_link_token(self, data):
        if validation := validate_request(data, {"token"}):
            return validation, 400

        token = data.get("token")
        return self.support.verify_token(token)
    

    @handle_logs_and_exceptions
    def support_link_delete(self, data):
        if validation := validate_request(data, {"user_id", "link_id"}):
            return validation, 400

        return self.support.link_delete(data)
    

    @handle_logs_and_exceptions
    def support_link_history(self, data):
        return self.support.link_history(data)
    

    def support_pdf(self, order_number):
        return self.support.create_pdf(order_number)
    
    
    def support_link_pdf(self, order_number):
        return self.support.create_link_pdf(order_number)


    @handle_logs_and_exceptions
    def support_statistics(self, data):
        return self.support.statistics(data)
    

    @handle_logs_and_exceptions
    def support_find_order(self, order_number):
        if not order_number:
            return None, 400
        
        return self.support.find_orders(order_number)
    