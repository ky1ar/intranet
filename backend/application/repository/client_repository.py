import logging
from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_db_exceptions
from application.models import Clients, ClientOrders
from flask import g


class ClientRepository:
    def __init__(self):
        self.support_department = 5
        self.admin_level = 3


    @handle_db_exceptions
    def get_client_by_document(self, document):
        client = g.db_session.query(Clients).filter_by(document=document).first()
        if not client:
            return 'No se encontró el cliente', 404

        return client, 200
        

    @handle_db_exceptions
    def get_client_order_by_number(self, order_number):
        user_order = g.db_session.query(ClientOrders).filter_by(number=order_number).first()
        if not user_order:
            return 'Orden de cliente no encontrada', 404

        return user_order, 200

    @handle_db_exceptions
    def get_client_order_by_id(self, order_id):
        user_order = g.db_session.query(ClientOrders).filter_by(id=order_id).first()
        if not user_order:
            return 'Orden de cliente no encontrada', 404

        return user_order, 200
    

    @handle_db_exceptions
    def get_client_order(self, order_number, client_id):
        user_order = g.db_session.query(ClientOrders).filter(ClientOrders.number == order_number, ClientOrders.client_id == client_id).first()
        if not user_order:
            return 'Orden de cliente no encontrada', 404

        return user_order, 200
    

    @handle_db_exceptions
    def get_client_by_id(self, id):
        client = g.db_session.query(Clients).filter_by(id=id).first()
        if not client:
            return 'Cliente no encontrado', 404

        return client, 200
    

    @handle_db_exceptions
    def get_client_orders(self, client_id):
        orders = (
            g.db_session.query(ClientOrders)
            .filter(ClientOrders.client_id == client_id)
            .all()
        )
        if not orders:
            return "No se encontraron ordenes", 404

        return orders, 200
    

    @handle_db_exceptions
    def get_all_clients(self, page=1, per_page=20):
        query = (
            g.db_session.query(Clients)
            .order_by(Clients.name)
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
    def add_client(self, client):
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)

        new_client = Clients(
            document=client.get("document"),
            name=client.get("name"),
            email=client.get("email"),
            phone=f'51{client.get("phone")}',
            department_id=client.get("department_id"),
            province_id=client.get("province_id"),
            district_id=client.get("district_id"),
            address=client.get("address"),
            stamp=peru_time,
        )
        g.db_session.add(new_client)
        g.db_session.flush()
        client_id = new_client.id
        g.db_session.commit()
        logging.info(f"New client added to DB with id {client_id}")
        return client_id, 200

    
    @handle_db_exceptions
    def add_client_order(self, order_number, client_id):
        new_client_order = ClientOrders(
            number=order_number,
            client_id=client_id,
        )

        g.db_session.add(new_client_order)
        g.db_session.flush()
        client_order_id = new_client_order.id
        g.db_session.commit()
        logging.info(f"New client order added to DB with id {client_order_id}")
        return client_order_id, 200
    

    @handle_db_exceptions
    def add_client_minimal(self, document, name, email=None, phone=None):
        new_client = Clients(
            document=document,
            name=name,
            email=email,
            phone=f'51{phone}' if phone else None,
            address="",
        )
        g.db_session.add(new_client)
        g.db_session.flush()
        client_id = new_client.id
        g.db_session.commit()
        return client_id, 200

    @handle_db_exceptions
    def update_client_contact(self, client, email=None, phone=None):
        if email:
            client.email = email
        if phone:
            client.phone = f'51{phone}'
        g.db_session.commit()
        return client, 200

    @handle_db_exceptions
    def update_client(self, client, data):
        client.phone = f'51{data.get("phone")}'
        client.email = data.get("email")
        client.department_id = data.get("department_id")
        client.province_id = data.get("province_id")
        client.district_id = data.get("district_id")
        client.address = data.get("address")
        
        g.db_session.add(client)
        g.db_session.flush()
        g.db_session.commit()
        
        return client, 200
    