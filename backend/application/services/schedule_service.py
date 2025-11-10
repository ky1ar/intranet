import logging
from datetime import datetime, timedelta, date
from calendar import monthrange
from application.handlers import handle_exceptions
from application.repository.schedule_repository import ScheduleRepository
from application.repository.user_repository import UserRepository
from application.services.general_service import GeneralService
from application import socketio
from flask_jwt_extended import get_jwt_identity


class ScheduleService:
    def __init__(self):
        self.schedule_repository = ScheduleRepository()
        self.user_repository = UserRepository()
        self.general_service = GeneralService()


    @handle_exceptions
    def get_month(self, offset):
        raw_viewer_id = get_jwt_identity()
        try:
            viewer_id = int(raw_viewer_id) if raw_viewer_id is not None else None
        except (TypeError, ValueError):
            viewer_id = None

        # ===================== USUARIO ACTUAL =====================
        viewer_dept_id = None
        if viewer_id:
            viewer, vc_user = self.user_repository.get_user_by_id(viewer_id)
            if vc_user == 200:
                viewer_dept_id = viewer.department_id

        now = datetime.now()
        offset = int(offset) if offset is not None else 0

        target_month = now.month + offset
        target_year = now.year

        while target_month > 12:
            target_month -= 12
            target_year += 1
        while target_month < 1:
            target_month += 12
            target_year -= 1

        first_day = datetime(target_year, target_month, 1)
        last_day_num = monthrange(target_year, target_month)[1]
        last_day = datetime(target_year, target_month, last_day_num)

        start_grid_date = first_day - timedelta(days=first_day.weekday())
        end_grid_date = last_day + timedelta(days=(6 - last_day.weekday()))

        events, vc = self.schedule_repository.get_events_in_range(start_grid_date, end_grid_date)
        if vc != 200:
            return events, vc

        # ===================== FILTRO POR VISIBILITY =====================
        filtered_events = []
        for ev in events:
            # El creador siempre ve sus eventos
            if ev.user_id == viewer_id:
                filtered_events.append(ev)
                continue

            vis = ev.visibility_id or 1

            if vis == 1:
                filtered_events.append(ev)
                continue

            if vis == 2:
                creator_dept_id = getattr(getattr(ev, "user", None), "department_id", None)
                if creator_dept_id and viewer_dept_id and creator_dept_id == viewer_dept_id:
                    filtered_events.append(ev)
                continue

            if vis == 3:
                continue

            filtered_events.append(ev)

        events = filtered_events
        # ===================== FIN FILTRO VISIBILITY =====================

        today_date = now.date()

        def format_time(dt: datetime) -> str:
            return dt.strftime("%I:%M %p")

        occurrences_by_day = {}

        def add_occurrence(date_obj: date, ev, occ_start: datetime | None, occ_end: datetime | None):
            date_key = date_obj.isoformat()
            all_day = True if ev.all_day or ev.all_day == 1 else False

            time_label = ""
            if occ_start:
                if occ_end:
                    time_label = f"{format_time(occ_start)} - {format_time(occ_end)}"
                else:
                    time_label = format_time(occ_start)

            occurrences_by_day.setdefault(date_key, []).append({
                "id": ev.id,
                "label": ev.title,
                "time": time_label,
                "hexColor": ev.hex_color,
                "allDay": all_day,
                "fullColor": bool(ev.hex_color and all_day),
                "creatorId": ev.user_id,
                "creatorImage": ev.user.image,
            })

        grid_start_date = start_grid_date.date()
        grid_end_date = end_grid_date.date()

        for ev in events:
            if not ev.start_datetime:
                continue

            start_dt = ev.start_datetime
            end_dt = ev.end_datetime
            base_date = start_dt.date()

            duration = end_dt - start_dt if end_dt else None
            rule = getattr(ev, "repeat_id")

            # ---- SIN REPETICIÓN ----
            if rule == 1:
                if grid_start_date <= base_date <= grid_end_date:
                    add_occurrence(base_date, ev, start_dt, end_dt)
                continue

            # ---- DIARIO ----
            if rule == 2:
                first_occ_date = max(base_date, grid_start_date)
                current_date = first_occ_date
                while current_date <= grid_end_date:
                    occ_start = datetime.combine(current_date, start_dt.time())
                    occ_end = occ_start + duration if duration else None
                    add_occurrence(current_date, ev, occ_start, occ_end)
                    current_date += timedelta(days=1)
                continue

            # ---- SEMANAL ----
            if rule == 3:
                first_week_date = grid_start_date
                days_diff = (base_date.weekday() - first_week_date.weekday()) % 7
                first_occ_date = first_week_date + timedelta(days=days_diff)
                if first_occ_date < base_date:
                    first_occ_date += timedelta(days=7)

                current_date = first_occ_date
                while current_date <= grid_end_date:
                    occ_start = datetime.combine(current_date, start_dt.time())
                    occ_end = occ_start + duration if duration else None
                    add_occurrence(current_date, ev, occ_start, occ_end)
                    current_date += timedelta(days=7)
                continue

            # ---- MENSUAL ----
            if rule == 4:
                event_day = base_date.day
                start_year, start_month = grid_start_date.year, grid_start_date.month
                end_year, end_month = grid_end_date.year, grid_end_date.month

                year = start_year
                month = start_month
                while (year < end_year) or (year == end_year and month <= end_month):
                    try:
                        candidate = date(year, month, event_day)
                    except ValueError:
                        candidate = None
                    if candidate and grid_start_date <= candidate <= grid_end_date and candidate >= base_date:
                        occ_start = datetime.combine(candidate, start_dt.time())
                        occ_end = occ_start + duration if duration else None
                        add_occurrence(candidate, ev, occ_start, occ_end)

                    if month == 12:
                        month = 1
                        year += 1
                    else:
                        month += 1
                continue

            # ---- ANUAL ----
            if rule == 5:
                event_day = base_date.day
                event_month = base_date.month
                for year in range(grid_start_date.year, grid_end_date.year + 1):
                    try:
                        candidate = date(year, event_month, event_day)
                    except ValueError:
                        candidate = None
                    if candidate and grid_start_date <= candidate <= grid_end_date and candidate >= base_date:
                        occ_start = datetime.combine(candidate, start_dt.time())
                        occ_end = occ_start + duration if duration else None
                        add_occurrence(candidate, ev, occ_start, occ_end)
                continue

            if grid_start_date <= base_date <= grid_end_date:
                add_occurrence(base_date, ev, start_dt, end_dt)

        days = []
        current = start_grid_date
        while current.date() <= end_grid_date.date():
            date_obj = current.date()
            date_key = date_obj.isoformat()

            day_events = occurrences_by_day.get(date_key, [])

            days.append({
                "date": date_key,
                "dayNumber": date_obj.day,
                "isCurrentMonth": (date_obj.month == target_month and date_obj.year == target_year),
                "isToday": (date_obj == today_date),
                "events": day_events,
            })

            current += timedelta(days=1)

        return days, 200


    @handle_exceptions
    def get_visibility(self):
        visibility, vc = self.schedule_repository.get_visibility()
        if vc != 200:
            return visibility, vc
        
        visibility_list = [
            {
                "id": option.id,
                "name": option.name,
                "slug": option.slug,

            } for option in visibility
        ]
        return visibility_list, 200
    
    
    @handle_exceptions
    def get_repeat(self):
        repeat, vc = self.schedule_repository.get_repeat()
        if vc != 200:
            return repeat, vc
        
        repeat_list = [
            {
                "id": option.id,
                "name": option.name,
                "slug": option.slug,

            } for option in repeat
        ]
        return repeat_list, 200


    @handle_exceptions
    def get_notify(self):
        notify, vc = self.schedule_repository.get_notify()
        if vc != 200:
            return notify, vc
        
        notify_list = [
            {
                "id": option.id,
                "name": option.name,
                "slug": option.slug,

            } for option in notify
        ]
        return notify_list, 200

        
    
    @handle_exceptions
    def get_colors(self):
        colors, vc = self.schedule_repository.get_colors()
        if vc != 200:
            return colors, vc
        
        colors_list = [
            {
                "id": option.id,
                "name": option.name,
                "hex": option.hex,

            } for option in colors
        ]
        return colors_list, 200


    @handle_exceptions
    def process(self, data):
        event_id = data.get("event_id")
        if not event_id:
            title = data.get("title", "").strip()
            if not title:
                return "Ingresa un título", 422

            raw_start = data.get("start_datetime")
            if not raw_start:
                return "Ingresa un fecha", 422
            
            add_event, aec = self.schedule_repository.add_event(data)
            if aec != 200:
                return add_event, aec
            
            socketio.emit("calendar_update_dashboard", {})
            return "Evento registrado correctamente", 200
        
        event, ec = self.schedule_repository.get_event_by_id(event_id)
        if ec != 200:
            return event, ec
        
        update_event, uec = self.schedule_repository.update_event(event, data)
        if uec != 200:
            return update_event, uec
        
        socketio.emit("calendar_update_dashboard", {})
        return "Evento actualizado correctamente", 200


    @handle_exceptions
    def delete(self, event_id):
        event, ec = self.schedule_repository.get_event_by_id(event_id)
        if ec != 200:
            return event, ec
        
        delete_event, dec = self.schedule_repository.get_delete_event(event)
        if dec != 200:
            return delete_event, dec
        
        socketio.emit("calendar_update_dashboard", {})
        return "Evento eliminado correctamente", 200


    @handle_exceptions
    def data(self, event_id):
        event, ec = self.schedule_repository.get_event_by_id(event_id)
        if ec != 200:
            return event, ec
        
        return {
            "id": event.id,
            "creator_id": event.user_id,
            "description": event.description,
            "start_datetime": event.start_datetime.isoformat(),
            "meet": event.meet,
            "hex_color": event.hex_color,
            "all_day": True if event.all_day or event.all_day == 1 else False,
            "end_datetime": event.end_datetime.isoformat() if event.end_datetime else None,
            "creator_name": self.general_service.format_name(event.user.name),
            "title": event.title,
            "repeat_id": event.repeat_id,
            "notify_id": event.notify_id,
            "visibility_id": event.visibility_id,
            "created_at": event.created_at.isoformat(),
        }, 200
