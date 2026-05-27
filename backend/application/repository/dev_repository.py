import logging
from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_db_exceptions
from application.models import UserContext
from flask import g


class DevRepository:
    def __init__(self):
        pass


    def peru_time(self):
        utc_now = datetime.now(timezone.utc)
        return utc_now - timedelta(hours=5)


    @handle_db_exceptions
    def get_users(self):
        users = g.db_session.query(UserContext).all()
        if not users:
            return 'No se encontró usuarios', 404
        return users, 200


    @handle_db_exceptions
    def get_all_pending_users(self, campaign):
        users = g.db_session.query(UserContext).filter(
            UserContext.status == 'idle',
            UserContext.campaign == campaign
        ).all()
        if not users:
            return 'No hay usuarios pendientes', 404
        return users, 200

    
    @handle_db_exceptions
    def get_accepted_users(self):
        users = g.db_session.query(UserContext).filter(UserContext.status == 'accepted').all()
        if not users:
            return 'No hay usuarios', 404
        return users, 200


    @handle_db_exceptions
    def get_user_by_phone(self, campaign, phone):
        user = g.db_session.query(UserContext).filter(
            UserContext.phone == phone,
            UserContext.campaign == campaign
        ).first()

        if not user:
            return 'No se encontró el usuario', 404
        return user, 200
    

    @handle_db_exceptions
    def get_confirmed_users(self):
        users = g.db_session.query(UserContext).filter(UserContext.status.in_(['accepted', 'reminded'])).all()
        if not users:
            return 'No hay usuarios', 404
        return users, 200
    

    @handle_db_exceptions
    def update_user(self, user, last_message_id=None, status=None):
        if not status:
            user.sended_at = self.peru_time()
            user.status = 'send'
            user.last_message_id = last_message_id
        else:
            user.updated_at = self.peru_time()
            user.status = status
        
        g.db_session.add(user)
        g.db_session.commit()
        return user, 200
    

    @handle_db_exceptions
    def get_all_users(self, campaign):
        users = g.db_session.query(UserContext).filter(
            UserContext.campaign == campaign
        ).all()
        if not users:
            return 'No hay usuarios', 404
        return users, 200


    @handle_db_exceptions
    def count_accepted_users(self):
        count = g.db_session.query(UserContext).filter(
            UserContext.status.in_(['accepted', 'reminded'])
        ).count()
        return count, 200