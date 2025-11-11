import logging
from datetime import date, datetime, timezone, timedelta, timezone
from application.handlers import handle_db_exceptions
from application.models import Events, Visibility, Repeat, Notify, Colors, Holidays
from flask import g
from sqlalchemy import or_

class ScheduleRepository:
    def __init__(self):
        pass

    
    @handle_db_exceptions
    def add_holiday(self, name, date_value, hex_color=None):
        holiday = Holidays(name=name, date=date_value, hex_color=hex_color)
        g.db_session.add(holiday)
        g.db_session.commit()
        return holiday, 200


    @handle_db_exceptions
    def delete_holiday(self, holiday):
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)
        holiday.deleted_at = peru_time

        g.db_session.add(holiday)
        g.db_session.commit()
        return True, 200
    
    
    @handle_db_exceptions
    def get_events_starting_between(self, start_dt, end_dt):
        events = (
            g.db_session.query(Events)
            .filter(
                Events.deleted_at.is_(None),
                Events.start_datetime >= start_dt,
                Events.start_datetime < end_dt,
            )
            .all()
        )
        return events or [], 200


    @handle_db_exceptions
    def get_holidays_in_range(self, start_date, end_date):
        start = start_date.date() if isinstance(start_date, datetime) else start_date
        end = end_date.date() if isinstance(end_date, datetime) else end_date

        holidays = (
            g.db_session.query(Holidays)
            .filter(
                Holidays.date >= start,
                Holidays.date <= end,
                Holidays.deleted_at.is_(None)
            )
            .order_by(Holidays.date.asc())
            .all()
        )
        return holidays, 200
    

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

        # normalizamos all_day a bool
        raw_all_day = data.get("all_day")
        all_day_flag = True if raw_all_day in (True, 1, "1", "true", "True") else False

        def parse_dt(raw):
            if not raw:
                return None
            # 👇 si es all_day, solo usamos la fecha a las 00:00
            if all_day_flag:
                date_str = raw[:10]
                return datetime.strptime(date_str, "%Y-%m-%d")
            # si no es all_day, respetamos fecha y hora
            return datetime.fromisoformat(raw) if "T" in raw else datetime.strptime(raw, "%Y-%m-%d")

        start_datetime = parse_dt(raw_start)
        end_datetime = parse_dt(raw_end)

        event = Events(
            user_id      = data.get("user_id"),
            title        = data.get("title"),
            description  = data.get("description"),
            start_datetime = start_datetime,
            end_datetime   = end_datetime,
            meet         = data.get("meet"),
            hex_color    = data.get("hex_color"),
            visibility_id = data.get("visibility_id"),
            all_day      = all_day_flag,
            repeat_id    = data.get("repeat_id"),
            notify_id    = data.get("notify_id"),
            created_at   = peru_time
        )

        g.db_session.add(event)
        g.db_session.commit()
        return event.id, 200
        

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
                    Events.repeat_id != 5               
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

        raw_all_day = data.get("all_day")
        all_day_flag = True if raw_all_day in (True, 1, "1", "true", "True") else False

        def parse_dt(raw):
            if not raw:
                return None
            if all_day_flag:
                date_str = raw[:10]
                return datetime.strptime(date_str, "%Y-%m-%d")
            return datetime.fromisoformat(raw) if "T" in raw else datetime.strptime(raw, "%Y-%m-%d")

        start_datetime = parse_dt(raw_start)
        end_datetime   = parse_dt(raw_end)

        event.title         = data.get("title")
        event.description   = data.get("description")
        event.start_datetime = start_datetime
        event.end_datetime   = end_datetime
        event.meet          = data.get("meet")
        event.hex_color     = data.get("hex_color")
        event.visibility_id = data.get("visibility_id")
        event.all_day       = all_day_flag
        event.repeat_id     = data.get("repeat_id")
        event.notify_id     = data.get("notify_id")
        event.created_at    = peru_time

        g.db_session.add(event)
        g.db_session.commit()
        return True, 200