import logging
from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_db_exceptions
from application.models import Users, ClientOrders
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
    def get_user_by_id(self, id):
        user = g.db_session.query(Users).filter_by(id=id).first()
        if not user:
            return 'Usuario no encontrado', 404

        return user, 200
    

    @handle_db_exceptions
    def get_department_team(self, admin_id, department_id):
        team = (
            g.db_session.query(Users)
            .filter(
                Users.department_id == department_id,
                Users.level_id != 1,
                Users.id != admin_id
            )
            .order_by(Users.name)
            .all()
        )
        if not team:
            return [], 200

        return team, 200
    
    
    @handle_db_exceptions
    def set_user_pin(self, user, pin):
        user.password = pin

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
