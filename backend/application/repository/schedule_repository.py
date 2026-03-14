import logging
from datetime import date, datetime, timezone, timedelta, timezone
from application.handlers import handle_db_exceptions
from application.models import Events, Visibility, Repeat, Notify, Colors, Holidays
from application.models import EventVisibilityUser, EventVisibilityDepartment
from application.models import Users, UserDepartment
from application.db_models.import_model import ImportAttachment
from sqlalchemy import or_, and_
from flask import g


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
    def replace_event_users(self, event_id, user_ids):
        g.db_session.query(EventVisibilityUser).filter(EventVisibilityUser.event_id == event_id).delete()
        rows = [EventVisibilityUser(event_id=event_id, user_id=int(uid)) for uid in (user_ids or [])]
        if rows:
            g.db_session.bulk_save_objects(rows)
        g.db_session.commit()
        return True, 200


    @handle_db_exceptions
    def replace_event_departments(self, event_id, dept_ids):
        g.db_session.query(EventVisibilityDepartment).filter(EventVisibilityDepartment.event_id == event_id).delete()
        rows = [EventVisibilityDepartment(event_id=event_id, department_id=int(did)) for did in (dept_ids or [])]
        if rows:
            g.db_session.bulk_save_objects(rows)
        g.db_session.commit()
        return True, 200


    @handle_db_exceptions
    def get_event_users_map(self, event_ids):
        if not event_ids:
            return {}, 200
        rows = (
            g.db_session.query(EventVisibilityUser.event_id, EventVisibilityUser.user_id)
            .filter(EventVisibilityUser.event_id.in_(event_ids))
            .all()
        )
        m = {}
        for eid, uid in rows:
            m.setdefault(int(eid), set()).add(int(uid))
        return m, 200


    @handle_db_exceptions
    def get_event_departments_map(self, event_ids):
        if not event_ids:
            return {}, 200
        rows = (
            g.db_session.query(EventVisibilityDepartment.event_id, EventVisibilityDepartment.department_id)
            .filter(EventVisibilityDepartment.event_id.in_(event_ids))
            .all()
        )
        m = {}
        for eid, did in rows:
            m.setdefault(int(eid), set()).add(int(did))
        return m, 200

    
    @handle_db_exceptions
    def get_user_ids_by_departments(self, dept_ids: list[int]):
        if not dept_ids:
            return [], 200
        ids = (
            g.db_session.query(Users.id)
            .filter(Users.department_id.in_([int(x) for x in dept_ids]))
            .all()
        )
        return [int(r[0]) for r in ids], 200

    @handle_db_exceptions
    def get_users_minimal(self):
        users = (
            g.db_session.query(Users.id, Users.name, Users.department_id)
            .filter(Users.level_id != 1)
            .filter(Users.level_id != 5)
            .filter(Users.id != 21)
            .order_by(Users.name.asc())
            .all()
        )
        return [{"id": int(u.id), "name": u.name or "", "department_id": u.department_id} for u in users], 200


    @handle_db_exceptions
    def get_departments(self):
        deps = g.db_session.query(UserDepartment.id, UserDepartment.name).order_by(UserDepartment.name.asc()).all()
        return [{"id": int(d.id), "name": d.name or ""} for d in deps], 200


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
        visibility = g.db_session.query(Visibility).order_by(Visibility.name.desc()).all()
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
    def get_all_day_events_for_date(self, day: date):
        start_day = datetime.combine(day, datetime.min.time())
        end_day = start_day + timedelta(days=1)

        events = (
            g.db_session.query(Events)
            .filter(
                Events.deleted_at.is_(None),
                (Events.all_day == True) | (Events.all_day == 1),
                Events.start_datetime >= start_day,
                Events.start_datetime < end_day,
            )
            .all()
        )
        return events or [], 200


    @handle_db_exceptions
    def add_event(self, data):
        raw_start = data.get("start_datetime")
        raw_end = data.get("end_datetime")
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)

        # normalizamos all_day a bool
        raw_all_day = data.get("all_day")
        all_day_flag = True if raw_all_day in (True, 1, "1", "true", "True") else False

        def parse_start(raw):
            if not raw:
                return None
            if all_day_flag:
                date_str = raw[:10]
                return datetime.strptime(date_str, "%Y-%m-%d")
            return datetime.fromisoformat(raw) if "T" in raw else datetime.strptime(raw, "%Y-%m-%d")

        def parse_end(raw, start_dt):
            if all_day_flag:
                if raw:
                    date_str = raw[:10]
                    d = datetime.strptime(date_str, "%Y-%m-%d")
                else:
                    d = start_dt
                return d.replace(hour=23, minute=59, second=59)
            else:
                if not raw:
                    return None
                return datetime.fromisoformat(raw) if "T" in raw else datetime.strptime(raw, "%Y-%m-%d")

        start_datetime = parse_start(raw_start)
        end_datetime = parse_end(raw_end, start_datetime) if start_datetime else None

        raw_visibility = data.get("visibility_id")
        try:
            visibility_id = int(raw_visibility) if raw_visibility not in (None, "") else 1
        except (TypeError, ValueError):
            visibility_id = 1

        event = Events(
            user_id       = data.get("user_id"),
            title         = data.get("title"),
            description   = data.get("description"),
            start_datetime = start_datetime,
            end_datetime   = end_datetime,
            meet          = data.get("meet"),
            import_shipment_id = data.get("import_shipment_id"),
            hex_color     = data.get("hex_color"),
            visibility_id = visibility_id,
            all_day       = all_day_flag,
            repeat_id     = data.get("repeat_id"),
            notify_id     = data.get("notify_id"),
            created_at    = peru_time,
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
    def get_import_attachments(self, import_shipment_id, target=None):
        query = (
            g.db_session.query(ImportAttachment)
            .filter(ImportAttachment.import_shipment_id == import_shipment_id)
        )

        if target:
            query = query.filter(ImportAttachment.target == target)

        rows = query.order_by(ImportAttachment.created_at.desc()).all()
        return rows or [], 200


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
        if raw_all_day is None:
            all_day_flag = bool(event.all_day)
        else:
            all_day_flag = True if raw_all_day in (True, 1, "1", "true", "True") else False

        def parse_start(raw):
            if not raw:
                return event.start_datetime
            if all_day_flag:
                date_str = raw[:10]
                return datetime.strptime(date_str, "%Y-%m-%d")  # 00:00:00
            return datetime.fromisoformat(raw) if "T" in raw else datetime.strptime(raw, "%Y-%m-%d")

        def parse_end(raw, start_dt):
            if all_day_flag:
                if raw:
                    date_str = raw[:10]
                    d = datetime.strptime(date_str, "%Y-%m-%d")
                else:
                    base = start_dt or event.start_datetime
                    d = base.date()
                    d = datetime.combine(d, datetime.min.time())
                return d.replace(hour=23, minute=59, second=59)
            else:
                if not raw:
                    return event.end_datetime
                return datetime.fromisoformat(raw) if "T" in raw else datetime.strptime(raw, "%Y-%m-%d")

        start_datetime = parse_start(raw_start)
        end_datetime   = parse_end(raw_end, start_datetime)

        raw_visibility = data.get("visibility_id")
        if raw_visibility not in (None, ""):
            try:
                visibility_id = int(raw_visibility)
            except (TypeError, ValueError):
                visibility_id = event.visibility_id
        else:
            visibility_id = event.visibility_id

        event.title          = data.get("title")
        event.description    = data.get("description")
        event.start_datetime = start_datetime
        event.end_datetime   = end_datetime
        event.meet           = data.get("meet")
        event.hex_color      = data.get("hex_color")
        event.visibility_id  = visibility_id
        event.all_day        = all_day_flag
        event.repeat_id      = data.get("repeat_id")
        event.notify_id      = data.get("notify_id")
        event.created_at     = peru_time  # idealmente aquí usarías updated_at

        g.db_session.add(event)
        g.db_session.commit()
        return True, 200
