
from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_db_exceptions
from application.models import TrackingOrders, TrackingOrderStatus, TrackingAgencies
from flask import g


class TrackingRepository:
    @handle_db_exceptions
    def add_tracking_order(self, data, tracking_data):
        last_status_date = None
        status_data = tracking_data.get("status_data")
        last_status_id = tracking_data.get("last_status_id")
        if last_status_id == 1:
            last_status_date = status_data.get("agency_at")
        elif last_status_id == 2:
            last_status_date = status_data.get("onway_at")
        elif last_status_id == 3:
            last_status_date = status_data.get("delivered_at")

        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)

        new_tracking_order = TrackingOrders(
            client_order_id=data.get("client_order_id"),
            agency_id=data.get("agency_id"),
            status_id=last_status_id,
            code1=data.get("code1"),
            code2=data.get("code2"),
            code3=data.get("code3"),
            origin_agency=tracking_data.get("origin_agency"),
            destination_agency=tracking_data.get("destination_agency"),
            external_id=tracking_data.get("external_id"),
            register_at=peru_time,
            updated_at=last_status_date,
        )

        g.db_session.add(new_tracking_order)
        g.db_session.flush()
        tracking_order_id = new_tracking_order.id
        g.db_session.commit()
        return tracking_order_id, 200
    

    @handle_db_exceptions
    def get_list(self, order_ids):
        order_list = (
            g.db_session.query(TrackingOrders)
            .filter(TrackingOrders.client_order_id.in_(order_ids))
            .all()
        )
        if not order_list:
            return [], 200

        return order_list, 200
    

    @handle_db_exceptions
    def get_all_list(self):
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_orders = (
            g.db_session.query(TrackingOrders)
            .filter(TrackingOrders.register_at >= thirty_days_ago)
            .order_by(TrackingOrders.register_at.desc())
            .all()
        )

        return recent_orders, 200


    @handle_db_exceptions
    def get_tracking_order(self, client_order_id):
        tracking_order = (
            g.db_session.query(TrackingOrders)
            .filter(TrackingOrders.client_order_id == client_order_id)
            .first()
        )
        if not tracking_order:
            return 'Tracking Orden no localizada', 400

        return tracking_order, 200
    

    @handle_db_exceptions
    def get_agency(self, agency_id):
        agency = (
            g.db_session.query(TrackingAgencies)
            .filter(TrackingAgencies.id == agency_id)
            .first()
        )
        if not agency:
            return 'Agencia no localizada', 400

        return agency, 200


    @handle_db_exceptions
    def get_tracking_order_by_id(self, id):
        tracking_order = (
            g.db_session.query(TrackingOrders)
            .filter(TrackingOrders.id == id)
            .first()
        )
        if not tracking_order:
            return 'Tracking Orden no localizada', 400

        return tracking_order, 200


    @handle_db_exceptions
    def get_tracking_order_by_id(self, tracking_order_id):
        tracking_order = (
            g.db_session.query(TrackingOrders)
            .filter(TrackingOrders.id == tracking_order_id)
            .first()
        )
        if not tracking_order:
            return 'Tracking Orden no localizada', 400

        return tracking_order, 200


    @handle_db_exceptions
    def add_tracking_history(self, tracking_order_id, status_data):
        status_mapping = {
            'agency_at': 1,
            'onway_at': 2,
            'delivered_at': 3
        }
            
        for key, timestamp in status_data.items():
            if not timestamp:
                continue

            g.db_session.add(TrackingOrderStatus(
                tracking_order_id=tracking_order_id,
                status_id=status_mapping.get(key),
                register_at=timestamp
            ))

        g.db_session.commit()
        return True, 200
    

    @handle_db_exceptions
    def get_tracking_history(self, tracking_order_id):
        order_history = (
            g.db_session.query(TrackingOrderStatus)
            .filter(TrackingOrderStatus.tracking_order_id == tracking_order_id)
            .all()
        )
        if not order_history:
            return [], 400

        return order_history, 200
