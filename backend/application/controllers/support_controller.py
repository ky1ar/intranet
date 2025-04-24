import logging

from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.support_service import SupportService
from flask import g


class SupportController:
    def __init__(self):
        self.support = SupportService() 


    @handle_logs_and_exceptions
    def support_order_consult(self, request):
        if validation := validate_request(request, {"order_number", "document"}):
            return validation, 400
        
        order_number = request.get("order_number")
        document = request.get("document")
        return self.support.order_consult(order_number, document)
    

    @handle_logs_and_exceptions
    def support_service_order_next(self, request):
        if validation := validate_request(request, {"order_number", "notes", "admin_id"}):
            return validation, 400
        
        order_number = request.get("order_number")
        admin_id = request.get("admin_id")
        notes = request.get("notes")
        return self.support.service_order_next(order_number, admin_id, notes)
    

    @handle_logs_and_exceptions
    def support_service_order_prev(self, request):
        if validation := validate_request(request, {"order_number", "admin_id"}):
            return validation, 400
        
        order_number = request.get("order_number")
        admin_id = request.get("admin_id")
        return self.support.service_order_prev(order_number, admin_id)
    

    @handle_logs_and_exceptions
    def support_service_order_by_number(self, number):
        return self.support.get_service_order_by_number(number)


    @handle_logs_and_exceptions
    def support_service_order_new(self, request):
        if validation_error := validate_request(request, {"admin_id", "machine_id", "notes"}):
            return validation_error, 400

        return self.support.service_order_new(request)
    

    @handle_logs_and_exceptions
    def support_dashboard(self):
        return self.support.support_dashboard()


    @handle_logs_and_exceptions
    def support_service_order_process(self, request):
        if validation_error := validate_request(
            request, 
            {"edit", "order_number", "machine_id", "method_id", "technician_id", "origin_id" ,"status_id" ,"register_at", "paid", "comments"}
        ):
            return validation_error, 400

        return self.support.service_order_process(request)
    

