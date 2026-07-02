import logging
from application.handlers import handle_logs_and_exceptions
from application.services.wordpress_service import WordpressService


class WordpressController:
    def __init__(self):
        self.wordpress_service = WordpressService() 

    @handle_logs_and_exceptions
    def wordpres_order_complete(self, data):
        return self.wordpress_service.order_complete(data)

    @handle_logs_and_exceptions
    def wordpress_order_status(self, data):
        return self.wordpress_service.order_status_changed(data)
