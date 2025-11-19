import logging
from decimal import Decimal
from datetime import date, datetime, timezone, timedelta, timezone
from application.handlers import handle_db_exceptions
from application.models import PurchaseRequest, PurchaseType, PurchaseUrgency, PurchaseItems
from application.utils import peru_time
from flask import g
from sqlalchemy import or_
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.orm import selectinload


class PurchaseRepository:
    def __init__(self):
        pass


    @handle_db_exceptions
    def add_purchase(self, data):
        user_id = get_jwt_identity()

        items_data = data.get("items") or []
        if not items_data:
            return "Debe registrar al menos un ítem", 400

        needed_date = None
        needed_date_str = data.get("needed_date")
        if needed_date_str:
            try:
                needed_date = datetime.strptime(needed_date_str, "%Y-%m-%d").date()
            except ValueError:
                return "Fecha inválida", 400

        purchase = PurchaseRequest(
            user_id=user_id,
            type_id=data.get("type_id", 1),
            user_comment=data.get("comments") or data.get("user_comment"),
            urgency_id=data.get("urgency_id", 1),
            needed_date=needed_date,
            express=1 if data.get("express") else 0,
            total_amount=Decimal("0.00"),
            total_items=0,
            status_id=1,
            created_at=peru_time(),
        )

        g.db_session.add(purchase)
        g.db_session.flush()

        total_items = 0
        total_amount = Decimal("0.00")

        for item in items_data:
            title = (item.get("title") or "").strip()
            quantity = int(item.get("quantity") or 0)

            if not title or quantity <= 0:
                continue

            price_raw = item.get("price")
            price = None
            if price_raw not in (None, ""):
                price = Decimal(str(price_raw))

            purchase_item = PurchaseItems(
                purchase_id=purchase.id,
                title=title,
                description=item.get("description"),
                quantity=quantity,
                price=price,
                url=item.get("url"),
                ruc=item.get("ruc"),
            )
            g.db_session.add(purchase_item)

            total_items += quantity
            if price is not None:
                total_amount += price * quantity

        if total_items == 0:
            g.db_session.rollback()
            return "Debe registrar al menos un ítem válido", 400

        purchase.total_items = total_items
        purchase.total_amount = total_amount

        g.db_session.commit()
        return purchase.id, 200


    @handle_db_exceptions
    def get_purchase_by_id(self, purchase_id):
        purchase = (
            g.db_session.query(PurchaseRequest)
            .options(selectinload(PurchaseRequest.items))
            .filter(
                PurchaseRequest.id == purchase_id,
                PurchaseRequest.deleted_at.is_(None),
            )
            .first()
        )
        if not purchase:
            return "Solicitud no encontrada", 404

        # (opcional) validar que solo el dueño pueda verla
        # current_user_id = get_jwt_identity()
        # if purchase.user_id != current_user_id:
        #     return "No autorizado", 403

        return purchase, 200
    

    @handle_db_exceptions
    def update_purchase(self, data):
        purchase_id = data.get("purchase_id")
        current_user_id = int(get_jwt_identity())

        purchase = (
            g.db_session.query(PurchaseRequest)
            .options(selectinload(PurchaseRequest.items))
            .filter(
                PurchaseRequest.id == purchase_id,
                PurchaseRequest.deleted_at.is_(None),
            )
            .first()
        )
        if not purchase:
            return "Solicitud no encontrada", 404

        # Solo el dueño puede editar (ajusta según tu caso de uso)
        #if purchase.user_id != int(current_user_id):
        #    return "No autorizado para editar esta solicitud", 403

        items_data = data.get("items") or []
        if not items_data:
            return "Debe registrar al menos un ítem", 400

        needed_date = None
        needed_date_str = data.get("needed_date")
        if needed_date_str:
            try:
                needed_date = datetime.strptime(needed_date_str, "%Y-%m-%d").date()
            except ValueError:
                return "Fecha inválida", 400

        purchase.type_id = data.get("type_id", purchase.type_id)
        purchase.user_comment = data.get("user_comment") or purchase.user_comment
        purchase.urgency_id = data.get("urgency_id", purchase.urgency_id)
        purchase.urgency_id = data.get("urgency_id", purchase.urgency_id)
        purchase.needed_date = needed_date
        purchase.express = 1 if data.get("express") else 0

        status_id = data.get("status_id")
        if status_id:
            purchase.leader_comment = data.get("leader_comment") or purchase.leader_comment
            purchase.status_id = status_id

        # Marcamos ítems anteriores como eliminados (soft delete)
        now = peru_time()
        for item in purchase.items:
            if not item.deleted_at:
                item.deleted_at = now

        # Creamos nuevos ítems desde el payload
        total_items = 0
        total_amount = Decimal("0.00")

        for item in items_data:
            title = (item.get("title") or "").strip()
            quantity = int(item.get("quantity") or 0)

            if not title or quantity <= 0:
                continue

            price_raw = item.get("price")
            price = None
            if price_raw not in (None, ""):
                price = Decimal(str(price_raw))

            new_item = PurchaseItems(
                purchase_id=purchase.id,
                title=title,
                description=item.get("description"),
                quantity=quantity,
                price=price,
                url=item.get("url"),
                ruc=item.get("ruc"),
            )
            g.db_session.add(new_item)

            total_items += quantity
            if price is not None:
                total_amount += price * quantity

        if total_items == 0:
            g.db_session.rollback()
            return "Debe registrar al menos un ítem válido", 400

        purchase.total_items = total_items
        purchase.total_amount = total_amount

        g.db_session.commit()
        return purchase.id, 200


    @handle_db_exceptions
    def get_purchase_requests(self, visibility):
        query  = (
            g.db_session.query(PurchaseRequest)
            .filter(PurchaseRequest.deleted_at.is_(None))
        )
        if visibility:
            query = query.filter(PurchaseRequest.user_id.in_(visibility))

        purchase_requests = (
            query
            .order_by(PurchaseRequest.id.desc())
            .all()
        )

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