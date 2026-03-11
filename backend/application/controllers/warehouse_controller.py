import logging
from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.warehouse_service import WarehouseService
from flask import g

class WarehouseController:
    def __init__(self):
        self.warehouse = WarehouseService() 


    @handle_logs_and_exceptions
    def warehouse_find_product(self, search):
        return self.warehouse.find_product(search)
    