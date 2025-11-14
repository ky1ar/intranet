import logging
from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.purchase_service import PurchaseService


class PurchaseController:
    def __init__(self):
        self.purchase = PurchaseService() 


    @handle_logs_and_exceptions
    def purchase_requests(self):
        return self.purchase.requests()
    

    @handle_logs_and_exceptions
    def purchase_type_options(self):
        return self.purchase.type_options()
    

    @handle_logs_and_exceptions
    def purchase_urgency_options(self):
        return self.purchase.urgency_options()
    

    @handle_logs_and_exceptions
    def purchase_process(self, data):
        if validation_error := validate_request(data, {"title"}):
            return validation_error, 400
        return self.purchase.process(data)


    @handle_logs_and_exceptions
    def purchase_approve(self, data):
        if validation_error := validate_request(data, {"purchase_id"}):
            return validation_error, 400

        purchase_id = data.get("purchase_id")
        return self.purchase.approve(purchase_id)
    