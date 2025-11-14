import logging
from datetime import date, datetime, timezone, timedelta, timezone
from application.handlers import handle_db_exceptions
from application.models import PurchaseRequest, PurchaseType, PurchaseUrgency
from application.utils.general import peru_time
from flask import g
from sqlalchemy import or_
from flask_jwt_extended import get_jwt_identity


class PurchaseRepository:
    def __init__(self):
        pass


    @handle_db_exceptions
    def add_purchase(self, data):
        purchase = PurchaseRequest(
            user_id = 23, # get_jwt_identity
            type_id = data.get("type_id", 1),
            title = data.get("title"),
            reason = data.get("reason"),
            urgency_id = data.get("urgency_id", 1),
            quantity = data.get("quantity"),
            price = data.get("price"),
            needed_date = data.get("needed_date"),
            express = data.get("express", 0),
            status = "created",
            created_at = peru_time()
        )

        g.db_session.add(purchase)
        g.db_session.commit()
        return purchase.id, 200


    @handle_db_exceptions
    def get_purchase_requests(self):
        purchase_requests = g.db_session.query(PurchaseRequest).order_by(PurchaseRequest.id.asc()).all()
        if not purchase_requests:
            return [], 200

        return purchase_requests, 200
    

    @handle_db_exceptions
    def get_purchase_type(self):
        purchase_type = g.db_session.query(PurchaseType).order_by(PurchaseType.id.asc()).all()
        if not purchase_type:
            return [], 200

        return purchase_type, 200


    @handle_db_exceptions
    def get_urgency(self):
        urgency = g.db_session.query(PurchaseUrgency).order_by(PurchaseUrgency.id.asc()).all()
        if not urgency:
            return [], 200

        return urgency, 200