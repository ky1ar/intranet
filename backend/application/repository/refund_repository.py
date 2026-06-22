from application.handlers import handle_db_exceptions
from application.utils import peru_time
from application.db_models.refund_model import (
    RefundRequest, RefundStatus, RefundAttachment, RefundChat, RefundLink
)
from application.db_models.module_model import UserModulePermission, ModulePermission, Module
from application.models import Clients, ClientOrders, Users
from flask import g
from sqlalchemy import or_, cast, String, func
from datetime import datetime, timedelta


class RefundRepository:

    @handle_db_exceptions
    def get_statuses(self):
        rows = g.db_session.query(RefundStatus).order_by(RefundStatus.id).all()
        return rows or [], 200

    @handle_db_exceptions
    def get_dashboard(self, only_commercial=False):
        q = (
            g.db_session.query(RefundRequest)
            .filter(RefundRequest.deleted_at.is_(None))
        )
        if only_commercial:
            q = q.filter(RefundRequest.is_admin_register == False)
        return q.order_by(RefundRequest.created_at.desc()).all() or [], 200

    @handle_db_exceptions
    def search_requests(self, term, only_commercial=False, limit=20):
        like = f"%{term}%"
        q = (
            g.db_session.query(RefundRequest)
            .join(ClientOrders, RefundRequest.client_order_id == ClientOrders.id)
            .join(Clients, ClientOrders.client_id == Clients.id)
            .filter(RefundRequest.deleted_at.is_(None))
            .filter(or_(
                Clients.name.ilike(like),
                Clients.document.ilike(like),
                cast(ClientOrders.number, String).ilike(like),
            ))
        )
        if only_commercial:
            q = q.filter(RefundRequest.is_admin_register == False)
        rows = q.order_by(RefundRequest.created_at.desc()).limit(limit).all()
        return rows or [], 200

    @handle_db_exceptions
    def get_requests_paginated(self, page=1, per_page=12, only_commercial=False):
        q = (
            g.db_session.query(RefundRequest)
            .filter(RefundRequest.deleted_at.is_(None))
        )
        if only_commercial:
            q = q.filter(RefundRequest.is_admin_register == False)
        total = q.count()
        items = (
            q.order_by(RefundRequest.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return {
            "list": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }, 200

    # ── Statistics ──────────────────────────────────────────────────────────

    def _stats_scope(self, q, only_commercial):
        q = q.filter(RefundRequest.deleted_at.is_(None))
        if only_commercial:
            q = q.filter(RefundRequest.is_admin_register == False)
        return q

    @handle_db_exceptions
    def stats_total(self, only_commercial=False):
        q = self._stats_scope(g.db_session.query(func.count(RefundRequest.id)), only_commercial)
        return q.scalar() or 0, 200

    @handle_db_exceptions
    def stats_executed_money(self, only_commercial=False):
        q = (
            g.db_session.query(
                func.coalesce(func.sum(RefundRequest.net_refund), 0),
                func.coalesce(func.sum(RefundRequest.penalty_amount), 0),
            )
            .join(RefundStatus, RefundRequest.status_id == RefundStatus.id)
            .filter(RefundStatus.slug == "executed")
        )
        q = self._stats_scope(q, only_commercial)
        row = q.first()
        return (float(row[0] or 0), float(row[1] or 0)), 200

    @handle_db_exceptions
    def stats_penalty_count(self, only_commercial=False):
        q = self._stats_scope(
            g.db_session.query(func.count(RefundRequest.id))
            .filter(RefundRequest.applies_penalty == True),
            only_commercial,
        )
        return q.scalar() or 0, 200

    @handle_db_exceptions
    def stats_by_reason(self, only_commercial=False):
        q = self._stats_scope(
            g.db_session.query(RefundRequest.reason, func.count(RefundRequest.id)),
            only_commercial,
        )
        return q.group_by(RefundRequest.reason).order_by(func.count(RefundRequest.id).desc()).all() or [], 200

    @handle_db_exceptions
    def stats_by_month(self, only_commercial=False):
        period = func.date_format(RefundRequest.created_at, "%Y-%m").label("period")
        q = self._stats_scope(
            g.db_session.query(period, func.count(RefundRequest.id)),
            only_commercial,
        )
        return q.group_by("period").order_by("period").all() or [], 200

    @handle_db_exceptions
    def stats_by_assignee(self, start_date=None, end_date=None, only_commercial=False):
        q = (
            g.db_session.query(Users.id, Users.name, func.count(RefundRequest.id))
            .join(Users, RefundRequest.assigned_to == Users.id)
        )
        q = self._stats_scope(q, only_commercial)
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end_excl = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                q = q.filter(RefundRequest.created_at >= start, RefundRequest.created_at < end_excl)
            except ValueError:
                pass
        return (
            q.group_by(Users.id, Users.name)
            .order_by(func.count(RefundRequest.id).desc())
            .all()
        ) or [], 200

    @handle_db_exceptions
    def get_by_id(self, refund_id):
        row = (
            g.db_session.query(RefundRequest)
            .filter(RefundRequest.id == refund_id, RefundRequest.deleted_at.is_(None))
            .first()
        )
        if not row:
            return "Solicitud no encontrada", 404
        return row, 200

    @handle_db_exceptions
    def create(self, data):
        penalty = 10.0 if data.get("applies_penalty") else 0.0
        net = float(data["refund_amount"]) - penalty

        row = RefundRequest(
            status_id=data.get("status_id", 1),
            is_admin_register=bool(data.get("is_admin_register", False)),
            assigned_to=data.get("assigned_to"),
            original_order_number=data.get("original_order_number"),
            client_order_id=data["client_order_id"],
            reason=data["reason"],
            reason_detail=data.get("reason_detail"),
            detail=data.get("detail"),
            order_amount=data["order_amount"],
            refund_amount=data["refund_amount"],
            applies_penalty=bool(data.get("applies_penalty")),
            penalty_amount=round(penalty, 2),
            net_refund=round(net, 2),
            payment_method=data["payment_method"],
            refund_account=data.get("refund_account"),
        )
        g.db_session.add(row)
        g.db_session.commit()
        return row.id, 200

    @handle_db_exceptions
    def update_status(self, refund_id, status_id):
        row = g.db_session.query(RefundRequest).get(refund_id)
        if not row:
            return "No encontrado", 404
        row.status_id = status_id
        g.db_session.commit()
        return "OK", 200

    @handle_db_exceptions
    def update_client_order(self, refund_id, client_order_id):
        row = g.db_session.query(RefundRequest).get(refund_id)
        if not row:
            return "No encontrado", 404
        row.client_order_id = client_order_id
        g.db_session.commit()
        return "OK", 200

    @handle_db_exceptions
    def update_status_and_assign(self, refund_id, status_id, assigned_to):
        row = g.db_session.query(RefundRequest).get(refund_id)
        if not row:
            return "No encontrado", 404
        row.status_id = status_id
        row.assigned_to = assigned_to
        g.db_session.commit()
        return "OK", 200

    @handle_db_exceptions
    def update_penalty(self, refund_id, applies_penalty):
        row = g.db_session.query(RefundRequest).get(refund_id)
        if not row:
            return "No encontrado", 404
        penalty = 10.0 if applies_penalty else 0.0
        row.applies_penalty = applies_penalty
        row.penalty_amount = round(penalty, 2)
        row.net_refund = round(float(row.refund_amount) - penalty, 2)
        g.db_session.commit()
        return "OK", 200

    @handle_db_exceptions
    def update_scheduled_date(self, refund_id, scheduled_date):
        row = g.db_session.query(RefundRequest).get(refund_id)
        if not row:
            return "No encontrado", 404
        row.scheduled_date = scheduled_date
        row.status_id = 5
        g.db_session.commit()
        return "OK", 200

    @handle_db_exceptions
    def soft_delete(self, refund_id):
        row = g.db_session.query(RefundRequest).get(refund_id)
        if not row:
            return "No encontrado", 404
        row.deleted_at = peru_time()
        g.db_session.commit()
        return "OK", 200

    @handle_db_exceptions
    def get_users_with_perm(self, module_slug, perm_slug):
        rows = (
            g.db_session.query(UserModulePermission.user_id)
            .join(ModulePermission, UserModulePermission.module_permission_id == ModulePermission.id)
            .join(Module, ModulePermission.module_id == Module.id)
            .filter(Module.slug == module_slug)
            .filter(ModulePermission.slug == perm_slug)
            .filter(UserModulePermission.granted == True)
            .all()
        )
        return [r[0] for r in rows], 200

    # ── Attachments ──

    @handle_db_exceptions
    def get_attachments(self, refund_id):
        rows = (
            g.db_session.query(RefundAttachment)
            .filter(RefundAttachment.refund_id == refund_id)
            .order_by(RefundAttachment.id.asc())
            .all()
        )
        return rows or [], 200

    @handle_db_exceptions
    def get_attachment_by_id(self, attachment_id):
        row = (
            g.db_session.query(RefundAttachment)
            .filter(RefundAttachment.id == attachment_id)
            .first()
        )
        if not row:
            return "Not found", 404
        return row, 200

    @handle_db_exceptions
    def add_attachment(self, refund_id, user_id, original_name, stored_name, mime_type, size_bytes):
        row = RefundAttachment(
            refund_id=refund_id,
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

    @handle_db_exceptions
    def delete_attachment(self, attachment_id):
        row = g.db_session.query(RefundAttachment).get(attachment_id)
        if not row:
            return "Not found", 404
        g.db_session.delete(row)
        g.db_session.commit()
        return "OK", 200

    # ── Chat ──

    @handle_db_exceptions
    def add_chat(self, refund_id, user_id, comment):
        chat = RefundChat(
            refund_id=refund_id,
            commenter_id=user_id,
            comment=comment,
            created_at=peru_time(),
        )
        g.db_session.add(chat)
        g.db_session.commit()
        g.db_session.refresh(chat)
        return chat, 200

    # ── Links ──

    @handle_db_exceptions
    def create_link(self, token, user_id):
        row = RefundLink(token=token, user_id=user_id, status_id=1)
        g.db_session.add(row)
        g.db_session.commit()
        g.db_session.refresh(row)
        return row, 200

    @handle_db_exceptions
    def get_link_by_id(self, link_id):
        row = g.db_session.query(RefundLink).filter(RefundLink.id == link_id).first()
        if not row:
            return "Enlace no encontrado", 404
        return row, 200

    @handle_db_exceptions
    def get_link_by_token(self, token):
        row = g.db_session.query(RefundLink).filter(RefundLink.token == token).first()
        if not row:
            return "Enlace no encontrado", 404
        return row, 200

    @handle_db_exceptions
    def mark_link_opened(self, link_id):
        row = g.db_session.query(RefundLink).get(link_id)
        if not row:
            return "Enlace no encontrado", 404
        row.status_id = 2
        g.db_session.commit()
        return "OK", 200

    @handle_db_exceptions
    def mark_link_used(self, link_id, refund_id):
        row = g.db_session.query(RefundLink).get(link_id)
        if not row:
            return "Enlace no encontrado", 404
        row.status_id = 3
        row.refund_id = refund_id
        g.db_session.commit()
        return "OK", 200

    @handle_db_exceptions
    def delete_link(self, link_id):
        row = g.db_session.query(RefundLink).get(link_id)
        if not row:
            return "Enlace no encontrado", 404
        row.status_id = 4
        g.db_session.commit()
        return "OK", 200

    @handle_db_exceptions
    def get_links_page(self, page=1, per_page=20):
        total = g.db_session.query(RefundLink).count()
        rows = (
            g.db_session.query(RefundLink)
            .order_by(RefundLink.id.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows or [], total, 200

    @handle_db_exceptions
    def get_chat_participants(self, refund_id, exclude_user_id=None):
        q = (
            g.db_session.query(RefundChat.commenter_id)
            .filter(RefundChat.refund_id == refund_id)
        )
        if exclude_user_id is not None:
            q = q.filter(RefundChat.commenter_id != exclude_user_id)
        user_ids = [r[0] for r in q.distinct().all()]

        refund, rc = self.get_by_id(refund_id)
        if rc == 200 and refund.assigned_to and refund.assigned_to != exclude_user_id:
            if refund.assigned_to not in user_ids:
                user_ids.append(refund.assigned_to)

        return user_ids, 200
