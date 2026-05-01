from application.handlers import handle_db_exceptions
from application.utils import peru_time
from application.db_models.refund_model import (
    RefundRequest, RefundStatus, RefundAttachment, RefundChat
)
from application.db_models.module_model import UserModulePermission, ModulePermission, Module
from flask import g


class RefundRepository:

    @handle_db_exceptions
    def get_statuses(self):
        rows = g.db_session.query(RefundStatus).order_by(RefundStatus.id).all()
        return rows or [], 200

    @handle_db_exceptions
    def get_dashboard(self, user_id=None, only_commercial=False):
        q = (
            g.db_session.query(RefundRequest)
            .filter(RefundRequest.deleted_at.is_(None))
        )
        if user_id is not None:
            q = q.filter(RefundRequest.registered_by == user_id)
        if only_commercial:
            q = q.filter(RefundRequest.is_admin_register == False)
        return q.order_by(RefundRequest.created_at.desc()).all() or [], 200

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
            registered_by=data["registered_by"],
            is_admin_register=bool(data.get("is_admin_register", False)),
            client_order_id=data["client_order_id"],
            reason=data["reason"],
            detail=data.get("detail"),
            order_amount=data["order_amount"],
            refund_amount=data["refund_amount"],
            applies_penalty=bool(data.get("applies_penalty")),
            penalty_amount=round(penalty, 2),
            net_refund=round(net, 2),
            payment_method=data["payment_method"],
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
        if rc == 200 and refund.registered_by != exclude_user_id:
            if refund.registered_by not in user_ids:
                user_ids.append(refund.registered_by)

        return user_ids, 200
