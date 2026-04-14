import logging
from datetime import timedelta
from application.handlers import handle_db_exceptions
from application.utils import peru_time
from application.db_models.safebuy_model import (
    SafebuyRequest, SafebuyStatus, SafebuyCreditUsage,
    SafebuyAttachment, SafebuyChat
)
from flask import g


class SafebuyRepository:

    @handle_db_exceptions
    def get_statuses(self):
        statuses = g.db_session.query(SafebuyStatus).order_by(SafebuyStatus.id).all()
        return statuses or [], 200

    @handle_db_exceptions
    def get_dashboard(self):
        requests = (
            g.db_session.query(SafebuyRequest)
            .filter(SafebuyRequest.deleted_at.is_(None))
            .order_by(SafebuyRequest.created_at.desc())
            .all()
        )
        return requests or [], 200

    @handle_db_exceptions
    def get_request_by_id(self, request_id):
        req = (
            g.db_session.query(SafebuyRequest)
            .filter(SafebuyRequest.id == request_id, SafebuyRequest.deleted_at.is_(None))
            .first()
        )
        if not req:
            return "Solicitud no encontrada", 404
        return req, 200

    @handle_db_exceptions
    def create_request(self, data):
        diff = float(data["paid_price"]) - float(data["new_price"])

        req = SafebuyRequest(
            client_name=data["client_name"],
            client_email=data.get("client_email"),
            client_phone=data.get("client_phone"),
            client_document=data.get("client_document"),
            order_number=data.get("order_number"),
            purchase_date=data["purchase_date"],
            purchase_channel=data.get("purchase_channel", "web"),
            product_name=data["product_name"],
            product_brand=data.get("product_brand"),
            product_model=data.get("product_model"),
            original_price=data["original_price"],
            paid_price=data["paid_price"],
            new_price=data["new_price"],
            price_difference=diff,
            proof_url=data.get("proof_url"),
            assigned_user_id=data.get("assigned_user_id"),
        )
        g.db_session.add(req)
        g.db_session.commit()
        return {"id": req.id}, 200

    @handle_db_exceptions
    def update_status(self, request_id, status_id, user_id=None, reason=None):
        req = g.db_session.query(SafebuyRequest).get(request_id)
        if not req:
            return "No encontrada", 404

        req.status_id = status_id

        if status_id == 3:  # approved
            req.approved_by = user_id
            req.approved_at = peru_time()
            req.credit_amount = float(req.price_difference)

        if status_id == 6:  # rejected
            req.approved_by = user_id
            req.approved_at = peru_time()
            req.rejection_reason = reason

        g.db_session.commit()
        return "OK", 200

    @handle_db_exceptions
    def update_request(self, request_id, data):
        req = g.db_session.query(SafebuyRequest).get(request_id)
        if not req:
            return "No encontrada", 404

        for key in ["assigned_user_id", "status_id"]:
            if key in data:
                setattr(req, key, data[key])

        g.db_session.commit()
        return "OK", 200

    @handle_db_exceptions
    def apply_credit(self, data):
        req = g.db_session.query(SafebuyRequest).get(data["request_id"])
        if not req:
            return "Solicitud no encontrada", 404

        available = float(req.credit_amount) - float(req.credit_used)
        amount = float(data["amount"])
        order_total = float(data.get("order_total") or 0)

        if amount > available:
            return "Monto excede el crédito disponible", 422

        if order_total > 0 and amount > (order_total * 0.5):
            return f"El crédito no puede cubrir más del 50% de la compra (máx S/ {order_total * 0.5:.2f})", 422

        usage = SafebuyCreditUsage(
            request_id=data["request_id"],
            amount_used=amount,
            order_number=data.get("order_number"),
            order_total=order_total,
            applied_by=data["applied_by"],
            notes=data.get("notes"),
        )
        g.db_session.add(usage)

        req.credit_used = float(req.credit_used) + amount

        if float(req.credit_used) >= float(req.credit_amount):
            req.status_id = 5  # usado completo
        else:
            req.status_id = 4  # usado parcial

        g.db_session.commit()
        return {"id": usage.id}, 200

    @handle_db_exceptions
    def get_credit_history(self, request_id):
        usages = (
            g.db_session.query(SafebuyCreditUsage)
            .filter(SafebuyCreditUsage.request_id == request_id)
            .order_by(SafebuyCreditUsage.created_at.desc())
            .all()
        )
        return usages or [], 200

    @handle_db_exceptions
    def soft_delete(self, request_id):
        req = g.db_session.query(SafebuyRequest).get(request_id)
        if not req:
            return "No encontrada", 404
        req.deleted_at = peru_time()
        g.db_session.commit()
        return "OK", 200

    # ── Attachments ──

    @handle_db_exceptions
    def get_attachments_by_request(self, request_id):
        rows = (
            g.db_session.query(SafebuyAttachment)
            .filter(SafebuyAttachment.request_id == request_id)
            .order_by(SafebuyAttachment.id.desc())
            .all()
        )
        return rows or [], 200

    @handle_db_exceptions
    def get_attachment_by_id(self, attachment_id):
        row = (
            g.db_session.query(SafebuyAttachment)
            .filter(SafebuyAttachment.id == attachment_id)
            .first()
        )
        if not row:
            return "Not found", 404
        return row, 200

    @handle_db_exceptions
    def add_attachment(self, request_id, user_id, target, original_name, stored_name, mime_type, size_bytes):
        row = SafebuyAttachment(
            request_id=request_id,
            target=target,
            user_id=user_id,
            original_name=original_name,
            stored_name=stored_name,
            mime_type=mime_type,
            size_bytes=size_bytes,
            created_at=peru_time(),
        )
        g.db_session.add(row)
        g.db_session.commit()
        return row.id, 200

    # ── Chat ──

    @handle_db_exceptions
    def add_chat(self, request_id, user_id, comment):
        chat = SafebuyChat(
            request_id=request_id,
            commenter_id=user_id,
            comment=comment,
            created_at=peru_time(),
        )
        g.db_session.add(chat)
        g.db_session.commit()
        g.db_session.refresh(chat)
        return chat, 200

    @handle_db_exceptions
    def get_chat_participants(self, request_id, exclude_user_id=None):
        q = (
            g.db_session.query(SafebuyChat.commenter_id)
            .filter(SafebuyChat.request_id == request_id)
        )
        if exclude_user_id is not None:
            q = q.filter(SafebuyChat.commenter_id != exclude_user_id)

        user_ids = [row[0] for row in q.distinct().all()]
        return user_ids, 200