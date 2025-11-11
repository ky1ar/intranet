import logging
from datetime import datetime, timedelta, date, timezone
from calendar import monthrange
from application.handlers import handle_exceptions
from application.repository.schedule_repository import ScheduleRepository
from application.repository.user_repository import UserRepository
from application.services.general_service import GeneralService
from application.services.push_service import PushSender 
from application import socketio
from flask_jwt_extended import get_jwt_identity


class ScheduleService:
    def __init__(self):
        self.schedule_repository = ScheduleRepository()
        self.user_repository = UserRepository()
        self.general_service = GeneralService()
        self.push_sender = PushSender()


    def _get_recipients_for_event(self, event, for_reminder=False):
        """
        visibility_id:
        1 = TODOS
        2 = ÁREA (department)
        3 = PRIVADO
        """
        visibility = event.visibility_id or 1
        creator_id = event.user_id

        # EVENTO PARA TODOS
        if visibility == 1:
            users, uc = self.user_repository.get_all_users()
            if uc != 200:
                logging.warning(f"[SCHEDULE] Error obteniendo usuarios: {users}")
                return []
            return [u.id for u in users]

        # EVENTO PARA ÁREA DEL CREADOR
        if visibility == 2:
            creator, cc = self.user_repository.get_user_by_id(creator_id)
            if cc != 200 or not getattr(creator, "department_id", None):
                logging.warning(f"[SCHEDULE] Creador sin departamento o no encontrado (id={creator_id})")
                return []
            users, uc = self.user_repository.get_users_by_department(creator.department_id)
            if uc != 200:
                logging.warning(f"[SCHEDULE] Error obteniendo usuarios por área: {users}")
                return []
            return [u.id for u in users]

        # PRIVADO:
        #  - creación / actualización / eliminación: no se notifica (for_reminder=False)
        #  - recordatorio: solo al creador
        if visibility == 3:
            return [creator_id] if for_reminder else []

        return []
    

    def _notify_event_change(self, event_id: int, action: str, old_visibility_id: int | None = None):
        # 👇 recargamos el evento con una sesión "limpia"
        event, ec = self.schedule_repository.get_event_by_id(event_id)
        if ec != 200:
            logging.warning(f"[SCHEDULE] No se pudo cargar evento {event_id} para notificación: {event}")
            return

        visibility = event.visibility_id or 1
        old_visibility = old_visibility_id or visibility

        # Reglas de visibilidad como las que ya tenías:
        if action in ("created", "deleted"):
            if visibility == 3:
                return

        if action == "updated":
            if old_visibility == 3 and visibility == 3:
                return
            if visibility == 3:
                return

        creator = getattr(event, "user", None)
        creator_name = self.general_service.format_name(creator.name) if creator and creator.name else "Alguien"

        if action == "created":
            title = "Nuevo evento"
            if visibility == 1:
                body = f"{creator_name} creó un evento para todos: \"{event.title}\""
            elif visibility == 2:
                body = f"{creator_name} creó un evento para tu área: \"{event.title}\""
            else:
                body = f"{creator_name} creó un evento: \"{event.title}\""
        elif action == "updated":
            title = "Evento actualizado"
            body = f"{creator_name} actualizó el evento \"{event.title}\""
        elif action == "deleted":
            title = "Evento eliminado"
            body = f"{creator_name} eliminó el evento \"{event.title}\""
        elif action == "reminder":
            if event.all_day or event.all_day == 1:
                title = "Evento de hoy"
                body = f"Hoy tienes \"{event.title}\"."
            else:
                title = "Evento en curso"
                body = f"\"{event.title}\" está comenzando ahora."
        else:
            return

        recipients = self._get_recipients_for_event(event, for_reminder=(action == "reminder"))
        if not recipients:
            return

        payload = {
            "type": "SCHEDULE_EVENT",
            "action": action,
            "event_id": str(event.id),
            "visibility_id": str(visibility),
            "start_datetime": event.start_datetime.isoformat() if event.start_datetime else None,
        }

        for user_id in set(recipients):
            self.push_sender.send_to_user(user_id, title, body, data=payload)

            

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

        utc_now = datetime.now(timezone.utc)
        now = utc_now - timedelta(hours=5)
        
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
                "type": "EVENT",
                "clickable": True, 
            })

        grid_start_date = start_grid_date.date()
        grid_end_date = end_grid_date.date()

        holidays, hc = self.schedule_repository.get_holidays_in_range(start_grid_date, end_grid_date)
        if hc != 200:
            return holidays, hc

        holidays_by_date = {}
        for h in holidays:
            key = h.date.isoformat()
            holidays_by_date.setdefault(key, []).append(h)

        users_with_birthday, ubc = self.user_repository.get_users_with_birthday()
        if ubc != 200:
            return users_with_birthday, ubc

        birthdays_by_mmdd = {}
        for u in users_with_birthday:
            if not getattr(u, "birthday", None):
                continue
            mmdd = u.birthday.strftime("%m-%d")
            birthdays_by_mmdd.setdefault(mmdd, []).append(u)


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

            # Eventos normales
            normal_events = list(occurrences_by_day.get(date_key, []))

            # ---- FERIADOS (pueden seguir siendo clickeables si quieres) ----
            holiday_events = []
            holiday_list = holidays_by_date.get(date_key, [])
            for h in holiday_list:
                holiday_events.append({
                    "id": f"holiday-{h.id}",
                    "label": h.name,
                    "time": "",
                    "hexColor": None,
                    "allDay": True,
                    "fullColor": False,
                    "creatorId": None,
                    "creatorImage": None,
                    "type": "BIRTHDAY",
                    "clickable": False,   # si no quieres que abran modal, pon False
                })

            # ---- CUMPLEAÑOS (van ARRIBA, no clickeables) ----
            birthday_events = []
            mmdd = date_obj.strftime("%m-%d")
            birthday_users = birthdays_by_mmdd.get(mmdd, [])
            for u in birthday_users:
                birthday_events.append({
                    "id": f"birthday-{u.id}",
                    "label": f"🎂 {self.general_service.format_name(u.name)}",
                    "time": "",
                    "hexColor": None,       # o un color fijo desde front
                    "allDay": True,
                    "fullColor": False,
                    "creatorId": u.id,
                    "creatorImage": u.image,
                    "type": "BIRTHDAY",
                    "clickable": False,     # 👈 no clickeable
                })

            # Orden final: cumpleaños → feriados → eventos normales
            day_events = birthday_events + holiday_events + normal_events

            holiday_names = [h.name for h in holiday_list]

            days.append({
                "date": date_key,
                "dayNumber": date_obj.day,
                "isCurrentMonth": (date_obj.month == target_month and date_obj.year == target_year),
                "isToday": (date_obj == today_date),

                # Para que puedas poner el día completo en gris/centrado
                "isHoliday": bool(holiday_names),      # fondo gris del día
                "holidayNames": holiday_names,         # por si quieres mostrar el nombre en el header del día

                "hasBirthdays": bool(birthday_users),  # iconito 🎂 en el día
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

        # ============ CREAR ============
        if not event_id:
            title = data.get("title", "").strip()
            if not title:
                return "Ingresa un título", 422

            raw_start = data.get("start_datetime")
            if not raw_start:
                return "Ingresa un fecha", 422
            
            new_event_id, aec = self.schedule_repository.add_event(data)
            if aec != 200:
                return new_event_id, aec
            
            socketio.emit("calendar_update_dashboard", {})

            self._notify_event_change(new_event_id, "created")

            return "Evento registrado correctamente", 200
        
        # ============ EDITAR ============
        event, ec = self.schedule_repository.get_event_by_id(event_id)
        if ec != 200:
            return event, ec

        old_visibility_id = event.visibility_id

        updated, uec = self.schedule_repository.update_event(event, data)
        if uec != 200:
            return updated, uec
        
        socketio.emit("calendar_update_dashboard", {})

        # 🔔 notificación por actualización usando el ID
        self._notify_event_change(event_id, "updated", old_visibility_id=old_visibility_id)

        return "Evento actualizado correctamente", 200



    @handle_exceptions
    def delete(self, event_id):
        event, ec = self.schedule_repository.get_event_by_id(event_id)
        if ec != 200:
            return event, ec
        
        # 🔔 notificar ANTES de marcar como borrado
        self._notify_event_change(event_id, "deleted")
        
        delete_event, dec = self.schedule_repository.get_delete_event(event)
        if dec != 200:
            return delete_event, dec
        
        socketio.emit("calendar_update_dashboard", {})
        return "Evento eliminado correctamente", 200


    @handle_exceptions
    def notify_upcoming_events(self):
        utc_now = datetime.now(timezone.utc)
        now = utc_now - timedelta(hours=5)

        window_start = now
        window_end = now + timedelta(minutes=1)

        logging.info(window_start)
        logging.info(window_end)

        events, ec = self.schedule_repository.get_events_starting_between(window_start, window_end)
        if ec != 200:
            return events, ec

        for ev in events:
            logging.info(ev.title)
            self._notify_event_change(ev.id, "reminder")

        return {"ok": True, "count": len(events)}, 200
        # crontab -e
        # * * * * * curl -s -X POST "https://devapi.krear3d.com/schedule/notifications/upcoming" > /dev/null 2>&1

    

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
