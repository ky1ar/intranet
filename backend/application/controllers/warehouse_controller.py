import logging
from application.handlers import handle_logs_and_exceptions
from application.services.warehouse_service import WarehouseService


class WarehouseController:
    def __init__(self):
        self.warehouse = WarehouseService()


    @handle_logs_and_exceptions
    def warehouse_find_product(self, search):
        return self.warehouse.find_product(search)


    @handle_logs_and_exceptions
    def warehouse_location_detail(self, label):
        return self.warehouse.get_location(label)


    @handle_logs_and_exceptions
    def warehouse_remove_stock(self, data):
        return self.warehouse.remove_stock(data)