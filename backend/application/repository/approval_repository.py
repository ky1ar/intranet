import logging
import os
import secrets
from application.handlers import handle_db_exceptions
from application.utils import peru_time, normalize_phone, upload_path, file_extension
from application.db_models.approval_model import ApprovalRequest, ApprovalType, ApprovalChats
from application.models import Clients
from config import Paths
from flask import g, request
from application.proxy.apiperu import ApiPeru


class ApprovalRepository:

    @handle_db_exceptions
    def get_or_create_client(self, data):
        """Find client by DNI; if found update wp_user_id/email/phone; if not, create minimal."""
        document   = data.get("dni")
        wp_user_id = data.get("wp_user_id")
        email      = data.get("email")
        phone      = normalize_phone(data.get("phone"))
        wp_name    = data.get("wp_username", "")

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
            # Consultamos RENIEC SOLO si el cliente aún no tiene nombre, para no
            # repetir la consulta en cada solicitud (el nombre nunca viene de WP).
            if not client.name:
                client.name = self._resolve_name(document) or wp_name
            g.db_session.commit()
        else:
            name = self._resolve_name(document) or wp_name
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

    def _resolve_name(self, document):
        """Nombre del titular desde RENIEC/API Perú por DNI. Cacheado en Redis por
        el proxy, y aquí solo se invoca cuando el cliente no tiene nombre todavía.
        Devuelve None si la consulta falla (no bloquea la solicitud)."""
        if not document:
            return None
        try:
            info, sc = ApiPeru().get_name("dni", document)
            if sc == 200 and info and info.get("name"):
                return info["name"]
        except Exception:
            logging.exception("No se pudo resolver el nombre por DNI %s", document)
        return None

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
    def create_request(self, client_id, type_slug, invoice_number=None):
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
                ApprovalRequest.status.in_(["pending", "in_review", "approved"]),
            )
            .first()
        )
        if existing:
            return {"id": existing.id, "already_exists": True}, 200

        voucher_filename = self._save_voucher()
        req = ApprovalRequest(
            client_id=client_id,
            type_id=type_obj.id,
            status="pending",
            created_at=peru_time(),
            invoice_number=invoice_number,
            voucher_filename=voucher_filename,
        )
        g.db_session.add(req)
        g.db_session.commit()
        return {"id": req.id, "already_exists": False, "type_name": type_obj.name}, 200

    def _save_voucher(self):
        """Guarda el adjunto de boleta/factura (solo imagen o PDF). Devuelve el nombre o None."""
        voucher = request.files.get("voucher")
        if not voucher or not voucher.filename:
            return None
        ext = file_extension(voucher.filename)
        if ext not in {"pdf", "png", "jpg", "jpeg", "webp"}:
            return None
        filename = f"{secrets.token_hex(16)}.{ext}"
        path = os.path.join(upload_path(Paths.APPROVAL_VOUCHERS), filename)
        voucher.save(path)
        return filename

    @handle_db_exceptions
    def get_dashboard(self):
        reqs = (
            g.db_session.query(ApprovalRequest)
            .order_by(ApprovalRequest.created_at.desc())
            .all()
        )
        return reqs or [], 200

    @handle_db_exceptions
    def set_review(self, request_id):
        req = (
            g.db_session.query(ApprovalRequest)
            .filter(ApprovalRequest.id == request_id)
            .first()
        )
        if not req:
            return "Solicitud no encontrada", 404
        if req.status != "pending":
            return "Solo se puede iniciar revisión de solicitudes pendientes", 400
        req.status = "in_review"
        g.db_session.commit()
        return {"id": req.id}, 200

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
    def get_request_info(self, request_id):
        """Datos mínimos de la solicitud, extraídos dentro de la sesión."""
        req = (
            g.db_session.query(ApprovalRequest)
            .filter(ApprovalRequest.id == request_id)
            .first()
        )
        if not req:
            return "Solicitud no encontrada", 404
        return {
            "id": req.id,
            "status": req.status,
            "client_email": req.client.email if req.client else None,
            "client_name": req.client.name if req.client else None,
            "type_slug": req.type_rel.slug if req.type_rel else None,
        }, 200

    @handle_db_exceptions
    def approve_request(self, request_id, approved_by, access_url=None):
        req = (
            g.db_session.query(ApprovalRequest)
            .filter(ApprovalRequest.id == request_id)
            .first()
        )
        if not req:
            return "Solicitud no encontrada", 404
        client_name  = req.client.name  if req.client  else None
        client_email = req.client.email if req.client  else None
        type_slug    = req.type_rel.slug if req.type_rel else None
        req.status      = "approved"
        req.approved_by = approved_by
        req.approved_at = peru_time()
        req.access_url  = access_url
        g.db_session.commit()
        return {"id": req.id, "client_name": client_name, "client_email": client_email, "type_slug": type_slug}, 200

    @handle_db_exceptions
    def add_chat(self, approval_id, user_id, comment):
        chat = ApprovalChats(
            approval_id=approval_id,
            commenter_id=user_id,
            comment=comment,
            created_at=peru_time(),
        )
        g.db_session.add(chat)
        g.db_session.commit()
        g.db_session.refresh(chat)
        return chat, 200

    @handle_db_exceptions
    def get_chat_commenters(self, approval_id, exclude_user_id=None):
        q = (
            g.db_session.query(ApprovalChats.commenter_id)
            .filter(ApprovalChats.approval_id == approval_id)
        )
        if exclude_user_id is not None:
            q = q.filter(ApprovalChats.commenter_id != exclude_user_id)
        return [row[0] for row in q.distinct().all()], 200

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
