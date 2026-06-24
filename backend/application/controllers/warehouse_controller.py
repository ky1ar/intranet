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


    @handle_logs_and_exceptions
    def warehouse_add_stock(self, data):
        return self.warehouse.add_stock(data)


    @handle_logs_and_exceptions
    def warehouse_move_stock(self, data):
        return self.warehouse.move_stock(data)


    @handle_logs_and_exceptions
    def warehouse_search_machines(self, query):
        return self.warehouse.search_machines(query)


    @handle_logs_and_exceptions
    def warehouse_load_excel(self, data):
        return self.warehouse.load_excel(data)


    @handle_logs_and_exceptions
    def warehouse_get_logs(self, page):
        return self.warehouse.get_logs(page=page)

    @handle_logs_and_exceptions
    def warehouse_statistics(self):
        return self.warehouse.statistics()


    @handle_logs_and_exceptions
    def warehouse_picking_plan(self, order_number):
        if not order_number:
            return "number requerido", 400
        return self.warehouse.build_picking_plan(order_number)


    @handle_logs_and_exceptions
    def warehouse_complete_picking(self, data):
        return self.warehouse.complete_picking(data)


    @handle_logs_and_exceptions
    def warehouse_get_occupied_locations(self):
        return self.warehouse.get_occupied_locations()