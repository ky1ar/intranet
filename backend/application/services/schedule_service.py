import logging
from datetime import datetime
from application.handlers import handle_exceptions
from application.repository.schedule_repository import ScheduleRepository


class ScheduleService:
    def __init__(self):
        self.schedule_repository = ScheduleRepository()


    @handle_exceptions
    def get_month(self, offset):
        return True, 200
    

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
    def process(self, data):
        title = data.get("title", "").strip()
        if not title:
            return "Ingresa un título", 422

        raw_start = data.get("start_datetime")
        if not raw_start:
            return "Ingresa un fecha", 422
        #start_datetime = datetime.fromisoformat(raw_start) if "T" in raw_start else datetime.strptime(raw_start, "%Y-%m-%d")
        
        order_status, aec = self.schedule_repository.add_event(data)
        if aec != 200:
            return order_status, aec
        
        return "Evento registrado correctamente", 200


    @handle_exceptions
    def delete(self, data):
        return True, 200


    @handle_exceptions
    def data(self, event_id):
        return True, 200
