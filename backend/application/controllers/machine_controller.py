import logging

from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.machine_service import MachineService


class MachineController:
    def __init__(self):
        self.machine = MachineService() 


    @handle_logs_and_exceptions
    def machine_find_machines(self, machine_name):
        if not machine_name:
            return None, 400
        
        return self.machine.find_machines(machine_name)
