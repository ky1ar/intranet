from application.handlers import handle_db_exceptions
from application.models import ServiceOrders, ServiceOrderStatus
from sqlalchemy import func
from flask import g


class SupportRepository:
    @handle_db_exceptions
    def get_service_order_by_number_and_document(self, order_number, document):
        service_order = (
            g.db_session.query(ServiceOrders)
            .filter(
                ServiceOrders.order_number == order_number,
                ServiceOrders.client.has(document=document)
            )
            .first()
        )

        if not service_order:
            return 'Orden no localizada, verifique los datos', 400

        return service_order, 200
    

    @handle_db_exceptions
    def get_service_order_by_number(self, order_number):
        service_order = (
            g.db_session.query(ServiceOrders)
            .filter(ServiceOrders.order_number == order_number)
            .first()
        )
        if not service_order:
            return 'Orden no localizada, verifique los datos', 400

        return service_order, 200
    

    @handle_db_exceptions
    def get_order_status(self, service_order_id, current_status_id):
        service_order = (
            g.db_session.query(ServiceOrderStatus)
            .filter(ServiceOrderStatus.service_order_id == service_order_id, ServiceOrderStatus.status_id == current_status_id)
            .first()
        )
        if not service_order:
            return 'Estado de Orden no localizada, verifique los datos', 400

        return service_order, 200
    

    @handle_db_exceptions
    def delete_order_status(self, order_status):
        g.db_session.delete(order_status)
        g.db_session.commit()
        return True, 200
    

    @handle_db_exceptions
    def next_service_order(self, service_order, current_status_id, stamp):
        if current_status_id > 8:
            return "La orden ha alcanzado el status máximo", 400

        service_order.status_id = current_status_id + 1
        service_order.updated_at = stamp

        g.db_session.add(service_order)
        g.db_session.commit()
        return True, 200
    

    @handle_db_exceptions
    def prev_service_order(self, service_order, current_status_id, stamp):
        if current_status_id < 2:
            return "La orden ha alcanzado el status mínimo", 400

        service_order.status_id = current_status_id - 1
        service_order.updated_at = stamp

        g.db_session.add(service_order)
        g.db_session.commit()
        return True, 200
    
    
    @handle_db_exceptions
    def new_order_status(self, service_order_id, current_status_id, user_id, stamp, notes):
        new_order_status = ServiceOrderStatus(
            service_order_id=service_order_id,
            status_id=current_status_id + 1,
            user_id=user_id,
            register_at=stamp,
            notes=notes
        )
        g.db_session.add(new_order_status)
        g.db_session.commit()
        return True, 200
    
    
    @handle_db_exceptions
    def get_service_order_history(self, service_order_id):
        history = (
            g.db_session.query(ServiceOrderStatus)
            .filter(ServiceOrderStatus.service_order_id == service_order_id)
            .all()
        )
        if not history:
            return [], 200

        return history, 200


    @handle_db_exceptions
    def get_working_service_order(self):
        service_order = (
            g.db_session.query(ServiceOrders)
            .filter(ServiceOrders.status_id != 9)
            .all()
        )
        if not service_order:
            return [], 200

        return service_order, 200
    

    @handle_db_exceptions
    def add_service_order(self, data):
        new_service_order = ServiceOrders(
            order_number=data.get("order_number"),
            machine_id=data.get("machine_id"),
            client_id=data.get("client_id"),
            technician_id=data.get("technician_id"),
            method_id=data.get("method_id"),
            origin_id=data.get("origin_id"),
            status_id=data.get("status_id"),
            register_at=data.get("register_at"),
            comments=data.get("comments"),
        )

        g.db_session.add(new_service_order)
        g.db_session.flush()
        shipping_order_id = new_service_order.id
        g.db_session.commit()
        return shipping_order_id, 200
    

    @handle_db_exceptions
    def get_next_order_number(self):
        last_order = g.db_session.query(func.max(ServiceOrders.order_number)).scalar()
        return int(last_order or 0) + 1


    @handle_db_exceptions
    def new_service_order(self, data):
        new_service_order = ServiceOrders(
            order_number=data.get("order_number"),
            machine_id=data.get("machine_id"),
            technician_id=data.get("technician_id"),
            client_id=data.get("client_id"),
            status_id=data.get("status_id"),
            register_at=data.get("register_at"),
            comments="",
        )

        g.db_session.add(new_service_order)
        g.db_session.flush()
        shipping_order_id = new_service_order.id
        g.db_session.commit()
        return shipping_order_id, 200
    

    @handle_db_exceptions
    def add_order_status(self, service_order_id, data):
        new_order_status = ServiceOrderStatus(
            service_order_id=service_order_id,
            status_id=data.get("status_id"),
            user_id=data.get("user_id"),
            register_at=data.get("register_at"),
            notes=data.get("notes"),
        )

        g.db_session.add(new_order_status)
        g.db_session.commit()
        return new_order_status, 200
    
        