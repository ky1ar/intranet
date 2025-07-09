import logging
from datetime import datetime, timezone, timedelta
from application.handlers import handle_db_exceptions
from application.models import ServiceOrders, ServiceOrderStatus, ServiceLinks, ServiceStatus, Users, Clients, db
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
    def get_orders_by_status(self):
        orders_by_status = (
            g.db_session.query(
                ServiceStatus.id,
                ServiceStatus.name,
                func.count(ServiceOrders.id).label("count")
            )
            .outerjoin(ServiceOrders, ServiceOrders.status_id == ServiceStatus.id)
            .filter(ServiceOrders.status_id != 9)
            .group_by(ServiceStatus.id, ServiceStatus.name)
            .order_by(ServiceStatus.id)
            .all()
        )
        if not orders_by_status:
            return 'No se encontraron órdenes', 404

        return orders_by_status, 200


    @handle_db_exceptions
    def get_orders_by_month(self):
        orders_by_month = (
            g.db_session.query(
                func.date_format(ServiceOrders.register_at, "%Y-%m").label('period'),
                func.count(ServiceOrders.id)
            )
            .group_by('period')
            .order_by('period')
            .all()
        )
        if not orders_by_month:
            return 'No se encontraron órdenes', 404

        return orders_by_month, 200
    

    @handle_db_exceptions
    def get_orders_by_tech(self):
        orders_by_tech = (
            g.db_session.query(Users.name, func.count(ServiceOrders.id))
            .join(ServiceOrders, ServiceOrders.technician_id == Users.id)
            .filter(Users.level_id != 1)
            .filter(Users.id != 21)
            .group_by(Users.name)
            .all()
        )
        if not orders_by_tech:
            return 'No se encontraron órdenes', 404

        return orders_by_tech, 200
    

    @handle_db_exceptions
    def get_total_orders(self):
        orders = g.db_session.query(func.count(ServiceOrders.id)).scalar()
        if not orders:
            return None, 200

        return orders, 200


    @handle_db_exceptions
    def get_today_total_orders(self):
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        today_total = (
            g.db_session.query(func.count(ServiceOrders.id))
            .filter(func.date(ServiceOrders.register_at) == today.date())
            .scalar()
        )
        if not today_total:
            return None, 200

        return today_total, 200
    

    @handle_db_exceptions
    def get_week_total_orders(self):
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_week = today - timedelta(days=today.weekday())
        week_total = (
            g.db_session.query(func.count(ServiceOrders.id))
            .filter(ServiceOrders.register_at >= start_of_week)
            .scalar()
        )
        if not week_total:
            return None, 200

        return week_total, 200
    

    @handle_db_exceptions
    def get_month_total_orders(self):
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_month = today.replace(day=1)
        month_total = (
            g.db_session.query(func.count(ServiceOrders.id))
            .filter(ServiceOrders.register_at >= start_of_month)
            .scalar()
        )
        if not month_total:
            return None, 200

        return month_total, 200
    

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
        #if current_status_id > 8:
        #    return "La orden ha alcanzado el status máximo", 400

        service_order.status_id = current_status_id + 1
        service_order.updated_at = stamp

        g.db_session.add(service_order)
        g.db_session.commit()
        return True, 200
    

    @handle_db_exceptions
    def update_service_order(self, service_order, data):
        allowed_fields = {'method_id', 'technician_id', 'origin_id', 'pay_amount', 'paid'}
        updated_fields = []

        for key in allowed_fields:
            if key in data:
                setattr(service_order, key, data[key])
                updated_fields.append(key)

        if updated_fields:
            g.db_session.add(service_order)
            g.db_session.commit()
            return "Updated fields", 200
        return "No fields updated", 200


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
    def create_link(self, token, user_id):
        duration_hours = 24
        utc_now = datetime.now(timezone.utc)
        created_at = utc_now - timedelta(hours=5)
        expires_at = created_at + timedelta(hours=duration_hours)

        service_link = ServiceLinks(
            token=token,
            status_id=1,
            user_id=user_id,
            created_at=created_at,
            expires_at=expires_at,
        )
        g.db_session.add(service_link)
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
    def get_working_service_order(self, leader, user):
        query = g.db_session.query(ServiceOrders).filter(ServiceOrders.status_id != 9)

        if user.department_id == 5 and user.id != leader.id:
            query = query.filter(ServiceOrders.technician_id == user.id)

        service_order = query.all()

        if not service_order:
            return [], 200

        return service_order, 200
    

    @handle_db_exceptions
    def get_ready_service_order(self):
        query = g.db_session.query(ServiceOrders).filter(ServiceOrders.status_id == 8)
        service_order = query.all()

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
    def get_all_service_orders(self, page=1, per_page=20):
        query = (
            g.db_session.query(ServiceOrders)
            .order_by(ServiceOrders.id.desc())
        )

        total = query.count()
        list = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            "list": list,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page 
        }, 200
    

    @handle_db_exceptions
    def get_service_links_history(self, page=1, per_page=20):
        query = (
            g.db_session.query(ServiceLinks)
            .order_by(ServiceLinks.id.desc())
        )

        total = query.count()
        list = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            "list": list,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page 
        }, 200
    

    def get_next_order_number(self):
        last_order = g.db_session.query(func.max(ServiceOrders.order_number)).scalar()
        return max(int(last_order or 0) + 1, 10001)


    @handle_db_exceptions
    def new_service_order(self, order_number, leader_id, data):
        new_service_order = ServiceOrders(
            order_number=order_number,
            machine_id=data.get("machine_id"),
            client_id=data.get("client_id"),
            technician_id=leader_id,
            method_id=data.get("method_id"),
            origin_id=data.get("origin_id"),
            status_id=data.get("status_id"),
            register_at=data.get("register_at"),
            comments=data.get("signature", ""),
        )

        g.db_session.add(new_service_order)
        g.db_session.flush()
        shipping_order_id = new_service_order.id
        g.db_session.commit()
        return shipping_order_id, 200
    

    @handle_db_exceptions
    def add_order_status(self, service_order_id, user_id, data):
        new_order_status = ServiceOrderStatus(
            service_order_id=service_order_id,
            status_id=data.get("status_id"),
            user_id=user_id,
            register_at=data.get("register_at"),
            notes=data.get("notes"),
        )

        g.db_session.add(new_order_status)
        g.db_session.commit()
        return new_order_status, 200
    
    
    @handle_db_exceptions
    def get_service_by_id(self, service_order_id):
        service_order = (
            g.db_session.query(ServiceOrders)
            .filter(ServiceOrders.id == service_order_id)
            .first()
        )

        if not service_order:
            return 'Orden no encontrada', 404
        return service_order, 200
    

    @handle_db_exceptions
    def get_link(self, link_id):
        link = (
            g.db_session.query(ServiceLinks)
            .filter(ServiceLinks.id == link_id)
            .first()
        )

        if not link:
            return 'Link no encontrado', 404
        return link, 200
    

    @handle_db_exceptions
    def get_link_by_token(self, token):
        link = (
            g.db_session.query(ServiceLinks)
            .filter(ServiceLinks.token == token)
            .first()
        )

        if not link:
            return 'Link no encontrado', 404
        return link, 200


    @handle_db_exceptions
    def update_link(self, link):
        link.status_id = 2

        g.db_session.add(link)
        g.db_session.commit()
        return True, 200


    @handle_db_exceptions
    def update_link_client(self, link, order_number, client_id):
        link.status_id = 3
        link.order_number = order_number
        link.client_id = client_id

        g.db_session.add(link)
        g.db_session.commit()
        return True, 200
    

    @handle_db_exceptions
    def delete_link(self, link):
        link.status_id = 5

        g.db_session.add(link)
        g.db_session.commit()
        return True, 200
    

    @handle_db_exceptions
    def get_orders_like(self, order_number):
        search_term = f"%{order_number}%"

        results = (
            g.db_session.query(ServiceOrders)
            .join(Clients, ServiceOrders.client_id == Clients.id)
            .filter(
                db.or_(
                    db.cast(ServiceOrders.order_number, db.String).ilike(search_term),
                    Clients.name.ilike(search_term),
                    Clients.document.ilike(search_term)
                )
            )
            .order_by(ServiceOrders.order_number.desc())
            .distinct()
            .all()
        )
        if not results:
            return None, 400

        return results, 200