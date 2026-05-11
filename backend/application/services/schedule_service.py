import logging
from datetime import datetime, timedelta, date, timezone
from calendar import monthrange
from application.handlers import handle_exceptions
from application.utils import format_name, format_date
from application.services.module_service import ModuleService
from application.repository.schedule_repository import ScheduleRepository
from application.repository.user_repository import UserRepository
from application.repository.import_repository import ImportRepository
from application.services.general_service import GeneralService
from application.services.push_service import PushSender 
from application import socketio, redis_client
from flask_jwt_extended import get_jwt_identity


ROOM_BOOKING_COLOR = '#37474F'
ROOM_BOOKING_TITLE = 'Sala de Reuniones'


class ScheduleService:
    def __init__(self):
        self.module_service = ModuleService()
        self.schedule_repository = ScheduleRepository()
        self.user_repository = UserRepository()
        self.import_repository = ImportRepository()
        self.general_service = GeneralService()
        self.push_sender = PushSender()


    def _has_perm(self, user_id, perm_slug):
        result, code = self.module_service.check_permission(user_id, 'schedule', perm_slug)
        if code != 200:
            return False
        return result.get('granted', False) if isinstance(result, dict) else False


    def _get_visible_department_ids(self, user_id):
        """Retorna set de department_ids que el usuario puede ver en la agenda"""
        if self._has_perm(user_id, 'view_all'):
            return None  # None = ve todo

        modules_data, _ = self.module_service.get_user_modules(user_id)
        dept_slugs = []
        if isinstance(modules_data, list):
            for m in modules_data:
                if m['slug'] == 'schedule':
                    for perm_slug, granted in m.get('permissions', {}).items():
                        if granted and perm_slug.startswith('view_'):
                            dept_slugs.append(perm_slug.replace('view_', ''))
                    break

        if not dept_slugs:
            return set()  # vacío = solo ve su departamento

        # Convertir slugs a department_ids
        dept_ids, rc = self.user_repository.get_department_ids_by_slugs(dept_slugs)
        if rc == 200:
            return set(dept_ids)
        return set()


    def _audience_for_visibility(self, visibility_id, creator_id, creator_dept_id):
        """
        visibility_id:
          1 = TODOS
          2 = ÁREA (del creador)
          3 = PRIVADO (nadie)
        Excluye siempre al creador.
        """
        try:
            vis = int(visibility_id) if visibility_id is not None else 1
        except (TypeError, ValueError):
            vis = 1

        try:
            if vis == 1:
                ids, _ = self.user_repository.get_all_user_ids()
                audience = set(ids)
            elif vis == 2 and creator_dept_id:
                ids, _ = self.user_repository.get_user_ids_by_department(creator_dept_id)
                audience = set(ids)
            else:
                audience = set()
            audience.discard(creator_id)
            return audience
        except Exception:
            return set()
    

    def _audience_for_event(self, event, user_ids_specific=None, dept_ids_specific=None):
        """
        Devuelve set de user_ids que deben ser notificados (EXCLUYE al creador).
        visibility_id:
        1 TODOS
        2 ÁREA (del creador)
        3 PRIVADO
        4 USUARIOS ESPECÍFICOS
        5 ÁREAS ESPECÍFICAS
        """
        creator_id = int(event.user_id)
        vis = int(event.visibility_id or 1)

        audience: set[int] = set()

        if vis == 1:
            ids, _ = self.user_repository.get_all_user_ids()
            audience = set(ids)

        elif vis == 2:
            creator_dept, _ = self.user_repository.get_user_department_id(creator_id)
            if creator_dept:
                ids, _ = self.user_repository.get_user_ids_by_department(creator_dept)
                audience = set(ids)

        elif vis == 4:
            audience = set(int(x) for x in (user_ids_specific or []))

        elif vis == 5:
            dept_ids = [int(x) for x in (dept_ids_specific or [])]
            ids, _ = self.schedule_repository.get_user_ids_by_departments(dept_ids)
            audience = set(ids)

        # 3 o default => vacío
        audience.discard(creator_id)
        return audience

    def _build_event_payload(self, event, action):
        data = {
            "type": "SCHEDULE_EVENT",
            "action": action,              # created | updated | removed | reminder
            "event_id": str(event.id),
            "visibility_id": str(event.visibility_id or 1),
            "all_day": bool(event.all_day),
            "title": event.title or "",
        }
        if event.all_day:
            if event.start_datetime:
                data["start_date"] = event.start_datetime.date().isoformat()
        else:
            if event.start_datetime:
                data["start_datetime"] = event.start_datetime.isoformat()
            if event.end_datetime:
                data["end_datetime"] = event.end_datetime.isoformat()
        return data
    

    def _format_title_body(self, event, action: str) -> tuple[str, str]:
        titulo = (event.title or "").strip()

        creator = getattr(event, "user", None)
        actor_name = "Alguien"

        if creator and getattr(creator, "name", None):
            full_name = format_name(creator.name)
            actor_name = full_name.split(" ", 1)[0] or "Alguien"

        if action == "created":
            return (
                "Nuevo evento en tu agenda ✨",
                f"{actor_name} creó el evento: {titulo}."
            )

        if action == "updated":
            if event.import_shipment_id:
                new_date = format_date(event.start_datetime) if event.start_datetime else "-"
                return (
                    "Nueva fecha de arribo 🛳️",
                    f"{actor_name} actualizó la llegada de: {titulo}. Nueva fecha: {new_date}."
                )
            return (
                "Actualización de evento ✏️",
                f"{actor_name} actualizó el evento: {titulo}."
            )

        if action == "removed":
            return (
                "Evento eliminado 🗑️",
                f"{actor_name} eliminó el evento: {titulo}."
            )

        if action == "reminder":
            if event.all_day:
                return (
                    "Evento de hoy 📅",
                    f"Hoy tienes: {titulo}, en tu agenda."
                )
            return (
                "Un evento está por empezar ⏰",
                f"{titulo}, está a punto de comenzar."
            )

        return (
            "Notificación de tu agenda",
            f"«{titulo}»"
        )


    def _notify_bulk(self, user_ids: set[int], event, action: str):
        if not user_ids:
            return
        title, body = self._format_title_body(event, action)
        payload = self._build_event_payload(event, action)
        for uid in user_ids:
            self.push_sender.send_to_user(uid, title, body, payload)


    def _notify_reminder(self, event):
        """
        Recordatorios respetando visibilidad:
        - TODOS / ÁREA: todos los que ven el evento + el creador
        - PRIVADO: solo el creador
        """
        creator_id = event.user_id
        creator_dept, _ = self.user_repository.get_user_department_id(creator_id)
        visibility_id = event.visibility_id or 1

        if visibility_id == 3:
            # privado → solo creador
            audience = {creator_id}
        else:
            # misma lógica que el resto, pero sumando creador
            audience = self._audience_for_visibility(visibility_id, creator_id, creator_dept)
            audience.add(creator_id)

        self._notify_bulk(audience, event, "reminder")


    @handle_exceptions
    def get_month(self, offset):
        viewer_id = get_jwt_identity()
        if not viewer_id:
            return "Unauthorized", 422
        
        viewer_id = int(viewer_id)
        viewer, vc = self.user_repository.get_user_by_id(viewer_id)
        if vc != 200:
            return "User department not found", 422
        
        viewer_dept_id = viewer.department_id
        viewer_level_id = viewer.level_id
        visible_depts = self._get_visible_department_ids(viewer_id)
        
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

        events, ec = self.schedule_repository.get_events_in_range(start_grid_date, end_grid_date)
        if ec != 200:
            return events, ec

        event_ids = [int(e.id) for e in events]
        users_map, _ = self.schedule_repository.get_event_users_map(event_ids)
        depts_map, _ = self.schedule_repository.get_event_departments_map(event_ids)

        filtered_events = []
        for ev in events:
            # El creador siempre ve sus eventos
            if ev.user_id == viewer_id:
                filtered_events.append(ev)
                continue

            vis = int(ev.visibility_id or 1)

            if vis == 1:
                filtered_events.append(ev)
                continue

            if vis == 2:
                creator_dept_id = ev.user.department_id

                # Siempre ve eventos de su propio departamento
                if creator_dept_id == viewer_dept_id:
                    filtered_events.append(ev)
                    continue

                # Si tiene view_all, ve todo tipo "área"
                if visible_depts is None:
                    filtered_events.append(ev)
                    continue

                # Si tiene view_* específicos, verificar
                if creator_dept_id in visible_depts:
                    filtered_events.append(ev)
                continue

            if vis == 3:
                continue
            
            if vis == 4:
                allowed_users = users_map.get(int(ev.id), set())
                if viewer_id in allowed_users:
                    filtered_events.append(ev)
                continue

            if vis == 5:
                allowed_depts = depts_map.get(int(ev.id), set())
                if viewer_dept_id in allowed_depts:
                    filtered_events.append(ev)
                continue

            filtered_events.append(ev)

        events = filtered_events
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

            is_room = bool(getattr(ev, "is_room_booking", 0))
            if is_room and ev.user and ev.user.name:
                first_name = format_name(ev.user.name).split()[0]
                event_label = f"Sala de reuniones | {first_name}"
            else:
                event_label = ev.title

            room_start_hhmm = occ_start.strftime("%H:%M") if (is_room and occ_start and not all_day) else None
            room_end_hhmm   = occ_end.strftime("%H:%M")   if (is_room and occ_end   and not all_day) else None

            occurrences_by_day.setdefault(date_key, []).append({
                "id": ev.id,
                "label": event_label,
                "time": time_label,
                "hexColor": ev.hex_color,
                "allDay": all_day,
                "fullColor": is_room or bool(ev.hex_color and all_day),
                "creatorId": ev.user_id,
                "creatorImage": ev.user.image,
                "type": "EVENT",
                "clickable": True,
                "isRoomBooking": is_room,
                "roomStart": room_start_hhmm,
                "roomEnd": room_end_hhmm,
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
                    "clickable": False,
                })

            birthday_events = []
            mmdd = date_obj.strftime("%m-%d")
            birthday_users = birthdays_by_mmdd.get(mmdd, [])
            for u in birthday_users:
                birthday_events.append({
                    "id": f"birthday-{u.id}",
                    "label": f"🎂 {format_name(u.name)}",
                    "time": "",
                    "hexColor": None,
                    "allDay": True,
                    "fullColor": False,
                    "creatorId": u.id,
                    "creatorImage": u.image,
                    "type": "BIRTHDAY",
                    "clickable": False,
                })

            day_events = birthday_events + holiday_events + normal_events
            holiday_names = [h.name for h in holiday_list]

            days.append({
                "date": date_key,
                "dayNumber": date_obj.day,
                "dayName": self.get_day_name_es_3(date_obj),
                "isCurrentMonth": (date_obj.month == target_month and date_obj.year == target_year),
                "isToday": (date_obj == today_date),

                "isHoliday": bool(holiday_names),
                "holidayNames": holiday_names,

                "hasBirthdays": bool(birthday_users),
                "events": day_events,
            })

            current += timedelta(days=1)

        return days, 200


    def get_day_name_es_3(self, date_obj):
        names = ["lun", "mar", "mie", "jue", "vie", "sab", "dom"]
        return names[date_obj.weekday()]


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


    def _serialize_import_attachment(self, attachment):
        ext = ""
        if attachment.original_name and "." in attachment.original_name:
            ext = attachment.original_name.rsplit(".", 1)[-1].lower()

        return {
            "id": attachment.id,
            "target": attachment.target,
            "original_name": attachment.original_name,
            "ext": ext,
            "mime_type": attachment.mime_type,
            "size_bytes": attachment.size_bytes,
            # ajusta estas rutas si tu módulo de imports usa otras
            "inline_url": f"/imports/attachment/{attachment.id}?disposition=inline",
            "download_url": f"/imports/attachment/{attachment.id}?disposition=attachment",
            "preview_url": f"/imports/attachment/{attachment.id}/preview",
        }

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
                return "Ingresa una fecha", 422
            
            new_event_id, aec = self.schedule_repository.add_event(data)
            if aec != 200:
                return new_event_id, aec
            
            vis = int(data.get("visibility_id") or 1)
            if vis == 4:
                user_ids = data.get("audience_user_ids") or []
                if not user_ids:
                    return "Selecciona al menos un usuario", 422
                self.schedule_repository.replace_event_users(new_event_id, user_ids)

            elif vis == 5:
                dept_ids = data.get("audience_department_ids") or []
                if not dept_ids:
                    return "Selecciona al menos un área", 422
                self.schedule_repository.replace_event_departments(new_event_id, dept_ids)
                
            socketio.emit("calendar_update_dashboard", {})

            event, ec = self.schedule_repository.get_event_by_id(new_event_id)
            if ec == 200:
                u_map, _ = self.schedule_repository.get_event_users_map([event.id])
                d_map, _ = self.schedule_repository.get_event_departments_map([event.id])

                audience = self._audience_for_event(
                    event,
                    user_ids_specific=list(u_map.get(event.id, [])),
                    dept_ids_specific=list(d_map.get(event.id, [])),
                )
                self._notify_bulk(audience, event, "created")
                
            return "Evento registrado correctamente", 200
        
        # ============ EDITAR ============
        event, ec = self.schedule_repository.get_event_by_id(event_id)
        if ec != 200:
            return event, ec

        eid = int(event_id)  # 👈 GUARDA SIEMPRE COMO PRIMITIVO

        old_vis = int(event.visibility_id or 1)
        creator_id = int(event.user_id)

        old_u_map, _ = self.schedule_repository.get_event_users_map([eid])
        old_d_map, _ = self.schedule_repository.get_event_departments_map([eid])

        old_audience = self._audience_for_event(
            event,
            user_ids_specific=list(old_u_map.get(eid, [])),
            dept_ids_specific=list(old_d_map.get(eid, [])),
        )

        # parse new_vis
        raw_new_vis = data.get("visibility_id")
        try:
            new_vis = int(raw_new_vis) if raw_new_vis not in (None, "") else old_vis
        except (TypeError, ValueError):
            new_vis = old_vis
        data["visibility_id"] = new_vis

        new_user_ids = data.get("audience_user_ids") or []
        new_dept_ids = data.get("audience_department_ids") or []

        if new_vis == 4 and not new_user_ids:
            return "Selecciona al menos un usuario", 422
        if new_vis == 5 and not new_dept_ids:
            return "Selecciona al menos un área", 422

        updated, uec = self.schedule_repository.update_event(event, data)
        if uec != 200:
            return updated, uec

        # 👇 IMPORTANTÍSIMO: NO usar event.id aquí (ya puede estar detached)
        if new_vis == 4:
            self.schedule_repository.replace_event_users(eid, new_user_ids)
            self.schedule_repository.replace_event_departments(eid, [])
        elif new_vis == 5:
            self.schedule_repository.replace_event_departments(eid, new_dept_ids)
            self.schedule_repository.replace_event_users(eid, [])
        else:
            self.schedule_repository.replace_event_users(eid, [])
            self.schedule_repository.replace_event_departments(eid, [])

        # re-fetch (acá ya trabajas con uno nuevo)
        event, ec = self.schedule_repository.get_event_by_id(eid)
        if ec != 200:
            return event, ec

        new_u_map, _ = self.schedule_repository.get_event_users_map([eid])
        new_d_map, _ = self.schedule_repository.get_event_departments_map([eid])

        new_audience = self._audience_for_event(
            event,
            user_ids_specific=list(new_u_map.get(eid, [])),
            dept_ids_specific=list(new_d_map.get(eid, [])),
        )

        added   = new_audience - old_audience
        removed = old_audience - new_audience
        stayed  = new_audience & old_audience

        self._notify_bulk(added, event, "created")
        self._notify_bulk(removed, event, "removed")
        self._notify_bulk(stayed, event, "updated")

        socketio.emit("calendar_update_dashboard", {})

        if event.import_shipment_id and event.start_datetime:
            new_eta = event.start_datetime.date()
            self.import_repository.update_eta(event.import_shipment_id, new_eta)
            socketio.emit("imports_dashboard_update", {})

        return "Evento actualizado correctamente", 200


    @handle_exceptions
    def delete(self, event_id):
        event, ec = self.schedule_repository.get_event_by_id(event_id)
        if ec != 200:
            return event, ec
        
        creator_id = event.user_id
        creator_dept, _ = self.user_repository.get_user_department_id(creator_id)
        audience = self._audience_for_visibility(event.visibility_id or 1, creator_id, creator_dept)

        delete_event, dec = self.schedule_repository.get_delete_event(event)
        if dec != 200:
            return delete_event, dec

        event, ec = self.schedule_repository.get_event_by_id(event_id)
        if ec != 200:
            return event, ec
        
        self._notify_bulk(audience, event, "removed")

        socketio.emit("calendar_update_dashboard", {})
        return "Evento eliminado correctamente", 200


    @handle_exceptions
    def notify_upcoming_events(self):
        utc_now = datetime.now(timezone.utc)
        now = utc_now - timedelta(hours=5)

        window_start = now.replace(second=0, microsecond=0)
        window_end = window_start + timedelta(minutes=1)

        logging.info(f"[REMINDERS] {window_start.isoformat()} -> {window_end.isoformat()}")

        sent = 0

        # 1) Timed events (no all_day) que empiezan en este minuto
        events, ec = self.schedule_repository.get_events_starting_between(window_start, window_end)
        if ec != 200:
            return events, ec

        for ev in events:
            # Seguridad: ignorar all_day aquí
            if bool(ev.all_day):
                continue

            # Dedupe por minuto: reminder:{event_id}:{YYYYMMDDHHMM}
            stamp = window_start.strftime("%Y%m%d%H%M")
            key = f"reminder:{ev.id}:{stamp}"
            if redis_client.setnx(key, "1"):
                redis_client.expire(key, 120)  # 2 min de margen
                self._notify_reminder(ev)
                sent += 1

        # 2) All-day: sólo a las 00:00 (Lima) del día
        if window_start.hour == 0 and window_start.minute == 0:
            today = window_start.date()
            all_day_events, ec2 = self.schedule_repository.get_all_day_events_for_date(today)
            if ec2 != 200:
                return all_day_events, ec2

            for ev in all_day_events:
                # Dedupe por día: reminder:allday:{event_id}:{YYYYMMDD}
                dkey = f"reminder:allday:{ev.id}:{today.strftime('%Y%m%d')}"
                if redis_client.setnx(dkey, "1"):
                    redis_client.expire(dkey, 26 * 3600)
                    self._notify_reminder(ev)
                    sent += 1

        return {"ok": True, "count": sent}, 200
        # crontab -e
        # * * * * * curl -s -X POST "https://devapi.krear3d.com/schedule/notifications/upcoming" > /dev/null 2>&1

    

    @handle_exceptions
    def data(self, event_id):
        event, ec = self.schedule_repository.get_event_by_id(event_id)
        if ec != 200:
            return event, ec
        
        u_map, _ = self.schedule_repository.get_event_users_map([event.id])
        d_map, _ = self.schedule_repository.get_event_departments_map([event.id])

        is_import = event.import_shipment is not None
        import_data = None

        if is_import:
            shipment = event.import_shipment

            product_list_files, _ = self.schedule_repository.get_import_attachments(
                shipment.id,
                target="product_list"
            )

            import_data = {
                "id": shipment.id,
                "port_name": shipment.port.name.title() if shipment.port else None,
                "custom_port_name": shipment.custom_port_name,
                "tracking_link": shipment.tracking_link,
                "etd_date": shipment.etd_date.isoformat() if shipment.etd_date else None,
                "eta_date": shipment.eta_date.isoformat() if shipment.eta_date else None,
                "product_list_files": [
                    self._serialize_import_attachment(f) for f in product_list_files
                ],
            }

        return {
            "id": event.id,
            "creator_id": event.user_id,
            "description": event.description,
            "start_datetime": event.start_datetime.isoformat(),
            "meet": event.meet,
            "hex_color": event.hex_color,
            "all_day": True if event.all_day or event.all_day == 1 else False,
            "end_datetime": event.end_datetime.isoformat() if event.end_datetime else None,
            "creator_name": format_name(event.user.name),
            "title": event.title,
            "repeat_id": event.repeat_id,
            "notify_id": event.notify_id,
            "visibility_id": event.visibility_id,
            "audience_user_ids": sorted(list(u_map.get(event.id, set()))),
            "audience_department_ids": sorted(list(d_map.get(event.id, set()))),
            "created_at": event.created_at.isoformat(),
            "is_import": is_import,
            "import_shipment": import_data,
            "is_room_booking": bool(getattr(event, "is_room_booking", 0)),
        }, 200


    @handle_exceptions
    def room_booking_process(self, data):
        user_id = int(get_jwt_identity())
        booking_id = data.get("booking_id")
        date_str = (data.get("date") or "").strip()
        start_time_str = (data.get("start_time") or "").strip()
        end_time_str = (data.get("end_time") or "").strip()
        description = (data.get("description") or "").strip()

        if not date_str:
            return "Selecciona una fecha", 400
        if not start_time_str or not end_time_str:
            return "Selecciona hora de inicio y fin", 400

        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_dt = datetime.strptime(f"{date_str}T{start_time_str}", "%Y-%m-%dT%H:%M")
            end_dt = datetime.strptime(f"{date_str}T{end_time_str}", "%Y-%m-%dT%H:%M")
        except ValueError:
            return "Formato de fecha u hora inválido", 400

        if start_dt.hour < 9 or end_dt.hour > 18 or (end_dt.hour == 18 and end_dt.minute > 0):
            return "El horario debe estar entre 9:00 a.m. y 6:00 p.m.", 400

        if end_dt <= start_dt:
            return "La hora de fin debe ser mayor a la de inicio", 400

        existing, _ = self.schedule_repository.get_room_bookings_for_date(
            target_date, exclude_id=booking_id
        )
        for ev in existing:
            ev_start = ev.start_datetime
            ev_end = ev.end_datetime or ev.start_datetime
            if start_dt < ev_end and end_dt > ev_start:
                owner = format_name(ev.user.name).split()[0] if ev.user and ev.user.name else "alguien"
                return f"Horario ocupado: {owner} tiene la sala de {ev_start.strftime('%H:%M')} a {ev_end.strftime('%H:%M')}", 409

        if booking_id:
            event, ec = self.schedule_repository.get_event_by_id(booking_id)
            if ec != 200:
                return event, ec
            if not getattr(event, "is_room_booking", 0):
                return "No autorizado", 403
            if event.user_id != user_id:
                return "Solo el creador puede editar la reserva", 403
            ok, rc = self.schedule_repository.update_room_booking(event, start_dt, end_dt, description)
            if rc != 200:
                return ok, rc
        else:
            event_data = {
                "user_id": user_id,
                "title": ROOM_BOOKING_TITLE,
                "description": description,
                "start_datetime": start_dt.isoformat(),
                "end_datetime": end_dt.isoformat(),
                "hex_color": ROOM_BOOKING_COLOR,
                "visibility_id": 1,
                "all_day": False,
                "repeat_id": 1,
                "notify_id": 1,
                "is_room_booking": 1,
            }
            _, ec = self.schedule_repository.add_event(event_data)
            if ec != 200:
                return _, ec

        socketio.emit("calendar_update_dashboard", {})
        return "Reserva guardada correctamente", 200


    @handle_exceptions
    def room_booking_delete(self, booking_id, user_id):
        event, ec = self.schedule_repository.get_event_by_id(booking_id)
        if ec != 200:
            return event, ec
        if not getattr(event, "is_room_booking", 0):
            return "No es una reserva de sala", 400
        if event.user_id != user_id:
            return "Solo el creador puede eliminar la reserva", 403

        ok, dc = self.schedule_repository.get_delete_event(event)
        if dc != 200:
            return ok, dc

        socketio.emit("calendar_update_dashboard", {})
        return "Reserva eliminada", 200


    @handle_exceptions
    def get_users_options(self):
        users, uc = self.schedule_repository.get_users_minimal()
        if uc != 200:
            return users, uc
        # formatea bonito
        for u in users:
            u["name"] = format_name(u["name"])
        return users, 200


    @handle_exceptions
    def get_departments_options(self):
        deps, dc = self.schedule_repository.get_departments()
        if dc != 200:
            return deps, dc
        return deps, 200