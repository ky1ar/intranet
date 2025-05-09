import logging

from config import WABA
from application import socketio
from application.models import HistoryType, ShippingStatusList
from application.services.logistic_services import LogisticService
from application.handlers import handle_logs_and_exceptions, validate_request

class LogisticController:
    def __init__(self):
        self.logistic_service = LogisticService()     


    @handle_logs_and_exceptions
    def order_schedule(self, offset=0):
        return self.logistic_service.get_schedule(int(offset))
    

    @handle_logs_and_exceptions
    def shipping_day(self, offset=0):
        return self.logistic_service.get_day_shippings(int(offset))
    

    @handle_logs_and_exceptions
    def order_get_pending(self):
        return self.logistic_service.get_orders_by_status(status_id=1)
        

    @handle_logs_and_exceptions
    def order_get_by_number(self, order_number):
        shipping_order, status = self.logistic_service.shipping_by_order_number(order_number)
        if status != 200:
            return shipping_order, status
        
        return self.logistic_service.order_get_by_number(shipping_order)


    @handle_logs_and_exceptions
    def order_set(self, data):
        if validation_error := validate_request(data, {"order_number", "user_id"}):
            return validation_error, 400

        shipping_order, shipping_order_status = self.logistic_service.shipping_by_order_number(data.get("order_number"))
        if shipping_order_status != 200:
            return shipping_order, shipping_order_status
        
        return self.logistic_service.order_set(shipping_order, data)

    
    @handle_logs_and_exceptions
    def order_process(self, data):
        shipping_order_id = data.get("shipping_order_id")
        if shipping_order_id:
            shipping_order, shipping_status = self.logistic_service.shipping_by_id(shipping_order_id)
            if shipping_status != 200:
                return shipping_order, shipping_status
            
            return self.logistic_service.edit_shipping_order(shipping_order, data)
        
        return self.logistic_service.new_shipping_order(data)

        
    @handle_logs_and_exceptions
    def order_delete(self, data):
        if validation_error := validate_request(data, {"order_number", "user_id"}):
            return validation_error, 400

        order_number = data.get("order_number")
        shipping_order, shipping_order_status = self.logistic_service.shipping_by_order_number(order_number)
        if shipping_order_status != 200:
            return shipping_order, shipping_order_status
        
        return self.logistic_service.delete_shipping_order(shipping_order, data)
    

    @handle_logs_and_exceptions
    def photo_upload(self, data):
        order_number = data.pop("order_number")
        shipping_order, shipping_order_status = self.logistic_service.shipping_by_order_number(order_number)
        if shipping_order_status != 200:
            return shipping_order, shipping_order_status
        
        return self.logistic_service.photo_upload(shipping_order, data)
        



































    @handle_logs_and_exceptions
    def send_message(self, data):
        return self.logistic_service.send_message(data, template=3)


    


    def webhook(self, request):
        mode = request.get('hub.mode')
        challenge = request.get('hub.challenge')
        verify_token = request.get('hub.verify_token')
        logging.info(f"Webhook received - mode: {mode}, challenge: {challenge}, verify_token: {verify_token}")

        if verify_token == WABA.WEBHOOK_TOKEN:
            return challenge, 200
        else:
            return "Invalid token", 403
        

    @handle_logs_and_exceptions
    def webhook_data(self, request):
        #logging.info(request)
        return True, 200


    @handle_logs_and_exceptions
    def register_token(self, request):
        if validation_error := validate_request(
            request, 
            {"user_id", "device_id", "token"}
        ):
            return validation_error, 400
        
        return self.logistic_service.register_token(request)


