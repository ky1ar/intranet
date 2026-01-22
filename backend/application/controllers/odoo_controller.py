import logging
from application.handlers import handle_logs_and_exceptions
from application.services.odoo_service import OdooService


class OdooController:
    def __init__(self):
        self.odoo_service = OdooService() 


    @handle_logs_and_exceptions
    def poll_paid_invoices(self):
        return self.odoo_service.poll_paid_invoices()