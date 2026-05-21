import logging

from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.dev_service import DevService
from config import WABA


class DevController:
    def __init__(self):
        self.dev = DevService() 


    def webhook(self, data):
        mode = data.get('hub.mode')
        challenge = data.get('hub.challenge')
        verify_token = data.get('hub.verify_token')
        logging.info(f"Webhook received - mode: {mode}, challenge: {challenge}, verify_token: {verify_token}")

        if verify_token == WABA.WEBHOOK_TOKEN:
            return challenge, 200
        else:
            return "Invalid token", 403
        
        
    @handle_logs_and_exceptions
    def webhook_data(self, data):
        return self.dev.process_webhook(data)


    @handle_logs_and_exceptions
    def dev_confirm_flow(self, data):
        if validation_error := validate_request(data, {"phone"}):
            return validation_error, 422
        phone = data.get("phone")
        return self.dev.confirm_flow(phone)
    

    @handle_logs_and_exceptions
    def dev_confirm_flow_all(self):
        return self.dev.confirm_flow_all()
    

    @handle_logs_and_exceptions
    def dev_confirm_flow_list(self):
        return self.dev.confirm_flow_list()
    

    @handle_logs_and_exceptions
    def dev_confirm_flow_reminder(self):
        return self.dev.confirm_flow_reminder()
    

    @handle_logs_and_exceptions
    def dev_confirm_flow_reminder_2(self):
        return self.dev.confirm_flow_reminder_2()

    
    @handle_logs_and_exceptions
    def dev_token(self):
        return self.dev.token()    
    

    @handle_logs_and_exceptions
    def dev_push(self, data):
        return self.dev.push(data)


    @handle_logs_and_exceptions
    def dev_mkt_campaign(self, data):
        if validation_error := validate_request(data, {"template_name", "phones"}):
            return validation_error, 422
        if not isinstance(data.get("phones"), list) or not data["phones"]:
            return "phones debe ser un array no vacío", 422
        return self.dev.mkt_campaign(data)