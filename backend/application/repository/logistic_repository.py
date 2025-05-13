
from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_db_exceptions
from application.models import ShippingOrders, ClientOrders, ShippingHistory
from sqlalchemy.orm import joinedload
from sqlalchemy import asc
from flask import g


class LogisticRepository:
    @handle_db_exceptions
    def get_scheduled_shippings(self, start_date, end_date):
        shipping_orders = (
            g.db_session.query(ShippingOrders)
            .filter(ShippingOrders.delivery_date >= start_date, ShippingOrders.delivery_date <= end_date)
            .filter(ShippingOrders.is_deleted.is_(False))
            .filter(ShippingOrders.status_id != 1)
            .options(
                joinedload(ShippingOrders.client_order).joinedload(ClientOrders.client)
            )
            .all()
        )
        
        if not shipping_orders:
            return [], 200
        
        return shipping_orders, 200
    

    @handle_db_exceptions
    def get_list(self, order_ids):
        order_list = (
            g.db_session.query(ShippingOrders)
            .filter(ShippingOrders.client_order_id.in_(order_ids))
            .all()
        )
        if not order_list:
            return [], 200

        return order_list, 200
    

    @handle_db_exceptions
    def get_orders_by_status(self, status_id):
        shipping_orders = (
            g.db_session.query(ShippingOrders)
            .filter(ShippingOrders.status_id == status_id)
            .filter(ShippingOrders.is_deleted.is_(False))
            .options(
                joinedload(ShippingOrders.client_order).joinedload(ClientOrders.client)
            )
            .order_by(asc(ShippingOrders.register_date))
            .all()
        )

        if not shipping_orders:
            return 'No se encontraron ordenes de pedido para este estado', 404
        
        return shipping_orders, 200
    

    
    @handle_db_exceptions
    def get_shipping_by_id(self, shipping_order_id):
        shipping_order = (
            g.db_session.query(ShippingOrders)
            .join(ClientOrders, ShippingOrders.client_order_id == ClientOrders.id)
            .filter(ShippingOrders.id == shipping_order_id)
            .filter(ShippingOrders.is_deleted.is_(False))
            .options(
                joinedload(ShippingOrders.client_order).joinedload(ClientOrders.client),
            )
            .first()
        )

        if not shipping_order:
            return 'Orden de pedido no encontrada', 404
        return shipping_order, 200
    

    @handle_db_exceptions
    def get_shipping_by_order_number(self, order_number):
        shipping_order = (
            g.db_session.query(ShippingOrders)
            .join(ClientOrders, ShippingOrders.client_order_id == ClientOrders.id)
            .filter(ClientOrders.number == order_number)
            .filter(ShippingOrders.is_deleted.is_(False))
            .options(
                joinedload(ShippingOrders.client_order).joinedload(ClientOrders.client),
            )
            .first()
        )

        if not shipping_order:
            return 'Orden de pedido no encontrada', 404
        return shipping_order, 200
    

    @handle_db_exceptions
    def get_shipping_by_client_order_id(self, client_order_id):
        shipping_order = (
            g.db_session.query(ShippingOrders)
            .join(ClientOrders, ShippingOrders.client_order_id == ClientOrders.id)
            .filter(ShippingOrders.client_order_id == client_order_id)
            .filter(ShippingOrders.is_deleted.is_(False))
            .filter(ShippingOrders.status_id != 6)
            .options(
                joinedload(ShippingOrders.client_order).joinedload(ClientOrders.client),
            )
            .first()
        )

        if not shipping_order:
            return 'Orden de pedido no encontrada', 404
        return shipping_order, 200
    

    @handle_db_exceptions
    def add_shipping_history(self, user_id, shipping_order_id, history_type, status=None, data=None):
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)

        new_history = ShippingHistory(
            user_id=user_id,
            shipping_order_id=shipping_order_id,
            type=history_type,
            created_at=peru_time
        )
        if status:
            new_history.status = status
        if data:
            new_history.data = data

        g.db_session.add(new_history)
        g.db_session.commit()
        return True, 200
    

    @handle_db_exceptions
    def update_shipping_order(self, shipping_order, data):
        direct_update_fields = ["delivery_date", "status_id", "schedule_id", "proof_photo"]
        conditional_fields = [
            "method_id", "register_date", "address",
            "district_id", "maps", "assigned_id", "driver_id"
        ]

        updated_fields = {}

        for field in direct_update_fields:
            value = data.get(field)
            if value is not None:
                setattr(shipping_order, field, value)

        for field in conditional_fields:
            new_value = data.get(field, "").strip() if field == "address" else data.get(field)
            current_value = getattr(shipping_order, field)
            if new_value and new_value != current_value:
                updated_fields[field] = new_value
                setattr(shipping_order, field, new_value)

        if updated_fields or any(data.get(f) is not None for f in direct_update_fields):
            g.db_session.add(shipping_order)
            g.db_session.commit()

        return updated_fields, 200
    

    @handle_db_exceptions
    def get_shipping_order(self, client_order_id):
        logistic_order = (
            g.db_session.query(ShippingOrders)
            .filter(ShippingOrders.client_order_id == client_order_id)
            .first()
        )
        if not logistic_order:
            return 'Logistic Orden no localizada', 400

        return logistic_order, 200
    

    @handle_db_exceptions
    def get_shipping_order_by_id(self, id):
        logistic_order = (
            g.db_session.query(ShippingOrders)
            .filter(ShippingOrders.id == id)
            .first()
        )
        if not logistic_order:
            return 'Logistic Orden no localizada', 400

        return logistic_order, 200
    

    @handle_db_exceptions
    def get_shipping_history(self, shipping_order_id):
        order_history = (
            g.db_session.query(ShippingHistory)
            .filter(ShippingHistory.shipping_order_id == shipping_order_id)
            .all()
        )
        if not order_history:
            return [], 400

        return order_history, 200
    

    @handle_db_exceptions
    def get_shipping_date(self, shipping_order_id, status):
        get_shipping_date = (
            g.db_session.query(ShippingHistory)
            .filter(ShippingHistory.shipping_order_id == shipping_order_id)
            .filter(ShippingHistory.status == status)
            .order_by(ShippingHistory.created_at)
            .first()
        )

        if not get_shipping_date:
            return None, 200

        return get_shipping_date, 200


    @handle_db_exceptions
    def add_shipping_order(self, data):
        new_shipping_order = ShippingOrders(
            client_order_id=data.get("client_order_id"),
            method_id=data.get("method_id"),
            driver_id=data.get("driver_id"),
            assigned_id=data.get("assigned_id"),
            status_id=1,
            address=data.get("address"),
            district_id=data.get("district_id"),
            comments=data.get("comments"),
            maps=data.get("maps"),
            register_date=data.get("register_date"),
        )

        g.db_session.add(new_shipping_order)
        g.db_session.flush()
        shipping_order_id = new_shipping_order.id
        g.db_session.commit()
        return shipping_order_id, 200
    

    @handle_db_exceptions
    def delete_shipping_order(self, shipping_order):
        shipping_order.is_deleted = True
        g.db_session.add(shipping_order)
        g.db_session.commit()
        return True, 200
    