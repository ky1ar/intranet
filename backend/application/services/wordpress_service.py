import logging
from application.handlers import handle_exceptions


class WordpressService:
    def __init__(self):
        pass


    @handle_exceptions
    def order_complete(self, data):
        # logging.info(data)
        return "OK", 200