import logging
import threading
import secrets
from datetime import date, datetime, timezone, timedelta
from application import bcrypt
from application.handlers import handle_exceptions
from application.utils import format_name, generate_otp
from application.repository.user_repository import UserRepository
from application.repository.push_repository import PushRepository
from application.services.module_service import ModuleService
from application.proxy.apiperu import ApiPeru
from application.proxy.whatsapp import Whatsapp
from flask_jwt_extended import create_access_token, get_jwt_identity


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.push_repository = PushRepository()
        self.module_service = ModuleService()
        self.apiperu = ApiPeru()
        self.whatsapp = Whatsapp()
        

    @handle_exceptions
    def get_department_team(self, user_id):
        user, user_status = self.user_repository.get_user_by_id(user_id)
        if user_status != 200:
            return user, user_status

        if user.level_id == 1:
            return "Usuario sin acceso al sistema", 400

        team, team_status = self.user_repository.get_department_team(user.department_id)
        if team_status != 200:
            return team, team_status

        if user.department_id == 7:
            team = [t for t in team if t.level_id != 5]

        team_dict = [
            {
                "id": teammate.id,
                "level_id": teammate.level_id,
                "name": format_name(teammate.name),
                "department_name": teammate.department.name,
                "image": teammate.image if teammate.image else 'user_default.jpg',
            } for teammate in team
        ]

        team_dict = sorted(team_dict, key=lambda x: 0 if x["level_id"] == 5 else 1)

        return team_dict, 200


    def _has_attendance_perm(self, user_id, perm_slug):
        result, code = self.module_service.check_permission(user_id, 'attendance', perm_slug)
        if code != 200:
            return False
        return result.get('granted', False) if isinstance(result, dict) else False


    def _get_attendance_visible_depts(self, user_id):
        modules_data, _ = self.module_service.get_user_modules(user_id)
        if not isinstance(modules_data, list):
            return []
        
        perms = {}
        for m in modules_data:
            if m['slug'] == 'attendance':
                perms = m.get('permissions', {})
                break
        return [s.replace('view_', '') for s, g in perms.items() if g and s.startswith('view_')]

        
    @handle_exceptions
    def get_attendance_team(self, user_id):
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc

        if user.level_id == 1:
            return "Usuario sin acceso al sistema", 400

        has_view_all = self._has_attendance_perm(user_id, 'view_all') or self._has_attendance_perm(user_id, 'monitor')

        if has_view_all:
            team, tc = self.user_repository.get_all_team()
        else:
            dept_slugs = self._get_attendance_visible_depts(user_id)
            if dept_slugs:
                team, tc = self.user_repository.get_team_by_department_slugs(dept_slugs)
            else:
                return [], 200  # no ve a nadie más

        if tc != 200:
            return team, tc

        team_dict = [
            {
                "id": t.id,
                "level_id": t.level_id,
                "name": format_name(t.name),
                "department_name": t.department.name,
                "image": t.image if t.image else 'user_default.jpg',
            } for t in team
        ]

        return team_dict, 200
    

    @handle_exceptions
    @handle_exceptions
    def upload_avatar(self, user_id, file):
        from PIL import Image
        import os
        from werkzeug.utils import secure_filename

        ALLOWED = {"image/jpeg", "image/png", "image/webp"}
        if file.mimetype not in ALLOWED:
            return "Formato no permitido. Solo JPG, PNG o WEBP", 400

        img = Image.open(file.stream).convert("RGBA" if file.mimetype == "image/webp" else "RGB")

        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top  = (h - side) // 2
        img  = img.crop((left, top, left + side, top + side))
        img  = img.resize((512, 512), Image.LANCZOS)

        ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}[file.mimetype]
        ts = int(datetime.now().timestamp())
        filename = secure_filename(f"user_{user_id}_avatar_{ts}.{ext}")
        upload_dir = "/shared_uploads/users"
        os.makedirs(upload_dir, exist_ok=True)
        save_path = os.path.join(upload_dir, filename)

        if ext == "jpg":
            img.convert("RGB").save(save_path, "JPEG", quality=90)
        elif ext == "png":
            img.save(save_path, "PNG")
        else:
            img.save(save_path, "WEBP", quality=90)

        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc == 200 and user.image and user.image != filename:
            old_path = os.path.join(upload_dir, user.image)
            try:
                if os.path.exists(old_path):
                    os.remove(old_path)
            except OSError:
                pass

        return self.user_repository.update_user_image(user_id, filename)


    def get_user_by_document(self, document):
        user, user_status = self.user_repository.get_user_by_document(document)
        if user_status != 200:
            return user, user_status
        
        if user.level_id == 1:
            return "No cuentas con acceso al sistema", 400
        
        name = format_name(user.name).split()
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
    def verify(self):
        user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc
        
        if user.level_id < 2:
            return "Usuario sin acceso al sistema", 403

        modules_data, _ = self.module_service.get_user_modules(user.id)
        default_page, _ = self.module_service.get_default_page(user.id)

        return {
            "app_version": "1.7.7",
            "id": user.id,
            "level_id": user.level_id,
            "department_id": user.department_id,
            "department_name": user.department.name,
            "document": user.document,
            "name": format_name(user.name),
            "phone": user.phone[2:],
            "image": user.image if user.image else 'user_default.jpg',
            "default_page": default_page,
            "modules": modules_data if isinstance(modules_data, list) else [],
            "nav_order": user.nav_order or [],
        }, 200


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
            
            modules_data, _ = self.module_service.get_user_modules(user.id)
            default_page, _ = self.module_service.get_default_page(user.id)

            user_data = {
                "id": user.id,
                "level_id": user.level_id,
                "department_id": user.department_id,
                "department_name": user.department.name,
                # "shipping_app_level": user.shipping_app_level,
                "document": user.document,
                "name": format_name(user.name),
                "phone": user.phone[2:],
                "image": user.image if user.image else 'user_default.jpg',
                "default_page": default_page,
                "modules": modules_data if isinstance(modules_data, list) else [],
                "nav_order": user.nav_order or [],
                "token": access_token
            }
            return user_data, 200
        
        return "Clave incorrecta", 400
    

    @handle_exceptions
    def send_otp(self, user_id, phone):
        user, user_status = self.user_repository.get_user_by_id(user_id)
        if user_status != 200:
            return user, user_status
        
        if user.level_id == 1:
            return "No cuentas con acceso al sistema", 400
        
        otp_code = generate_otp()
        add_otp, add_otp_status = self.user_repository.add_otp(user_id, phone, otp_code)
        if add_otp_status != 200:
            return add_otp, add_otp_status
        
        if not phone.startswith("51"):
            phone = f"51{phone}"
            
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


    @handle_exceptions
    def register_device(self, device_id, fcm_token, device_platform, user_agent):
        user_id = int(get_jwt_identity())
        return self.push_repository.upsert_token(user_id, device_id, fcm_token, device_platform, user_agent)