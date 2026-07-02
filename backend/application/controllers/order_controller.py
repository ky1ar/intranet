from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.order_service import OrderService


class OrderController:
    def __init__(self):
        self.service = OrderService()

    @handle_logs_and_exceptions
    def ingest_wc_order(self, data):
        return self.service.ingest_wc_order(data)

    @handle_logs_and_exceptions
    def get_dashboard(self, data):
        return self.service.dashboard()

    @handle_logs_and_exceptions
    def get_order_detail(self, data):
        return self.service.get_order_detail(data.get("order_id"))

    @handle_logs_and_exceptions
    def search_orders(self, term):
        return self.service.search_orders(term)

    @handle_logs_and_exceptions
    def history(self, data):
        return self.service.history(data)

    @handle_logs_and_exceptions
    def change_status(self, data):
        if validation := validate_request(data, {"order_id", "status"}):
            return validation, 400
        return self.service.change_status(data)

    @handle_logs_and_exceptions
    def refresh_wc_status(self, data):
        return self.service.refresh_wc_status(data.get("order_id"))
