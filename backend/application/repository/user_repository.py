import logging
from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_db_exceptions
from application.models import Users, UserCodes, UserDepartment
from flask import g


class UserRepository:
    def __init__(self):
        self.support_department = 5
        self.management_department = 7
        self.admin_level = 3


    @handle_db_exceptions
    def get_user_by_document(self, document):
        user = g.db_session.query(Users).filter_by(document=document).first()
        if not user:
            return 'No se encontró el usuario', 404

        return user, 200
        

    @handle_db_exceptions
    def get_users_with_birthday(self):
        users = (
            g.db_session.query(Users)
            .filter(Users.birthday.isnot(None))
            .all()
        )
        return users, 200
    

    @handle_db_exceptions
    def get_department_ids_by_slugs(self, slugs):
        """Convierte department slugs a ids"""
        rows = (
            g.db_session.query(UserDepartment.id)
            .filter(UserDepartment.slug.in_(slugs))
            .all()
        )
        return [r[0] for r in rows], 200

    
    @handle_db_exceptions
    def get_user_by_id(self, user_id):
        user = g.db_session.query(Users).filter_by(id=user_id).first()
        if not user:
            return 'Usuario no encontrado', 404

        return user, 200
    

    @handle_db_exceptions
    def get_all_team(self):
        team = (
            g.db_session.query(Users)
            .filter(Users.level_id != 1, Users.level_id != 5)
            .order_by(Users.name)
            .all()
        )
        return team or [], 200


    @handle_db_exceptions
    def get_team_by_department_slugs(self, department_slugs):
        team = (
            g.db_session.query(Users)
            .join(UserDepartment, Users.department_id == UserDepartment.id)
            .filter(
                Users.level_id != 1,
                Users.level_id != 5,
                UserDepartment.slug.in_(department_slugs),
            )
            .order_by(Users.name)
            .all()
        )
        return team or [], 200


    @handle_db_exceptions
    def get_user_name_by_id(self, user_id):
        user = g.db_session.query(Users).filter_by(id=user_id).first()
        if not user:
            return 'Usuario', 200

        return user.name.split()[0], 200
    

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
    def get_custom_team(self, department_id, user_id):
        query = (
            g.db_session.query(Users)
            .filter(Users.level_id != 1)
            .filter(Users.level_id != 5)
            .filter(Users.department_id != 7)
            .filter(Users.id != 23)
            .filter(Users.id != 21)
        )

        if user_id == 15:
            query = query.filter(Users.department_id.in_([3, 4]))

        elif department_id != 7 and user_id not in [23, 1, 1123]:
            query = query.filter(Users.department_id == department_id)

        team = query.order_by(Users.name).all()
        return team or [], 200
    

    @handle_db_exceptions
    def get_all_user_ids(self):
        rows = g.db_session.query(Users.id).filter(Users.level_id != 1).all()
        return [r[0] for r in rows], 200


    @handle_db_exceptions
    def get_user_ids_by_department(self, department_id: int):
        rows = (
            g.db_session.query(Users.id)
            .filter(Users.department_id == department_id)
            .filter(Users.level_id != 1)
            .all()
        )
        return [r[0] for r in rows], 200


    @handle_db_exceptions
    def get_user_department_id(self, user_id: int):
        dep = g.db_session.query(Users.department_id).filter(Users.id == user_id).first()
        return (dep[0] if dep else None), 200
    

    @handle_db_exceptions
    def get_users_by_department(self, department_id):
        users = (
            g.db_session.query(Users)
            .filter(Users.department_id == department_id)
            .filter(Users.level_id != 1)
            .all()
        )
        return users or [], 200
    

    @handle_db_exceptions
    def get_all_users(self):
        users = g.db_session.query(Users).filter(Users.level_id != 1).order_by(Users.name).all()
        return users or [], 200
    
    
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


    @handle_db_exceptions
    def get_user_ids_by_department_slugs(self, department_slugs):
        """Retorna IDs de usuarios que pertenecen a los departamentos indicados por slug"""
        user_ids = (
            g.db_session.query(Users.id)
            .join(UserDepartment, Users.department_id == UserDepartment.id)
            .filter(
                UserDepartment.slug.in_(department_slugs),
                Users.level_id != 1,  # excluir inactivos
            )
            .all()
        )
        return [uid[0] for uid in user_ids], 200
        

    @handle_db_exceptions
    def get_leader(self, department_id):
        leader =  g.db_session.query(Users).filter(
            Users.department_id == department_id,
            Users.level_id == self.admin_level
        ).first()
        
        if not leader:
            leader = g.db_session.query(Users).filter(
                Users.department_id == department_id,
                Users.level_id != 1
            ).first()
            
        return leader, 200
    
    
    @handle_db_exceptions
    def get_manager(self):
        return g.db_session.query(Users).filter(Users.department_id == self.management_department).first(), 200
    