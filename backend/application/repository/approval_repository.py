import logging
from application.handlers import handle_db_exceptions
from application.utils import peru_time
from application.db_models.approval_model import ApprovalRequest, ApprovalType
from application.models import Clients
from flask import g


class ApprovalRepository:

    @handle_db_exceptions
    def get_or_create_client(self, data):
        """Find client by DNI; if found update wp_user_id/email/phone; if not, create minimal."""
        document   = data.get("dni")
        wp_user_id = data.get("wp_user_id")
        email      = data.get("email")
        phone      = data.get("phone")
        name       = data.get("wp_username", "")

        client = (
            g.db_session.query(Clients)
            .filter(Clients.document == document)
            .first()
        )

        if client:
            if wp_user_id:
                client.wp_user_id = wp_user_id
            if email:
                client.email = email
            if phone:
                client.phone = phone
            g.db_session.commit()
        else:
            client = Clients(
                document=document,
                name=name,
                email=email,
                phone=phone,
                address="",
                wp_user_id=wp_user_id,
            )
            g.db_session.add(client)
            g.db_session.flush()
            g.db_session.commit()

        return client.id, 200

    @handle_db_exceptions
    def get_client_by_wp_user_id(self, wp_user_id):
        client = (
            g.db_session.query(Clients)
            .filter(Clients.wp_user_id == wp_user_id)
            .first()
        )
        return client, 200

    @handle_db_exceptions
    def get_request_status(self, wp_user_id, type_slug):
        req = (
            g.db_session.query(ApprovalRequest)
            .join(ApprovalType, ApprovalRequest.type_id == ApprovalType.id)
            .join(Clients, ApprovalRequest.client_id == Clients.id)
            .filter(
                Clients.wp_user_id == wp_user_id,
                ApprovalType.slug == type_slug,
            )
            .order_by(ApprovalRequest.created_at.desc())
            .first()
        )
        return req, 200

    @handle_db_exceptions
    def create_request(self, client_id, type_slug):
        type_obj = (
            g.db_session.query(ApprovalType)
            .filter(ApprovalType.slug == type_slug)
            .first()
        )
        if not type_obj:
            return "Tipo de solicitud no válido", 400

        existing = (
            g.db_session.query(ApprovalRequest)
            .filter(
                ApprovalRequest.client_id == client_id,
                ApprovalRequest.type_id == type_obj.id,
                ApprovalRequest.status.in_(["pending", "approved"]),
            )
            .first()
        )
        if existing:
            return {"id": existing.id, "already_exists": True}, 200

        req = ApprovalRequest(
            client_id=client_id,
            type_id=type_obj.id,
            status="pending",
        )
        g.db_session.add(req)
        g.db_session.commit()
        return {"id": req.id, "already_exists": False}, 200

    @handle_db_exceptions
    def get_all_requests(self, status_filter=None):
        q = (
            g.db_session.query(ApprovalRequest)
            .order_by(ApprovalRequest.created_at.desc())
        )
        if status_filter:
            q = q.filter(ApprovalRequest.status == status_filter)
        return q.all() or [], 200

    @handle_db_exceptions
    def get_request_by_id(self, request_id):
        req = (
            g.db_session.query(ApprovalRequest)
            .filter(ApprovalRequest.id == request_id)
            .first()
        )
        if not req:
            return "Solicitud no encontrada", 404
        return req, 200

    @handle_db_exceptions
    def approve_request(self, request_id, approved_by, access_url=None):
        req = (
            g.db_session.query(ApprovalRequest)
            .filter(ApprovalRequest.id == request_id)
            .first()
        )
        if not req:
            return "Solicitud no encontrada", 404
        req.status      = "approved"
        req.approved_by = approved_by
        req.approved_at = peru_time()
        req.access_url  = access_url
        g.db_session.commit()
        return {"id": req.id}, 200

    @handle_db_exceptions
    def reject_request(self, request_id, approved_by, reason=None):
        req = (
            g.db_session.query(ApprovalRequest)
            .filter(ApprovalRequest.id == request_id)
            .first()
        )
        if not req:
            return "Solicitud no encontrada", 404
        req.status           = "rejected"
        req.approved_by      = approved_by
        req.approved_at      = peru_time()
        req.rejection_reason = reason
        g.db_session.commit()
        return {"id": req.id}, 200
