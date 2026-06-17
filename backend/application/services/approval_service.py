import logging
import os
from datetime import datetime
from flask import render_template, request
from flask_mail import Message
from application import mail, socketio
from application.handlers import handle_exceptions
from application.utils import format_datetime, format_name, file_extension
from application.repository.approval_repository import ApprovalRepository
from application.services.push_service import PushSender
from application.services.module_service import ModuleService
from application.services.courses_provisioning_service import (
    CoursesProvisioningService, FabProvisioningService, is_course_slug, is_fab_slug,
)
from application.services.guide_service import GuideService
from config import Courses, Paths


# Estados del tablero (kanban). El status de approval_request es string libre.
STATUS_GROUPS = [
    {"slug": "pending",   "name": "Pendiente"},
    {"slug": "in_review", "name": "En revisión"},
    {"slug": "approved",  "name": "Aprobado"},
    {"slug": "rejected",  "name": "Rechazado"},
]


class ApprovalService:
    def __init__(self):
        self.repository = ApprovalRepository()
        self.push_service = PushSender()
        self.module_service = ModuleService()

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
        voucher = request.files.get("voucher")
        if not voucher or not voucher.filename:
            return "Debes adjuntar la boleta o factura (imagen o PDF)", 400
        if file_extension(voucher.filename) not in {"pdf", "png", "jpg", "jpeg", "webp"}:
            return "El archivo adjunto debe ser una imagen o PDF", 400

        client_id, sc = self.repository.get_or_create_client(data)
        if sc != 200:
            return client_id, sc

        result, sc = self.repository.create_request(
            client_id, data["type_slug"], data.get("invoice_number")
        )
        if sc != 200:
            return result, sc

        if result.get("already_exists"):
            return {"message": "Ya existe una solicitud activa para este servicio", "id": result["id"]}, 200
        self._notify_new_request(result["id"], result.get("type_name") or data.get("type_slug"))
        socketio.emit("approval_update", {})
        return {"message": "Solicitud enviada correctamente", "id": result["id"]}, 200

    def _notify_new_request(self, request_id, type_name):
        """Push a quienes tengan el permiso 'notify' del modulo de aprobaciones."""
        try:
            user_ids, _ = self.module_service.get_user_ids_with_permission("approvals", "notify")
            if not user_ids:
                return
            self.push_service.send_to_users(
                user_ids=user_ids,
                title="Nueva solicitud de aprobación",
                body=f"AP-{request_id} - {type_name}",
                data={"url": "/approvals", "title": "Nueva solicitud de aprobación"},
            )
        except Exception:
            logging.exception("Error notificando nueva solicitud de aprobación AP-%s", request_id)

    @handle_exceptions
    def get_all_requests(self, status_filter=None):
        requests, sc = self.repository.get_all_requests(status_filter)
        if sc != 200:
            return requests, sc
        return [self._format_request(r) for r in requests], 200

    @handle_exceptions
    def dashboard(self):
        requests, sc = self.repository.get_dashboard()
        if sc != 200:
            return requests, sc
        grouped = {
            g["slug"]: {"status_slug": g["slug"], "status_name": g["name"], "requests": []}
            for g in STATUS_GROUPS
        }
        # Máximo 10 por columna (las más recientes; vienen ordenadas por fecha desc).
        # Limitamos aquí para no formatear/enviar/loguear cientos de solicitudes.
        for req in requests:
            st = req.status if req.status in grouped else "pending"
            if len(grouped[st]["requests"]) >= 10:
                continue
            grouped[st]["requests"].append(self._format_request(req))
        return [grouped[g["slug"]] for g in STATUS_GROUPS], 200

    @handle_exceptions
    def search_requests(self, term):
        term = (term or "").strip()
        if len(term) < 2:
            return [], 200
        requests, sc = self.repository.search_requests(term)
        if sc != 200:
            return requests, sc
        return [self._format_request(r) for r in requests], 200

    @handle_exceptions
    def history(self, data):
        page     = data.get("page", 1)
        per_page = data.get("per_page", 12)
        result, sc = self.repository.get_requests_paginated(page, per_page)
        if sc != 200:
            return result, sc
        return {
            "list": [self._format_request(r) for r in result["list"]],
            "pagination": {
                "total":    result["total"],
                "page":     result["page"],
                "per_page": result["per_page"],
                "pages":    result["pages"],
            },
        }, 200

    @handle_exceptions
    def start_review(self, data):
        result, sc = self.repository.set_review(data.get("request_id"))
        if sc != 200:
            return result, sc
        socketio.emit("approval_update", {})
        return {"message": "Solicitud en revisión"}, 200

    def serve_voucher(self, filename):
        """Ruta del adjunto para que el intranet lo visualice/valide."""
        filepath = os.path.join(Paths.APPROVAL_VOUCHERS, filename)
        if not os.path.isfile(filepath):
            return None
        return filepath

    @handle_exceptions
    def approve_request(self, data):
        request_id = data.get("request_id")
        user_id    = data.get("user_id")

        info, sc = self.repository.get_request_info(request_id)
        if sc != 200:
            return info, sc

        type_slug    = info.get("type_slug")
        client_email = info.get("client_email")
        client_name  = info.get("client_name")

        # Guías: el contenido de la guía del equipo debe existir antes de aprobar.
        if type_slug == "guia":
            exists, esc = GuideService().content_exists_for_request(request_id)
            if esc != 200:
                return exists, esc
            if not exists:
                return "Debes crear la guía del equipo (contenido) antes de aprobar esta solicitud", 400

        # Cursos: primero aprovisionamos en la plataforma; si falla, NO aprobamos
        # (así la solicitud no queda "aprobada" sin acceso real). Es idempotente.
        if is_course_slug(type_slug):
            if not client_email:
                return "El cliente no tiene un correo registrado", 400
            prov, psc = CoursesProvisioningService().provision(client_email, client_name, type_slug)
            if psc != 200:
                return prov, psc
            result, sc = self.repository.approve_request(request_id, user_id, Courses.PLATFORM_URL)
            if sc != 200:
                return result, sc
            self._send_course_email(client_email, client_name, prov)
            socketio.emit("approval_update", {})
            return {"message": "Solicitud aprobada y acceso al curso creado"}, 200

        # FAB (modelos STL): aseguramos la cuenta y habilitamos fab_enabled, sin
        # otorgar ningún curso. Igual que cursos, si falla NO aprobamos. Idempotente.
        if is_fab_slug(type_slug):
            if not client_email:
                return "El cliente no tiene un correo registrado", 400
            prov, psc = FabProvisioningService().provision(client_email, client_name)
            if psc != 200:
                return prov, psc
            result, sc = self.repository.approve_request(request_id, user_id, Courses.FAB_URL)
            if sc != 200:
                return result, sc
            self._send_fab_email(client_email, client_name, prov)
            socketio.emit("approval_update", {})
            return {"message": "Solicitud aprobada y acceso a STL habilitado"}, 200

        # Otros tipos (p.ej. guías): solo se aprueba, sin correo de cursos.
        result, sc = self.repository.approve_request(request_id, user_id, None)
        if sc != 200:
            return result, sc
        socketio.emit("approval_update", {})
        return {"message": "Solicitud aprobada"}, 200

    def _send_course_email(self, email, name, prov):
        """Correo de curso: con credenciales si la cuenta es nueva; sin ellas si ya existía."""
        if not email:
            return
        try:
            created     = bool(prov.get("created_account"))
            course_name = prov.get("course_name") or "tu curso"
            if created:
                template = "course_account_created.html"
                subject  = "Tu acceso al curso ha sido aprobado"
            else:
                template = "course_added.html"
                subject  = "Se agregó un nuevo curso a tu cuenta"
            html_content = render_template(
                template,
                client_name=name or "Cliente",
                client_email=email,
                temp_pin=prov.get("temp_pin"),
                course_name=course_name,
                platform_url=Courses.PLATFORM_URL,
                current_year=datetime.now().year,
            )
            msg = Message(
                subject=subject,
                sender=("Krear 3D", "web@tiendakrear3d.com"),
                recipients=[email],
                html=html_content,
            )
            mail.send(msg)
        except Exception:
            logging.exception("Error enviando correo de curso a %s", email)

    def _send_fab_email(self, email, name, prov):
        """Correo de acceso FAB (STL): con credenciales si la cuenta es nueva; sin ellas si ya existía."""
        if not email:
            return
        try:
            created = bool(prov.get("created_account"))
            if created:
                template = "fab_account_created.html"
                subject  = "Tu acceso a los modelos STL ha sido aprobado"
            else:
                template = "fab_access_enabled.html"
                subject  = "Acceso a modelos STL habilitado"
            html_content = render_template(
                template,
                client_name=name or "Cliente",
                client_email=email,
                temp_pin=prov.get("temp_pin"),
                platform_url=Courses.FAB_URL,
                current_year=datetime.now().year,
            )
            msg = Message(
                subject=subject,
                sender=("Krear 3D", "web@tiendakrear3d.com"),
                recipients=[email],
                html=html_content,
            )
            mail.send(msg)
        except Exception:
            logging.exception("Error enviando correo de acceso FAB a %s", email)

    @handle_exceptions
    def reject_request(self, data):
        result, sc = self.repository.reject_request(
            data.get("request_id"), data.get("user_id"), data.get("reason")
        )
        if sc != 200:
            return result, sc
        socketio.emit("approval_update", {})
        return {"message": "Solicitud rechazada"}, 200

    @handle_exceptions
    def get_request_detail(self, request_id):
        req, sc = self.repository.get_request_by_id(request_id)
        if sc != 200:
            return req, sc
        return self._format_request(req, with_chats=True), 200

    @handle_exceptions
    def send_chat(self, data):
        request_id = data.get("request_id")
        user_id    = data.get("user_id")
        comment    = (data.get("comment") or "").strip()

        if not request_id:
            return "request_id requerido", 400
        if not user_id:
            return "user_id requerido", 400
        if not comment:
            return "Comentario vacío", 400

        req, sc = self.repository.get_request_by_id(request_id)
        if sc != 200:
            return req, sc

        chat, cc = self.repository.add_chat(request_id, user_id, comment)
        if cc != 200:
            return chat, cc

        participants, _ = self.repository.get_chat_commenters(
            request_id, exclude_user_id=user_id
        )
        if participants:
            self.push_service.send_to_users(
                user_ids=participants,
                title=f"Nuevo mensaje, solicitud AP-{request_id}",
                body=f"{format_name(chat.commenter.name, True)}: {comment}",
            )
        socketio.emit("approval_update", {})

        return {
            "id": chat.id,
            "comment": chat.comment,
            "commenter_id": chat.commenter_id,
            "commenter_name": format_name(chat.commenter.name),
            "commenter_image": chat.commenter.image,
            "created_at": format_datetime(chat.created_at),
        }, 200

    def _format_request(self, req, with_chats=False):
        client = req.client
        data = {
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
            "invoice_number": req.invoice_number,
            "voucher_filename": req.voucher_filename,
            "access_url": req.access_url,
            "rejection_reason": req.rejection_reason,
            "approved_by_name": req.approver.name if req.approver else None,
            "approved_at": format_datetime(req.approved_at) if req.approved_at else None,
            "created_at": format_datetime(req.created_at),
        }

        # Las solicitudes de tipo 'guia' llevan machine_id. Marcamos is_guide
        # para que la vista muestre el nombre del equipo en la etiqueta.
        if req.type_rel and req.type_rel.slug == "guia":
            data["is_guide"] = True
            machine = req.machine
            if machine:
                brand = machine.brand.name if machine.brand else ""
                data["machine_name"] = f"{brand} {machine.model}".strip()

        if with_chats:
            data["chats"] = [
                {
                    "id": c.id,
                    "comment": c.comment,
                    "commenter_id": c.commenter_id,
                    "commenter_name": format_name(c.commenter.name),
                    "commenter_image": c.commenter.image,
                    "created_at": format_datetime(c.created_at),
                }
                for c in sorted(req.chats, key=lambda x: x.id)
            ]
        return data
