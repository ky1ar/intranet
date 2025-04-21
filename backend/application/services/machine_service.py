import logging, json
from application import redis_client
from application.handlers import handle_exceptions
from application.repository.machine_repository import MachineRepository


class MachineService:
    def __init__(self):
        self.repository = MachineRepository()
        
    
    @handle_exceptions
    def find_machines(self, machine_name):
        if len(machine_name) < 3:
            return None, 400
        
        machines, machines_status = self.repository.get_machines(machine_name)
        if machines_status != 200:
            return machines, machines_status
        
        machines_list = [
            {
                "id": machine.id,
                "name": machine.full_name,
                "image": machine.image,

            } for machine in machines
        ]
        return machines_list, 200
