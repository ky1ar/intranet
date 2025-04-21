import logging, json
from application import bcrypt, redis_client
from application.handlers import handle_exceptions
from application.repository.user_repository import UserRepository
from application.proxy.apiperu import ApiPeru
from flask_jwt_extended import create_access_token


class UserService:
    def __init__(self):
        self.repository = UserRepository()
        self.apiperu = ApiPeru()
        
    
    @handle_exceptions
    def get_data(self, document):
        if len(document) not in (8, 11):
            return 'Documento inválido', 400
        
        key = f"client_data:{document}"
        cache = redis_client.get(key)
        if cache:
            logging.info('User data loaded from cache')
            return json.loads(cache), 200
        
        user_data, user_status = self.repository.get_user_by_document(document)
        if user_status == 500:
            return user_data, user_status
        
        if user_status == 200:
            user_dict = user_data.to_dict(only_fields=['id', 'document', 'name', 'phone'])
            if 'phone' in user_dict and user_dict['phone']:
                user_dict['phone'] = user_dict['phone'][2:]

            redis_client.set(key, json.dumps(user_dict))
            return user_dict, 200
        
        if len(document) == 8:
            return self.apiperu.get_name('dni', document)
        
        return self.apiperu.get_name('ruc', document)


    @handle_exceptions
    def get_department_team(self, admin_id):
        user, user_status = self.repository.get_user_by_id(admin_id)
        if user_status != 200:
            return user, user_status
        
        if user.level_id == 1:
            return "Usuario sin acceso al sistema", 400
        
        team, team_status = self.repository.get_department_team(admin_id, user.department_id)
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
    def get_name(self, document):
        if len(document) not in (8, 11):
            return None, 400
        
        if len(document) == 8:
            return self.apiperu.get_name('dni', document)
        
        return self.apiperu.get_name('ruc', document)


    @handle_exceptions
    def get_user_by_document(self, document):
        user, user_status = self.repository.get_user_by_document(document)
        if user_status != 200:
            return user, user_status
        
        if user.level_id == 1:
            return "No cuentas con acceso al sistema", 400

        response = {
            "image": user.image if user.image else 'user_default.jpg',
            "name": user.name.split()[0],
            "department_name": user.department.name,
        }

        if user.password == "password":
            response["first_login"] = True

        return response, 200
    

    @handle_exceptions
    def create_pin(self, document, pin):
        user, user_status = self.repository.get_user_by_document(document)
        if user_status != 200:
            return user, user_status
        
        hashed_pin = bcrypt.generate_password_hash(pin).decode("utf-8")
        return self.repository.set_user_pin(user, hashed_pin)
    
    
    @handle_exceptions
    def login(self, document, password, fcm_token):
        user, user_status = self.repository.get_user_by_document(document)
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
                "image": user.image if user.image else 'user_default.jpg',
                "name": user.name,
                "level_id": user.level_id,
                "document": user.document,
                "department_name": user.department.name,
                "shipping_app_level": user.shipping_app_level,
                "default_page": user.default_page or "home",
                "token": access_token
            }
            return user_data, 200
        
        return "Clave incorrecta", 400
    
    
        
        