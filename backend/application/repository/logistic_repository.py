
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
        method_id = data.get("method_id")
        register_date = data.get("register_date")
        address = data.get("address", "").strip()
        district_id = data.get("district_id")
        maps = data.get("maps")
        assigned_id = data.get("assigned_id")
        driver_id = data.get("driver_id")

        updated_fields = {}
        if shipping_order.method_id != method_id:
            updated_fields["method_id"] = method_id
        if shipping_order.register_date != register_date:
            updated_fields["register_date"] = register_date
        if shipping_order.address != address:
            updated_fields["address"] = address
        if shipping_order.district_id != district_id:
            updated_fields["district_id"] = district_id
        if shipping_order.maps != maps:
            updated_fields["maps"] = maps
        if shipping_order.assigned_id != assigned_id:
            updated_fields["assigned_id"] = assigned_id
        if shipping_order.driver_id != driver_id:
            updated_fields["driver_id"] = driver_id

        if updated_fields:
            for field, value in updated_fields.items():
                setattr(shipping_order, field, value)
            g.db_session.add(shipping_order)
            g.db_session.commit()
        return updated_fields, 200
    

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
    