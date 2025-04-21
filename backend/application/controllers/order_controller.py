import logging

from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.order_service import OrderService
from flask import g


class OrderController:
    def __init__(self):
        self.order = OrderService() 


    @handle_logs_and_exceptions
    def order_get_user_order(self, order_number):
        if not order_number:
            return 'Número de orden inválido', 400
        return self.order.get_user_order(order_number)


