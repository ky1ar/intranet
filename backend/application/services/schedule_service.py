import logging
from datetime import datetime, timedelta
from calendar import monthrange
from application.handlers import handle_exceptions
from application.repository.schedule_repository import ScheduleRepository
from application.services.general_service import GeneralService


class ScheduleService:
    def __init__(self):
        self.schedule_repository = ScheduleRepository()
        self.general_service = GeneralService()


    @handle_exceptions
    def get_month(self, offset):
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

        events, vc = self.schedule_repository.get_events_in_range(first_day, last_day)
        if vc != 200:
            return events, vc

        events_by_day = {}
        for event in events:
            date_key = event.start_datetime.date().isoformat()
            if date_key not in events_by_day:
                events_by_day[date_key] = []
            events_by_day[date_key].append({
                "id": event.id,
                "title": event.title,
                "all_day": True if event.all_day or event.all_day == 1 else False,
                "start_datetime": event.start_datetime.isoformat(),
                "end_datetime": event.end_datetime.isoformat() if event.end_datetime else None,
                "hex_color": event.hex_color,
            })

        days = []
        for day in range(1, last_day_num + 1):
            current_date = datetime(target_year, target_month, day).date().isoformat()
            days.append({
                "date": current_date,
                "events": events_by_day.get(current_date, [])
            })

        month_name = first_day.strftime("%B").capitalize()

        return {
            "month_name": month_name,
            "year": target_year,
            "offset": offset,
            "days": days
        }, 200
    

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
        return {"visibility": visibility_list}, 200
    
    
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
        return {"repeat": repeat_list}, 200


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
        return {"notify": notify_list}, 200

        
    
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
        return {"colors": colors_list}, 200


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
            
            return "Evento registrado correctamente", 200
        
        event, ec = self.schedule_repository.get_event_by_id(event_id)
        if ec != 200:
            return event, ec
        
        update_event, uec = self.schedule_repository.update_event(event, data)
        if uec != 200:
            return update_event, uec

        return "Evento actualizado correctamente", 200


    @handle_exceptions
    def delete(self, event_id):
        event, ec = self.schedule_repository.get_event_by_id(event_id)
        if ec != 200:
            return event, ec
        
        delete_event, dec = self.schedule_repository.get_delete_event(event)
        if dec != 200:
            return delete_event, dec
        
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
            "repeat": event.repeat_event,
            "notify": event.notify_event,
            "visibility": event.visibility,
            "created_at": event.created_at.isoformat(),
        }, 200
