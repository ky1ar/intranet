import logging

from config import WABA
from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.logistic_services import LogisticService

class LogisticController:
    def __init__(self):
        self.logistic_service = LogisticService()     


    @handle_logs_and_exceptions
    def logistic_dashboard_week(self, offset=0):
        return self.logistic_service.get_schedule(int(offset))
    

    @handle_logs_and_exceptions
    def logistic_dashboard_day(self, offset=0):
        return self.logistic_service.get_day_shippings(int(offset))
    

    @handle_logs_and_exceptions
    def logistic_pendings(self):
        return self.logistic_service.get_orders_by_status(status_id=1)
        

    @handle_logs_and_exceptions
    def logistic_order_number(self, order_number):
        shipping_order, status = self.logistic_service.shipping_by_order_number(order_number)
        if status != 200:
            return shipping_order, status
        
        return self.logistic_service.get_shipping_order(shipping_order)


    @handle_logs_and_exceptions
    def logistic_shipping_order_by_id(self, shipping_order_id):
        shipping_order, status = self.logistic_service.shipping_by_id(shipping_order_id)
        if status != 200:
            return shipping_order, status
        
        return self.logistic_service.get_shipping_order(shipping_order)
    

    @handle_logs_and_exceptions
    def logistic_set(self, data):
        if validation_error := validate_request(data, {"shipping_order_id", "user_id"}):
            return validation_error, 400

        shipping_order, shipping_order_status = self.logistic_service.shipping_by_id(data.get("shipping_order_id"))
        if shipping_order_status != 200:
            return shipping_order, shipping_order_status
        
        return self.logistic_service.order_set(shipping_order, data)

    
    @handle_logs_and_exceptions
    def logistic_process(self, data):
        shipping_order_id = data.get("shipping_order_id")
        if shipping_order_id:
            shipping_order, shipping_status = self.logistic_service.shipping_by_id(shipping_order_id)
            if shipping_status != 200:
                return shipping_order, shipping_status
            
            return self.logistic_service.edit_shipping_order(shipping_order, data)
        
        return self.logistic_service.new_shipping_order(data)

        
    @handle_logs_and_exceptions
    def logistic_delete(self, data):
        if validation_error := validate_request(data, {"shipping_order_id", "user_id"}):
            return validation_error, 400

        shipping_order, shipping_order_status = self.logistic_service.shipping_by_id(data.get("shipping_order_id"))
        if shipping_order_status != 200:
            return shipping_order, shipping_order_status
        
        return self.logistic_service.delete_shipping_order(shipping_order, data)
    

    @handle_logs_and_exceptions
    def logistic_upload_proof(self, data):
        shipping_order, shipping_order_status = self.logistic_service.shipping_by_id(data.get("shipping_order_id"))
        if shipping_order_status != 200:
            return shipping_order, shipping_order_status
        
        return self.logistic_service.photo_upload(shipping_order, data)
        

    @handle_logs_and_exceptions
    def logistic_history(self, data):
        return self.logistic_service.history(data)


    @handle_logs_and_exceptions
    def logistic_statistics(self):
        return self.logistic_service.statistics()


    @handle_logs_and_exceptions
    def logistic_find_order(self, order_number):
        if not order_number:
            return None, 400
        
        return self.logistic_service.find_orders(order_number)


    @handle_logs_and_exceptions
    def logistic_extract_picking(self, data):
        return self.logistic_service.extract_picking(data)
    

    def logistic_qr_pdf(self, data):
        return self.logistic_service.generate_qr_pdf(data)


    @handle_logs_and_exceptions
    def logistic_search_label_machines(self, query):
        return self.logistic_service.search_label_machines(query)


    def logistic_machine_label_pdf(self, data):
        return self.logistic_service.generate_machine_label_pdf(data)
