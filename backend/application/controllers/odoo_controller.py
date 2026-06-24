import logging
from application.handlers import handle_logs_and_exceptions
from application.services.odoo_service import OdooService


class OdooController:
    def __init__(self):
        self.odoo_service = OdooService() 


    @handle_logs_and_exceptions
    def poll_paid_invoices(self):
        return self.odoo_service.poll_paid_invoices()


    @handle_logs_and_exceptions
    def get_invoice_detail(self, data):
        invoice_number = (data or {}).get("invoice_number")
        if not invoice_number:
            return "invoice_number requerido", 400
        return self.odoo_service.get_invoice_detail(invoice_number)


    @handle_logs_and_exceptions
    def get_order_detail(self, data):
        order_number = (data or {}).get("order_number")
        if not order_number:
            return "order_number requerido", 400
        return self.odoo_service.get_sale_order_detail(order_number)
