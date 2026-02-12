import logging
from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_db_exceptions
from application.models import TrackingOrders, TrackingOrderStatus, TrackingAgencies, ClientOrders, Clients,  db
from sqlalchemy import asc, func
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
            last_status_date = status_data.get("arrived_at")
        elif last_status_id == 4:
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
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)

        thirty_days_ago = peru_time - timedelta(days=15)
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
    def update_tracking_order(self, tracking_id, tracking_data):
        last_status_date = None
        status_data = tracking_data.get("status_data")
        last_status_id = tracking_data.get("last_status_id")
        if last_status_id == 1:
            last_status_date = status_data.get("agency_at")
        elif last_status_id == 2:
            last_status_date = status_data.get("onway_at")
        elif last_status_id == 3:
            last_status_date = status_data.get("arrived_at")
        elif last_status_id == 4:
            last_status_date = status_data.get("delivered_at")

        tracking = g.db_session.query(TrackingOrders).filter_by(id=tracking_id).first()
        if not tracking:
            return "Tracking no encontrado", 404

        tracking.status_id = last_status_id
        tracking.updated_at = last_status_date
        
        g.db_session.commit()
        return True, 200


    @handle_db_exceptions
    def add_tracking_history(self, tracking_order_id, status_data, status_id=None):
        status_mapping = {
            'agency_at': 1,
            'onway_at': 2,
            'arrived_at': 3,
            'delivered_at': 4
        }
            
        for key, timestamp in status_data.items():
            if not timestamp:
                continue

            mapped_status = status_mapping.get(key)
            if status_id and mapped_status <= status_id:
                continue

            g.db_session.add(TrackingOrderStatus(
                tracking_order_id=tracking_order_id,
                status_id=status_mapping.get(key),
                register_at=timestamp
            ))

        g.db_session.commit()
        return True, 200
    

    @handle_db_exceptions
    def get_open_tracking_orders(self):
        tracking_orders = (
            g.db_session.query(TrackingOrders)
            .filter(TrackingOrders.status_id != 4)
            .all()
        )

        return tracking_orders, 200

        
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


    @handle_db_exceptions
    def get_all_tracking_orders(self, page=1, per_page=20):
        query = (
            g.db_session.query(TrackingOrders)
            .order_by(TrackingOrders.id.desc())
        )

        total = query.count()
        data_list = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            "list": data_list,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page 
        }, 200
    

    @handle_db_exceptions
    def get_orders_like(self, order_number):
        search_term = f"%{order_number}%"

        subq = (
            g.db_session.query(
                TrackingOrders.id.label("tid"),
                db.func.max(ClientOrders.number).label("num"),
            )
            .join(ClientOrders, TrackingOrders.client_order_id == ClientOrders.id)
            .join(Clients, ClientOrders.client_id == Clients.id)
            .filter(
                db.or_(
                    db.cast(ClientOrders.number, db.String).ilike(search_term),
                    Clients.name.ilike(search_term),
                    Clients.document.ilike(search_term),
                )
            )
            .group_by(TrackingOrders.id)
            .subquery()
        )

        results = (
            g.db_session.query(TrackingOrders)
            .join(subq, TrackingOrders.id == subq.c.tid)
            .order_by(subq.c.num.desc())
            .all()
        )

        if not results:
            return None, 400

        return results, 200
    

    @handle_db_exceptions
    def get_total_orders(self):
        orders = (
            g.db_session.query(func.count(TrackingOrders.id))
            .scalar()
        )
        if not orders:
            return None, 200

        return orders, 200
    

    @handle_db_exceptions
    def get_today_total_orders(self):
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        today_total = (
            g.db_session.query(func.count(TrackingOrders.id))
            .filter(func.date(TrackingOrders.register_at) == today.date())
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
            g.db_session.query(func.count(TrackingOrders.id))
            .filter(TrackingOrders.register_at >= start_of_week)
            .scalar()
        )
        if not week_total:
            return None, 200

        return week_total, 200
    

    @handle_db_exceptions
    def get_month_total_orders(self):
        today = datetime.today()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        month_total = (
            g.db_session.query(func.count(TrackingOrders.id))
            .filter(TrackingOrders.register_at >= start_of_month)
            .scalar()
        )
        if not month_total:
            return None, 200

        return month_total, 200
    

    @handle_db_exceptions
    def get_orders_by_agency(self):
        orders_by_agency = (
            g.db_session.query(
                TrackingAgencies.id,
                TrackingAgencies.name,
                func.count(TrackingOrders.id).label("count")
            )
            .outerjoin(TrackingOrders, TrackingOrders.agency_id == TrackingAgencies.id)
            .filter(TrackingOrders.agency_id < 4)
            .group_by(TrackingAgencies.id, TrackingAgencies.name)
            .order_by(TrackingAgencies.id)
            .all()
        )
        if not orders_by_agency:
            return 'No se encontraron órdenes', 404

        return orders_by_agency, 200
    

    @handle_db_exceptions
    def get_orders_by_month(self):
        orders_by_month = (
            g.db_session.query(
                func.date_format(TrackingOrders.register_at, "%Y-%m").label('period'),
                func.count(TrackingOrders.id)
            )
            .group_by('period')
            .order_by('period')
            .all()
        )
        if not orders_by_month:
            return 'No se encontraron órdenes', 404

        return orders_by_month, 200
    

    @handle_db_exceptions
    def get_orders_by_department(self):
        department = func.trim(
            db.case(
                (func.locate(',', TrackingOrders.destination_agency) > 0,
                func.substring_index(TrackingOrders.destination_agency, ',', -1)),
                else_=TrackingOrders.destination_agency
            )
        )

        orders_by_department = (
            g.db_session.query(department.label('department'), func.count(TrackingOrders.id))
            .filter(TrackingOrders.destination_agency.isnot(None))
            .group_by('department')
            .order_by(func.count(TrackingOrders.id).desc())
            .limit(5)
            .all()
        )
        if not orders_by_department:
            return 'No se encontraron órdenes', 404

        return orders_by_department, 200