import logging
from application import bcrypt
from application.handlers import handle_exceptions
from application.repository.user_repository import UserRepository
from application.services.general_service import GeneralService
from application.proxy.apiperu import ApiPeru
from flask_jwt_extended import create_access_token


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.general_service = GeneralService()
        self.apiperu = ApiPeru()
        

    @handle_exceptions
    def get_department_team(self, admin_id):
        user, user_status = self.user_repository.get_user_by_id(admin_id)
        if user_status != 200:
            return user, user_status
        
        if user.level_id == 1:
            return "Usuario sin acceso al sistema", 400
        
        team, team_status = self.user_repository.get_department_team(admin_id, user.department_id)
        if team_status != 200:
            return team, team_status
        
        team_dict = [
            {
                "id": teammate.id,
                "name": teammate.name,
                "image": teammate.image if teammate.image else 'user_default.jpg',

            } for teammate in team
        ]
        return team_dict, 200


    @handle_exceptions
    def get_user_by_document(self, document):
        user, user_status = self.user_repository.get_user_by_document(document)
        if user_status != 200:
            return user, user_status
        
        if user.level_id == 1:
            return "No cuentas con acceso al sistema", 400
        name = self.format_name(user.name)
        response = {
            "image": user.image if user.image else 'user_default.jpg',
            "name": name,
            "department_name": user.department.name,
        }

        if user.password == "password":
            response["first_login"] = True

        return response, 200
    

    @handle_exceptions
    def create_pin(self, document, pin):
        user, user_status = self.user_repository.get_user_by_document(document)
        if user_status != 200:
            return user, user_status
        
        hashed_pin = bcrypt.generate_password_hash(pin).decode("utf-8")
        return self.user_repository.set_user_pin(user, hashed_pin)
    
    
    @handle_exceptions
    def login(self, document, password, fcm_token):
        user, user_status = self.user_repository.get_user_by_document(document)
        if user_status != 200:
            return user, user_status
        
        if user.level_id == 1:
            return "No cuentas con acceso al sistema", 400

        if user.password == "password":
            return "Crea una clave antes de continuar", 400

        if bcrypt.check_password_hash(user.password.encode('utf-8'), password.encode('utf-8')):
            access_token = create_access_token(identity=str(user.id))
            #stored_token, stored_token_status = self.service.get_fcm_token(fcm_token)
            #if stored_token_status == 200:
            #   self.service.set_fcm_token(stored_token, user.id)
            
            user_data = {
                "id": user.id,
                "level_id": user.level_id,
                "department_id": user.department_id,
                "department_name": user.department.name,
                "shipping_app_level": user.shipping_app_level,
                "document": user.document,
                "name": self.general_service.format_name(user.name),
                "image": user.image if user.image else 'user_default.jpg',
                "default_page": user.default_page or "logistics",
                "token": access_token
            }
            return user_data, 200
        
        return "Clave incorrecta", 400
    
    
    @handle_exceptions
    def format_name(self, full_name):
        words = full_name.strip().split()

        if len(words) == 3:
            return f"{words[0]} {words[1]}"
        elif len(words) == 4:
            return f"{words[0]} {words[2]}"
        elif len(words) == 5:
            return f"{words[0]} {words[3]}"
        return "Texto no válido"
        