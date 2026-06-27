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

    # ------------------------------------------------------------- machines
    @handle_logs_and_exceptions
    def list_machines(self, data):
        return self.machine.list_machines(
            page=data.get("page", 1),
            per_page=data.get("per_page", 12),
            q=data.get("q"),
            category_id=data.get("category_id"),
            brand_id=data.get("brand_id"),
        )

    @handle_logs_and_exceptions
    def get_machine(self, machine_id):
        return self.machine.get_machine_detail(machine_id)

    @handle_logs_and_exceptions
    def create_machine(self, data):
        if validation := validate_request(data, {"model", "brand_id", "category_id"}):
            return validation, 400
        return self.machine.create_machine(data, data.get("image_file"))

    @handle_logs_and_exceptions
    def update_machine(self, data):
        return self.machine.update_machine(data.get("id"), data, data.get("image_file"))

    # ----------------------------------------------------------- categories
    @handle_logs_and_exceptions
    def list_categories(self):
        return self.machine.list_categories()

    @handle_logs_and_exceptions
    def create_category(self, data):
        if validation := validate_request(data, {"name"}):
            return validation, 400
        return self.machine.create_category(data)

    @handle_logs_and_exceptions
    def update_category(self, data):
        return self.machine.update_category(data.get("id"), data)

    # --------------------------------------------------------------- brands
    @handle_logs_and_exceptions
    def list_brands(self):
        return self.machine.list_brands()

    @handle_logs_and_exceptions
    def create_brand(self, data):
        if validation := validate_request(data, {"name"}):
            return validation, 400
        return self.machine.create_brand(data)

    @handle_logs_and_exceptions
    def update_brand(self, data):
        return self.machine.update_brand(data.get("id"), data)
