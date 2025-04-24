import logging
from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_db_exceptions
from application.models import Users, UserOrders
from flask import g


class UserRepository:
    def __init__(self):
        self.support_department = 5
        self.admin_level = 3


    @handle_db_exceptions
    def get_user_by_document(self, document):
        user = g.db_session.query(Users).filter_by(document=document).first()
        if not user:
            return 'No se encontró el usuario', 400

        return user, 200
        

    @handle_db_exceptions
    def get_user_by_user_order(self, user_order_id):
        user_order = g.db_session.query(UserOrders).filter_by(id=user_order_id).first()
        if not user_order:
            return 'Orden no encontrada', 404

        return user_order, 200


    @handle_db_exceptions
    def get_user_order_by_number(self, order_number):
        user_order = g.db_session.query(UserOrders).filter_by(number=order_number).first()
        if not user_order:
            return 'Orden no encontrada', 404

        return user_order, 200
    

    @handle_db_exceptions
    def get_user_by_id(self, id):
        user = g.db_session.query(Users).filter_by(id=id).first()
        if not user:
            return 'Usuario no encontrado', 400

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
    def get_user_orders(self, client_id):
        orders = (
            g.db_session.query(UserOrders)
            .filter(UserOrders.client_id == client_id)
            .all()
        )
        if not orders:
            return "No se encontraron ordenes", 400

        return orders, 200
    

    @handle_db_exceptions
    def get_all_clients(self, page=1, per_page=20):
        query = (
            g.db_session.query(Users)
            .filter(Users.level_id == 1)
            .order_by(Users.name)
        )

        total = query.count()
        clients = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            "clients": clients,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page 
        }, 200
    
    
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


    @handle_db_exceptions
    def add_client(self, client):
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)

        new_client = Users(
            level_id=1,
            document=client.get("document"),
            name=client.get("name"),
            email=client.get("email"),
            phone=f'51{client.get("phone")}',
            password="password",
            stamp=peru_time,
        )
        g.db_session.add(new_client)
        g.db_session.flush()
        client_id = new_client.id
        g.db_session.commit()
        logging.info(f"New client added to DB with id {client_id}")
        return client_id, 200


    @handle_db_exceptions
    def add_user_order(self, order_number, client_id):
        new_user_order = UserOrders(
            number=order_number,
            client_id=client_id,
        )

        g.db_session.add(new_user_order)
        g.db_session.flush()
        user_order_id = new_user_order.id
        g.db_session.commit()
        logging.info(f"New user order added to DB with id {user_order_id}")
        return user_order_id, 200
    

    @handle_db_exceptions
    def update_client(self, client, data):
        client.phone = f'51{data.get("phone")}'
        g.db_session.add(client)
        g.db_session.flush()
        g.db_session.commit()
        return client, 200