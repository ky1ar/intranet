import logging

from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.training_service import TrainingService
from flask import g


class TrainingController:
    def __init__(self):
        self.training = TrainingService() 


    @handle_logs_and_exceptions
    def training_calendar(self, offset=0):
        return self.training.get_calendar(int(offset))
    

    @handle_logs_and_exceptions
    def training_get_by_id(self, training_id):
        return self.training.get_by_id(training_id)
