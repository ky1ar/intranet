import logging
from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_db_exceptions
from application.models import Users, UserCodes
from flask import g


class UserRepository:
    def __init__(self):
        self.support_department = 5
        self.admin_level = 3


    @handle_db_exceptions
    def get_user_by_document(self, document):
        user = g.db_session.query(Users).filter_by(document=document).first()
        if not user:
            return 'No se encontró el usuario', 404

        return user, 200
        

    @handle_db_exceptions
    def get_user_by_id(self, user_id):
        user = g.db_session.query(Users).filter_by(id=user_id).first()
        if not user:
            return 'Usuario no encontrado', 404

        return user, 200
    

    @handle_db_exceptions
    def get_otp(self, user_id, phone):
        otp_code = (
            g.db_session.query(UserCodes)
            .filter(
                UserCodes.user_id == user_id,
                UserCodes.phone == phone,
            )
            .order_by(UserCodes.created_at.desc())
            .first()
        )

        if not otp_code:
            return 'Código inválido', 422

        return otp_code, 200


    @handle_db_exceptions
    def add_otp(self, user_id, phone, otp_code):
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)

        new_otp = UserCodes(
            user_id=user_id,
            phone=phone,
            otp=otp_code,
            created_at=peru_time
        )
        g.db_session.add(new_otp)
        g.db_session.commit()
        return True, 200
    

    @handle_db_exceptions
    def get_department_team(self, department_id):
        query = g.db_session.query(Users).filter(Users.level_id != 1)

        if department_id != 7:
            query = query.filter(Users.department_id == department_id)

        team = query.order_by(Users.name).all()

        return team or [], 200
    
    
    @handle_db_exceptions
    def set_user_pin(self, user, pin, phone):
        user.password = pin
        user.phone = f"51{phone}"

        g.db_session.add(user)
        g.db_session.commit()
        return "Usuario actualizado correctamente", 200
    

    @handle_db_exceptions
    def get_support_leader(self):
        leader =  g.db_session.query(Users).filter(
            Users.department_id == self.support_department,
            Users.level_id == self.admin_level
        ).first()
        
        if not leader:
            leader = g.db_session.query(Users).filter(
                Users.department_id == self.support_department
            ).first()
            
        return leader
