import logging
from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_db_exceptions
from application.models import Events, Visibility, Repeat, Notify, Colors
from flask import g
from sqlalchemy import or_

class ScheduleRepository:
    def __init__(self):
        pass

        
    @handle_db_exceptions
    def get_events(self):
        visibility = g.db_session.query(Events).filter(Events.deleted_at.is_(None)).all()
        if not visibility:
            return [], 200

        return visibility, 200
    

    @handle_db_exceptions
    def get_visibility(self):
        visibility = g.db_session.query(Visibility).all()
        if not visibility:
            return [], 200

        return visibility, 200


    @handle_db_exceptions
    def get_repeat(self):
        repeat = g.db_session.query(Repeat).all()
        if not repeat:
            return [], 200

        return repeat, 200


    @handle_db_exceptions
    def get_notify(self):
        notify = g.db_session.query(Notify).all()
        if not notify:
            return [], 200

        return notify, 200
    

    @handle_db_exceptions
    def get_colors(self):
        colors = g.db_session.query(Colors).all()
        if not colors:
            return [], 200

        return colors, 200


    @handle_db_exceptions
    def add_event(self, data):
        raw_start = data.get("start_datetime")
        raw_end = data.get("end_datetime")
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)

        if raw_end:
            end_datetime = datetime.fromisoformat(raw_end) if "T" in raw_end else datetime.strptime(raw_end, "%Y-%m-%d")
        else:
            end_datetime = None

        event = Events(
            user_id = data.get("user_id"),
            title = data.get("title"),
            description = data.get("description"),
            start_datetime=datetime.fromisoformat(raw_start) if "T" in raw_start else datetime.strptime(raw_start, "%Y-%m-%d"),
            end_datetime=end_datetime,
            meet = data.get("meet"),
            hex_color = data.get("hex_color"),
            visibility = data.get("visibility", "all"), #
            all_day = data.get("all_day"),
            repeat_event = data.get("repeat"), #
            notify_event = data.get("notify"), #
            created_at = peru_time
        )

        g.db_session.add(event)
        g.db_session.commit()
        return True, 200
        

    @handle_db_exceptions
    def get_event_by_id(self, event_id):
        event = g.db_session.query(Events).filter(Events.id==event_id).first()
        if not event:
            return "Evento no encontrado", 404

        return event, 200


    @handle_db_exceptions
    def get_events_in_range(self, start_date, end_date):
        next_day = end_date + timedelta(days=1)

        events = (
            g.db_session.query(Events)
            .filter(
                Events.deleted_at.is_(None),
                Events.start_datetime < next_day,
                or_(
                    Events.start_datetime >= start_date,
                    Events.repeat_event != 'none'               
                )
            )
            .order_by(Events.start_datetime.asc())
            .all()
        )
        return events, 200

        
    @handle_db_exceptions
    def get_delete_event(self, event):
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)
        event.deleted_at = peru_time

        g.db_session.add(event)
        g.db_session.commit()
        return True, 200
    

    @handle_db_exceptions
    def update_event(self, event, data):
        raw_start = data.get("start_datetime")
        raw_end = data.get("end_datetime")
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)

        if raw_end:
            end_datetime = datetime.fromisoformat(raw_end) if "T" in raw_end else datetime.strptime(raw_end, "%Y-%m-%d")
        else:
            end_datetime = None
            
        event.title = data.get("title")
        event.description = data.get("description")
        event.start_datetime = datetime.fromisoformat(raw_start) if "T" in raw_start else datetime.strptime(raw_start, "%Y-%m-%d")
        event.end_datetime = end_datetime
        event.meet = data.get("meet")
        event.hex_color = data.get("hex_color")
        event.visibility = data.get("visibility")
        event.all_day = data.get("all_day")
        event.repeat_event = data.get("repeat")
        event.notify_event = data.get("notify")
        event.created_at = peru_time

        g.db_session.add(event)
        g.db_session.commit()
        return True, 200