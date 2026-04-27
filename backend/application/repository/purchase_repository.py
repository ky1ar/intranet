import logging
from decimal import Decimal
from datetime import date, datetime, timezone, timedelta, timezone
from application.handlers import handle_db_exceptions
from application.models import PurchaseRequest, PurchaseType, PurchaseUrgency, PurchaseItems, PurchaseChats
from application.utils import peru_time
from flask import g
from sqlalchemy import or_
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.orm import selectinload


class PurchaseRepository:
    def __init__(self):
        self.worker_level = 2
        self.leader_level = 3
        self.management_level = 4


    @handle_db_exceptions
    def update_order_numbers(self, purchase_id, items):
        if not items:
            return "Items requeridos", 400

        mapping = {}
        for i in items:
            if not i.get("id"):
                continue
            mapping[int(i["id"])] = (i.get("order_number") or "").strip() or None

        if not mapping:
            return "Items inválidos", 400

        db_items = (
            g.db_session.query(PurchaseItems)
            .filter(
                PurchaseItems.purchase_id == purchase_id,
                PurchaseItems.deleted_at.is_(None),
                PurchaseItems.id.in_(list(mapping.keys())),
            )
            .all()
        )

        if not db_items:
            return "Items no encontrados", 404

        for it in db_items:
            it.order_number = mapping.get(it.id)

        g.db_session.commit()
        return "Nº de pedido actualizado", 200


    @handle_db_exceptions
    def add_purchase(self, data, user):
        initial_status_id = data.get("_initial_status", 1)

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
            user_id=user.id,
            type_id=data.get("type_id"),
            urgency_id=data.get("urgency_id"),
            needed_date=needed_date,
            express=data.get("express"),
            it_validation=data.get("it_validation"),
            status_id=initial_status_id,
            created_at=peru_time(),
        )

        g.db_session.add(purchase)
        g.db_session.flush()

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

        comment = data.get("comment")

        if comment:
            purchase_chat = PurchaseChats(
                purchase_id=purchase.id,
                comment=comment,
                commenter_id=user.id,
                created_at=peru_time(),
            )
            g.db_session.add(purchase_chat)

        g.db_session.commit()
        return purchase.id, 200


    @handle_db_exceptions
    def set_status(self, purchase_id, status_id):
        purchase = (
            g.db_session.query(PurchaseRequest)
            .filter(
                PurchaseRequest.id == purchase_id,
                PurchaseRequest.deleted_at.is_(None),
            )
            .first()
        )
        if not purchase:
            return "Solicitud no encontrada", 404

        purchase.status_id = status_id
        g.db_session.commit()

        return purchase.id, 200


    @handle_db_exceptions
    def get_purchase_by_id(self, purchase_id):
        purchase = (
            g.db_session.query(PurchaseRequest)
            .options(
                selectinload(PurchaseRequest.items),
                selectinload(PurchaseRequest.chats)
            )
            .filter(PurchaseRequest.id == purchase_id)
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
        purchase.urgency_id = data.get("urgency_id", purchase.urgency_id)
        purchase.needed_date = needed_date
        purchase.express = data.get("express")
        purchase.it_validation = data.get("it_validation")
        
        for item in purchase.items:
            if not item.deleted_at:
                item.deleted_at = peru_time()

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
    def get_statuses(self):
        from application.models import PurchaseStatus
        statuses = (
            g.db_session.query(PurchaseStatus)
            .filter(PurchaseStatus.id <= 9)
            .order_by(PurchaseStatus.id.asc())
            .all()
        )
        return statuses, 200


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


    @handle_db_exceptions
    def add_chat(self, purchase_id, user_id, comment):
        chat = PurchaseChats(
            purchase_id=purchase_id,
            commenter_id=user_id,
            comment=comment,
            created_at=peru_time(),
        )
        g.db_session.add(chat)
        g.db_session.commit()
        g.db_session.refresh(chat)

        return chat, 200
    
    
    @handle_db_exceptions
    def get_chat_participants(self, purchase_id, exclude_user_id = None, include_owner = True):
        q = (
            g.db_session.query(PurchaseChats.commenter_id)
            .filter(PurchaseChats.purchase_id == purchase_id)
        )

        if exclude_user_id is not None:
            q = q.filter(PurchaseChats.commenter_id != exclude_user_id)

        user_ids = [row[0] for row in q.distinct().all()]

        if include_owner:
            owner_id = (
                g.db_session.query(PurchaseRequest.user_id)
                .filter(PurchaseRequest.id == purchase_id, PurchaseRequest.deleted_at.is_(None))
                .scalar()
            )
            if owner_id and owner_id != exclude_user_id and owner_id not in user_ids:
                user_ids.append(owner_id)

        return user_ids, 200


    @handle_db_exceptions
    def find_purchases(self, query, visibility):
        from application.models import Users
        term = f"%{query}%"

        base = (
            g.db_session.query(PurchaseRequest)
            .join(Users, Users.id == PurchaseRequest.user_id)
            .outerjoin(
                PurchaseItems,
                (PurchaseItems.purchase_id == PurchaseRequest.id) &
                (PurchaseItems.deleted_at.is_(None))
            )
            .filter(
                PurchaseRequest.deleted_at.is_(None),
                or_(
                    Users.name.ilike(term),
                    PurchaseItems.title.ilike(term),
                ),
            )
            .distinct()
        )

        if visibility:
            base = base.filter(PurchaseRequest.user_id.in_(visibility))

        results = base.order_by(PurchaseRequest.id.desc()).limit(20).all()
        return results, 200


    @handle_db_exceptions
    def get_purchase_history(self, visibility, page, per_page=20):
        base = g.db_session.query(PurchaseRequest)

        if visibility:
            base = base.filter(PurchaseRequest.user_id.in_(visibility))

        total = base.count()
        pages = max(1, -(-total // per_page))  # ceil division

        purchases = (
            base
            .order_by(PurchaseRequest.id.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return {"list": purchases, "total": total, "pages": pages}, 200


    @handle_db_exceptions
    def soft_delete(self, purchase_id):
        purchase = (
            g.db_session.query(PurchaseRequest)
            .filter(
                PurchaseRequest.id == purchase_id,
                PurchaseRequest.deleted_at.is_(None),
            )
            .first()
        )
        if not purchase:
            return "Solicitud no encontrada", 404

        purchase.deleted_at = peru_time()
        g.db_session.commit()

        return "Solicitud eliminada", 200