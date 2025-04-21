import logging

from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.clients_service import ClientsService


class ClientsController:
    def __init__(self):
        self.clients = ClientsService() 


    @handle_logs_and_exceptions
    def clients_all(self, data):
        return self.clients.clients_all(data)
    