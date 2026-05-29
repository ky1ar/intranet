import logging
from datetime import datetime
from flask import render_template
from flask_mail import Message
from application import mail
from application.handlers import handle_exceptions
from application.utils import format_datetime
from application.repository.approval_repository import ApprovalRepository


class ApprovalService:
    def __init__(self):
        self.repository = ApprovalRepository()

    @handle_exceptions
    def get_wp_profile(self, wp_user_id):
        client, sc = self.repository.get_client_by_wp_user_id(wp_user_id)
        if sc != 200:
            return client, sc
        if not client:
            return {"exists": False}, 200
        return {
            "exists": True,
            "client_id": client.id,
            "email": client.email,
            "phone": client.phone,
            "dni": client.document,
        }, 200

    @handle_exceptions
    def get_request_status(self, wp_user_id, type_slug):
        req, sc = self.repository.get_request_status(wp_user_id, type_slug)
        if sc != 200:
            return req, sc
        if not req:
            return {"status": "none"}, 200
        return {
            "status": req.status,
            "id": req.id,
            "type": req.type_rel.slug if req.type_rel else None,
            "access_url": req.access_url,
            "created_at": format_datetime(req.created_at),
        }, 200

    @handle_exceptions
    def create_request(self, data):
        client_id, sc = self.repository.get_or_create_client(data)
        if sc != 200:
            return client_id, sc

        result, sc = self.repository.create_request(client_id, data["type_slug"])
        if sc != 200:
            return result, sc

        if result.get("already_exists"):
            return {"message": "Ya existe una solicitud activa para este servicio", "id": result["id"]}, 200
        return {"message": "Solicitud enviada correctamente", "id": result["id"]}, 200

    @handle_exceptions
    def get_all_requests(self, status_filter=None):
        requests, sc = self.repository.get_all_requests(status_filter)
        if sc != 200:
            return requests, sc
        return [self._format_request(r) for r in requests], 200

    @handle_exceptions
    def approve_request(self, data):
        result, sc = self.repository.approve_request(
            data.get("request_id"), data.get("user_id"), data.get("access_url")
        )
        if sc != 200:
            return result, sc
        self._send_lab_approval_email(result)
        return {"message": "Solicitud aprobada"}, 200

    def _send_lab_approval_email(self, result):
        email = result.get("client_email")
        name  = result.get("client_name") or "Cliente"
        if not email:
            return
        try:
            html_content = render_template(
                "k3d_lab_approved.html",
                client_name=name,
                client_email=email,
                temp_password="Krear3D@2025",
                current_year=datetime.now().year,
            )
            msg = Message(
                subject="Tu acceso a K3D Lab ha sido aprobado",
                sender=("Krear 3D", "web@tiendakrear3d.com"),
                recipients=[email],
                html=html_content,
            )
            mail.send(msg)
        except Exception:
            logging.exception("Error enviando correo de aprobación K3D Lab a %s", email)

    @handle_exceptions
    def reject_request(self, data):
        result, sc = self.repository.reject_request(
            data.get("request_id"), data.get("user_id"), data.get("reason")
        )
        if sc != 200:
            return result, sc
        return {"message": "Solicitud rechazada"}, 200

    def _format_request(self, req):
        client = req.client
        return {
            "id": req.id,
            "client_id": req.client_id,
            "client_name": client.name if client else None,
            "client_email": client.email if client else None,
            "client_phone": client.phone if client else None,
            "client_dni": client.document if client else None,
            "wp_user_id": client.wp_user_id if client else None,
            "type": req.type_rel.name if req.type_rel else None,
            "type_slug": req.type_rel.slug if req.type_rel else None,
            "status": req.status,
            "access_url": req.access_url,
            "rejection_reason": req.rejection_reason,
            "approved_by_name": req.approver.name if req.approver else None,
            "approved_at": format_datetime(req.approved_at) if req.approved_at else None,
            "created_at": format_datetime(req.created_at),
        }
