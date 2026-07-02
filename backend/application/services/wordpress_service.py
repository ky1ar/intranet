import logging
from application.handlers import handle_exceptions
from application.services.order_service import OrderService


class WordpressService:
    def __init__(self):
        self.order_service = OrderService()


    @handle_exceptions
    def order_complete(self, data):
        return self.order_service.ingest_wc_order(data)

    @handle_exceptions
    def order_status_changed(self, data):
        return self.order_service.sync_wc_status(data)
