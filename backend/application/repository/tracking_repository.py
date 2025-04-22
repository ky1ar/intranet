
from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_db_exceptions
from application.models import TrackingOrders
from flask import g


class TrackingRepository:
    @handle_db_exceptions
    def add_tracking_order(self, data):
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)

        new_tracking_order = TrackingOrders(
            user_order_id=data.get("user_order_id"),
            agency_id=data.get("agency_id"),
            status_id=1,
            code1=data.get("code1"),
            code2=data.get("code2"),
            origin_agency=data.get("origin_agency"),
            destination_agency=data.get("destination_agency"),
            external_id=data.get("external_id"),
            register_at=peru_time,
        )

        g.db_session.add(new_tracking_order)
        g.db_session.commit()
        return "Orden de rastreo creada exitosamente", 200
    

    @handle_db_exceptions
    def get_list(self, order_ids):
        order_list = (
            g.db_session.query(TrackingOrders)
            .filter(TrackingOrders.user_order_id.in_(order_ids))
            .all()
        )
        if not order_list:
            return [], 400

        return order_list, 200
    

    @handle_db_exceptions
    def get_tracking_order(self, user_order_id):
        tracking_order = (
            g.db_session.query(TrackingOrders)
            .filter(TrackingOrders.user_order_id == user_order_id)
            .first()
        )
        if not tracking_order:
            return 'Tracking Orden no localizada', 400

        return tracking_order, 200
    
