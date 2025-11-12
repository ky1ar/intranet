import logging
from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.user_service import UserService
from flask_jwt_extended import get_jwt_identity


class UserController:
    def __init__(self):
        self.user = UserService() 


    @handle_logs_and_exceptions
    def user_team(self, user_id):
        return self.user.get_department_team(user_id)
    

    @handle_logs_and_exceptions
    def user_find(self, data):
        if validation := validate_request(data, {"document"}):
            return validation, 400
        
        document = data.get("document")
        return self.user.get_user_by_document(document)
    

    @handle_logs_and_exceptions
    def user_create_pin(self, data):
        if validation := validate_request(data, {"document", "pin", "phone"}):
            return validation, 400
        
        document = data.get("document")
        pin = data.get("pin")
        phone = data.get("phone")
        return self.user.create_pin(document, pin, phone)
    

    @handle_logs_and_exceptions
    def user_login(self, data):
        if validation_error := validate_request(data, {"document", "password"}):
            return validation_error, 400
        
        document = data.get("document")
        password = data.get("password")
        fcm_token = data.get("fcm_token")

        return self.user.login(document, password, fcm_token)
    
        
    @handle_logs_and_exceptions
    def user_logout(self, data):
        if validation_error := validate_request(data, {"fcm_token"}):
            return validation_error, 400
        
        return True, 200
        #fcm_token = data.get("fcm_token")
        #stored_token, stored_token_status = self.service.get_fcm_token(fcm_token)
            
        #if stored_token_status == 200:
        #    return self.service.revome_fcm_token(stored_token)
        

    @handle_logs_and_exceptions
    def user_send_otp(self, data):
        if validation_error := validate_request(data, {"user_id", "phone"}):
            return validation_error, 400
        user_id = data.get("user_id")
        phone = data.get("phone")
        return self.user.send_otp(user_id, phone)
    

    @handle_logs_and_exceptions
    def user_validate_otp(self, data):
        if validation_error := validate_request(data, {"user_id", "phone", "otp_code"}):
            return validation_error, 400
        otp_code = data.get("otp_code")
        user_id = data.get("user_id")
        phone = data.get("phone")
        return self.user.validate_otp(user_id, phone, otp_code)
    

    @handle_logs_and_exceptions
    def register_device(self, data):
        device_id = data.get("device_id")
        fcm_token = data.get("fcm_token")
        device_platform = data.get("device_platform")
        user_agent = data.get("user_agent")

        if not device_id or not fcm_token:
            return "device_id y fcm_token son requeridos", 400

        return self.user.register_device(device_id, fcm_token, device_platform, user_agent)
    
        
    
    