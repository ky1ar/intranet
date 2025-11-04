import logging
from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_db_exceptions
from application.models import Events, Visibility, Repeat, Notify
from flask import g


class ScheduleRepository:
    def __init__(self):
        pass


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
            repeat_event = data.get("repeat_event"), #
            notify_event = data.get("notify_event"), #
            created_at = peru_time
        )

        g.db_session.add(event)
        g.db_session.commit()
        return True, 200
        
