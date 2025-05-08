import logging

from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.clients_service import ClientsService


class ClientsController:
    def __init__(self):
        self.clients = ClientsService() 

    
    @handle_logs_and_exceptions
    def user_data_document(self, document):
        if not document:
            return 'Documento inválido', 400
        
        return self.clients.get_data(document)
    
    
    @handle_logs_and_exceptions
    def user_name(self, document):
        return self.clients.get_name(document)
    

    @handle_logs_and_exceptions
    def clients_all(self, data):
        return self.clients.clients_all(data)
    

    @handle_logs_and_exceptions
    def order_get_user_order(self, order_number):
        if not order_number:
            return 'Número de orden inválido', 400
        return self.clients.get_user_order(order_number)
    
    