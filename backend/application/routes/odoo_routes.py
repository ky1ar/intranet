import logging
from flask import Blueprint, request
from application.controllers.odoo_controller import OdooController


odoo_bp = Blueprint("odoo", __name__, url_prefix="/odoo")
controller = OdooController()


@odoo_bp.route("/poll-paid-invoices", methods=["GET"])
def poll_paid_invoices():
    return controller.poll_paid_invoices()