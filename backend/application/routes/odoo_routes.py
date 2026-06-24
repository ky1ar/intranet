import logging
from flask import Blueprint, request
from application.controllers.odoo_controller import OdooController


odoo_bp = Blueprint("odoo", __name__, url_prefix="/odoo")
controller = OdooController()


@odoo_bp.route("/poll-paid-invoices", methods=["GET"])
def poll_paid_invoices():
    return controller.poll_paid_invoices()


@odoo_bp.route("/invoice", methods=["GET"])
def get_invoice_detail():
    return controller.get_invoice_detail({"invoice_number": request.args.get("number")})


@odoo_bp.route("/order", methods=["GET"])
def get_order_detail():
    return controller.get_order_detail({"order_number": request.args.get("number")})
