import logging
from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.schedule_service import ScheduleService


class ScheduleController:
    def __init__(self):
        self.schedule = ScheduleService() 


    @handle_logs_and_exceptions
    def schedule_get_month(self, offset=None):
        return self.schedule.get_month(offset)
    

    @handle_logs_and_exceptions
    def schedule_process(self, data):
        if validation_error := validate_request(data, {"user_id"}):
            return validation_error, 400
        return self.schedule.process(data)


    @handle_logs_and_exceptions
    def schedule_delete(self, data):
        if validation_error := validate_request(data, {"event_id"}):
            return validation_error, 400

        event_id = data.get("event_id")
        return self.schedule.delete(event_id)
    

    @handle_logs_and_exceptions
    def schedule_get_visibility(self):
        return self.schedule.get_visibility()

    
    @handle_logs_and_exceptions
    def schedule_get_repeat(self):
        return self.schedule.get_repeat()


    @handle_logs_and_exceptions
    def schedule_get_notify(self):
        return self.schedule.get_notify()


    @handle_logs_and_exceptions
    def schedule_get_colors(self):
        return self.schedule.get_colors()
    

    @handle_logs_and_exceptions
    def schedule_data(self, event_id):
        return self.schedule.data(event_id)


    @handle_logs_and_exceptions
    def schedule_notify_upcoming(self):
        return self.schedule.notify_upcoming_events()
    

    @handle_logs_and_exceptions
    def schedule_get_users(self):
        return self.schedule.get_users_options()

    @handle_logs_and_exceptions
    def schedule_get_departments(self):
        return self.schedule.get_departments_options()


    @handle_logs_and_exceptions
    def schedule_room_process(self, data):
        return self.schedule.room_booking_process(data)


    @handle_logs_and_exceptions
    def schedule_room_delete(self, booking_id, user_id):
        return self.schedule.room_booking_delete(booking_id, user_id)