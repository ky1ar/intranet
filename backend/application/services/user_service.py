import logging
import threading
import secrets

from datetime import date, datetime, timezone, timedelta
from application import bcrypt
from application.handlers import handle_exceptions
from application.repository.user_repository import UserRepository
from application.proxy.apiperu import ApiPeru
from application.proxy.whatsapp import Whatsapp
from flask_jwt_extended import create_access_token


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.apiperu = ApiPeru()
        self.whatsapp = Whatsapp()
        

    @handle_exceptions
    def extract_data(self, payload):
        entry = payload.get("entry", [])[0]
        change = entry.get("changes", [])[0]
        value = change.get("value", {})

        contacts = value.get("contacts", [])
        wa_id = contacts[0].get("wa_id") if contacts else None

        messages = value.get("messages", [])
        message_text = messages[0].get("text", {}).get("body") if messages else None

        if not wa_id or not message_text:
            return "Missing 'wa_id' or 'message'", 400
        
        return {
            "phone": wa_id,
            "message": message_text
        }, 200


    @handle_exceptions
    def process_webhook(self, data):
        extract, extract_status = self.extract_data(data)
        if extract_status != 200:
            return extract, extract_status
        
        return extract, 200
        

    @handle_exceptions
    def get_department_team(self, admin_id):
        user, user_status = self.user_repository.get_user_by_id(admin_id)
        if user_status != 200:
            return user, user_status
        
        if user.level_id == 1:
            return "Usuario sin acceso al sistema", 400
        
        team, team_status = self.user_repository.get_department_team(user.department_id)
        if team_status != 200:
            return team, team_status
        
        team_dict = [
            {
                "id": teammate.id,
                "name": self.format_name(teammate.name),
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
        
        name = self.format_name(user.name).split()
        response = {
            "id": user.id,
            "image": user.image if user.image else 'user_default.jpg',
            "name": name[0],
            "department_name": user.department.name,
        }

        if user.password == "password":
            response["first_login"] = True

        return response, 200
    

    @handle_exceptions
    def create_pin(self, document, pin, phone):
        user, user_status = self.user_repository.get_user_by_document(document)
        if user_status != 200:
            return user, user_status
        
        hashed_pin = bcrypt.generate_password_hash(pin).decode("utf-8")
        return self.user_repository.set_user_pin(user, hashed_pin, phone)
    
    
    @handle_exceptions
    def login(self, document, password, fcm_token):
        user, user_status = self.user_repository.get_user_by_document(document)
        if user_status != 200:
            return user, user_status
        
        if user.level_id == 1:
            return "No cuentas con acceso al sistema", 400

        if user.password == "password":
            return "Contraseña reseteada", 422

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
                "name": self.format_name(user.name),
                "phone": user.phone[2:],
                "image": user.image if user.image else 'user_default.jpg',
                "default_page": user.default_page or "logistics",
                "token": access_token
            }
            return user_data, 200
        
        return "Clave incorrecta", 400
    
    
    @handle_exceptions
    def format_name(self, full_name):
        words = full_name.strip().split()

        if len(words) == 1:
            return f"{words[0]}"
        if len(words) == 2:
            return f"{words[0]} {words[1]}"
        if len(words) == 3:
            return f"{words[0]} {words[1]}"
        elif len(words) == 4:
            return f"{words[0]} {words[2]}"
        elif len(words) == 5:
            return f"{words[0]} {words[3]}"
        return "Texto no válido"
        

    def generate_otp(self, length=6):
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])


    @handle_exceptions
    def send_otp(self, user_id, phone):
        user, user_status = self.user_repository.get_user_by_id(user_id)
        if user_status != 200:
            return user, user_status
        
        if user.level_id == 1:
            return "No cuentas con acceso al sistema", 400
        
        otp_code = self.generate_otp()
        add_otp, add_otp_status = self.user_repository.add_otp(user_id, phone, otp_code)
        if add_otp_status != 200:
            return add_otp, add_otp_status
        
        threading.Thread(target=self.whatsapp.otp, args=(phone, otp_code)).start()
        return "OTP Enviado correctamente", 200
    

    @handle_exceptions
    def validate_otp(self, user_id, phone, otp_code):
        user, user_status = self.user_repository.get_user_by_id(user_id)
        if user_status != 200:
            return user, user_status
        
        if user.level_id == 1:
            return "No cuentas con acceso al sistema", 400
        
        current_otp, current_otp_status = self.user_repository.get_otp(user_id, phone)
        if current_otp_status != 200:
            return current_otp, current_otp_status
        
        utc_now = datetime.now(timezone.utc)
        peru_time = (utc_now - timedelta(hours=5)).replace(tzinfo=None)
        if current_otp.created_at < peru_time - timedelta(minutes=10):
            return "Código expirado", 422
        
        if otp_code != current_otp.otp:
            return "Código inválido", 422

        return "Código validado correctamente", 200