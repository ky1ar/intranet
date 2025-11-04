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

        return self.schedule.delete(data)
    

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

