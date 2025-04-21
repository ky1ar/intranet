import logging

from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.user_service import UserService


class UserController:
    def __init__(self):
        self.user = UserService() 


    @handle_logs_and_exceptions
    def user_data_document(self, document):
        if not document:
            return 'Documento inválido', 400
        
        return self.user.get_data(document)
    

    @handle_logs_and_exceptions
    def user_team(self, data):
        if validation := validate_request(data, {"admin_id"}):
            return validation, 400
        admin_id = data.get("admin_id")
        return self.user.get_department_team(admin_id)


    @handle_logs_and_exceptions
    def user_name(self, document):
        return self.user.get_name(document)
    

    @handle_logs_and_exceptions
    def user_find(self, request):
        if validation := validate_request(request, {"document"}):
            return validation, 400
        
        document = request.get("document")
        return self.user.get_user_by_document(document)
    

    @handle_logs_and_exceptions
    def user_create_pin(self, request):
        if validation := validate_request(request, {"document", "pin"}):
            return validation, 400
        
        document = request.get("document")
        pin = request.get("pin")
        return self.user.create_pin(document, pin)
    

    @handle_logs_and_exceptions
    def user_login(self, request):
        if validation_error := validate_request(request, {"document", "password"}):
            return validation_error, 400
        
        document = request.get("document")
        password = request.get("password")
        fcm_token = request.get("fcm_token")

        return self.user.login(document, password, fcm_token)
    
        
    @handle_logs_and_exceptions
    def user_logout(self, request):
        if validation_error := validate_request(request, {"fcm_token"}):
            return validation_error, 400
        
        return True, 200
        #fcm_token = request.get("fcm_token")
        #stored_token, stored_token_status = self.service.get_fcm_token(fcm_token)
            
        #if stored_token_status == 200:
        #    return self.service.revome_fcm_token(stored_token)
        
