import os
import uuid
from datetime import timedelta
from flask import request, send_file
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename
from application.handlers import handle_exceptions
from application.utils import (
    format_name, format_datetime, format_date, file_extension,
    size, allowed_extension, peru_time
)
from application.repository.refund_repository import RefundRepository
from application.repository.user_repository import UserRepository
from application.repository.client_repository import ClientRepository
from application.services.module_service import ModuleService
from application.services.push_service import PushSender
from application import socketio
from config import Paths

REASON_LABELS = {
    "stock":    "Stock",
    "atencion": "Atención",
    "precio":   "Precio",
    "envio":    "Envío",
}

PAYMENT_LABELS = {
    "transferencia": "Transferencia",
    "web":           "Web",
    "link_pago":     "Link de pago",
}

# Fixed Peruvian holidays (month, day)
_PERU_HOLIDAYS = frozenset([
    (1, 1), (5, 1), (6, 29), (7, 28), (7, 29),
    (8, 30), (11, 1), (12, 8), (12, 9), (12, 25),
])

_HIGH_PERMS = {"validate", "approve_area", "approve_gerencia"}


class RefundService:
    def __init__(self):
        self.repository = RefundRepository()
        self.user_repository = UserRepository()
        self.client_repository = ClientRepository()
        self.module_service = ModuleService()
        self.push_service = PushSender()

    def _has_perm(self, user_id, perm_slug):
        result, code = self.module_service.check_permission(user_id, "refunds", perm_slug)
        if code != 200:
            return False
        return result.get("granted", False) if isinstance(result, dict) else False

    def _is_holiday(self, d):
        return (d.month, d.day) in _PERU_HOLIDAYS

    def _next_valid_friday(self, now):
        """Returns the scheduled date (Peru time, all rules):

        Mon/Tue/Wed  → this Friday; if holiday → its Thursday.
        Thu          → this Friday (any hour) if not holiday.
                       Before noon + holiday Friday → today (Thursday).
                       After noon  + holiday Friday → next Friday; if that also holiday → its Thursday.
        Fri not holiday → today (before noon) / next Friday (after noon); if next is holiday → its Thursday.
        Fri holiday  → next Friday; if that also holiday → its Thursday.
        """
        weekday = now.weekday()
        today = now.date()
        before_noon = now < now.replace(hour=12, minute=0, second=0, microsecond=0)

        def resolve(friday):
            """Return friday, or its Thursday if friday is a holiday."""
            return friday - timedelta(days=1) if self._is_holiday(friday) else friday

        if weekday == 4 and not self._is_holiday(today):  # Friday, not holiday
            return today if before_noon else resolve(today + timedelta(days=7))

        if weekday == 3:  # Thursday
            this_friday = today + timedelta(days=1)
            if not self._is_holiday(this_friday):
                return this_friday
            if before_noon:
                return today  # Thu before noon, holiday Friday → today
            return resolve(today + timedelta(days=8))  # Thu after noon → following Friday

        # Mon / Tue / Wed  OR  Friday-is-holiday (treated identically)
        days = 7 if weekday == 4 else 4 - weekday
        return resolve(today + timedelta(days=days))

    def _push_to_perm(self, perm_slug, title, body, exclude_id=None):
        """Send push notification to all users with the given permission."""
        user_ids, _ = self.repository.get_users_with_perm("refunds", perm_slug)
        if exclude_id is not None:
            user_ids = [uid for uid in user_ids if uid != exclude_id]
        if not user_ids:
            return
        tokens, _ = self.push_service.prefetch_registration_tokens(user_ids)
        socketio.start_background_task(self.push_service.send_to_tokens, tokens, title, body, None)

    def _push_to_perms(self, perm_slugs, title, body, exclude_id=None):
        """Send push to all users who have any of the given permissions."""
        all_ids = set()
        for slug in perm_slugs:
            ids, _ = self.repository.get_users_with_perm("refunds", slug)
            all_ids.update(ids)
        if exclude_id is not None:
            all_ids.discard(exclude_id)
        if not all_ids:
            return
        tokens, _ = self.push_service.prefetch_registration_tokens(list(all_ids))
        socketio.start_background_task(self.push_service.send_to_tokens, tokens, title, body, None)

    # ── Statuses ──

    @handle_exceptions
    def get_statuses(self):
        statuses, sc = self.repository.get_statuses()
        if sc != 200:
            return statuses, sc
        return [{"id": s.id, "name": s.name, "slug": s.slug} for s in statuses], 200

    # ── Dashboard ──

    @handle_exceptions
    def dashboard(self):
        user_id = int(get_jwt_identity())
        statuses, sc = self.repository.get_statuses()
        if sc != 200:
            return statuses, sc

        if self._has_perm(user_id, "view_all"):
            requests, rc = self.repository.get_dashboard()
        elif self._has_perm(user_id, "view_commercial"):
            requests, rc = self.repository.get_dashboard(only_commercial=True)
        else:
            requests, rc = self.repository.get_dashboard(user_id=user_id)
        if rc != 200:
            return requests, rc

        grouped = {
            s.id: {
                "status_id": s.id,
                "status_name": s.name,
                "status_slug": s.slug,
                "requests": [],
            }
            for s in statuses
        }

        for req in requests:
            sid = req.status_id
            if sid not in grouped:
                continue
            grouped[sid]["requests"].append({
                "id": req.id,
                "client_name": req.client_order.client.name if req.client_order else None,
                "client_dni": req.client_order.client.document if req.client_order else None,
                "order_number": str(req.client_order.number) if req.client_order else None,
                "reason": REASON_LABELS.get(req.reason, req.reason),
                "net_refund": float(req.net_refund or 0),
                "is_admin_register": req.is_admin_register,
                "registered_by": req.registered_by,
                "registered_by_name": format_name(req.registrant.name) if req.registrant else None,
                "scheduled_date": req.scheduled_date.isoformat() if req.scheduled_date else None,
                "created_at": format_datetime(req.created_at),
            })

        return [grouped[k] for k in sorted(grouped)], 200

    # ── Detail ──

    def _serialize_attachment(self, row):
        return {
            "id": row.id,
            "original_name": row.original_name,
            "mime_type": row.mime_type,
            "size_bytes": row.size_bytes,
            "size_h": size(row.size_bytes),
            "ext": file_extension(row.original_name),
            "uploaded_by": row.user_id,
            "inline_url": f"/refund/attachment/{row.id}?disposition=inline",
            "download_url": f"/refund/attachment/{row.id}?disposition=attachment",
            "preview_url": f"/refund/attachment/{row.id}/preview",
        }

    @handle_exceptions
    def get_refund(self, refund_id):
        req, rc = self.repository.get_by_id(refund_id)
        if rc != 200:
            return req, rc

        attachments, _ = self.repository.get_attachments(refund_id)

        chats = []
        for chat in (req.chats or []):
            chats.append({
                "id": chat.id,
                "comment": chat.comment,
                "commenter_id": chat.commenter_id,
                "commenter_name": format_name(chat.commenter.name),
                "commenter_image": chat.commenter.image,
                "created_at": format_datetime(chat.created_at),
            })

        return {
            "id": req.id,
            "status_id": req.status_id,
            "status_name": req.status.name,
            "status_slug": req.status.slug,
            "registered_by": req.registered_by,
            "registered_by_name": format_name(req.registrant.name) if req.registrant else None,
            "is_admin_register": req.is_admin_register,
            "client_order_id": req.client_order_id,
            "client_dni": req.client_order.client.document if req.client_order else None,
            "client_name": req.client_order.client.name if req.client_order else None,
            "order_number": str(req.client_order.number) if req.client_order else None,
            "reason": req.reason,
            "reason_label": REASON_LABELS.get(req.reason, req.reason),
            "detail": req.detail,
            "order_amount": float(req.order_amount or 0),
            "refund_amount": float(req.refund_amount or 0),
            "applies_penalty": req.applies_penalty,
            "penalty_amount": float(req.penalty_amount or 0),
            "net_refund": float(req.net_refund or 0),
            "payment_method": req.payment_method,
            "payment_method_label": PAYMENT_LABELS.get(req.payment_method, req.payment_method),
            "scheduled_date": req.scheduled_date.isoformat() if req.scheduled_date else None,
            "created_at": format_datetime(req.created_at),
            "attachments": [self._serialize_attachment(a) for a in attachments],
            "chats": chats,
        }, 200

    # ── Create ──

    @handle_exceptions
    def create(self):
        user_id = int(get_jwt_identity())

        has_commercial = self._has_perm(user_id, "register_commercial")
        has_admin_reg  = self._has_perm(user_id, "register_admin")

        if not has_commercial and not has_admin_reg:
            return "Sin permiso para registrar extornos", 403

        reason         = request.form.get("reason", "").strip()
        order_amount   = request.form.get("order_amount")
        refund_amount  = request.form.get("refund_amount")
        payment_method = request.form.get("payment_method", "").strip()

        if not reason:
            return "Motivo requerido", 400
        if reason not in {"stock", "atencion", "precio", "envio"}:
            return "Motivo inválido", 400
        if not order_amount or not refund_amount:
            return "Montos requeridos", 400
        if payment_method not in {"transferencia", "web", "link_pago"}:
            return "Medio de pago inválido", 400

        applies_penalty = request.form.get("applies_penalty") in ("true", "1", "True")
        is_admin_reg_flag = has_admin_reg and not has_commercial

        # Determine initial status based on creator's permissions
        if self._has_perm(user_id, "approve_area"):
            initial_status = 4
        elif self._has_perm(user_id, "validate") and has_admin_reg:
            initial_status = 3
        else:
            initial_status = 1

        raw_client_order_id = request.form.get("client_order_id") or None
        if raw_client_order_id:
            client_order_id = int(raw_client_order_id)
        else:
            # Resolve or create client + client_order from form fields
            order_number = request.form.get("order_number", "").strip()
            client_dni   = request.form.get("client_dni", "").strip()
            client_name  = request.form.get("client_name", "").strip()
            if not order_number or not client_dni:
                return "Número de pedido y DNI son requeridos", 400

            # Find or create client
            client, client_rc = self.client_repository.get_client_by_document(client_dni)
            if client_rc == 200:
                resolved_client_id = client.id
            else:
                resolved_client_id, crc = self.client_repository.add_client_minimal(client_dni, client_name or client_dni)
                if crc != 200:
                    return resolved_client_id, crc

            # Find or create client_order
            order, order_rc = self.client_repository.get_client_order_by_number(order_number)
            if order_rc == 200:
                client_order_id = order.id
            else:
                client_order_id, orc = self.client_repository.add_client_order(order_number, resolved_client_id)
                if orc != 200:
                    return client_order_id, orc

        data = {
            "status_id":        initial_status,
            "registered_by":    user_id,
            "is_admin_register": is_admin_reg_flag,
            "client_order_id":  client_order_id,
            "reason":           reason,
            "detail":           request.form.get("detail") or None,
            "order_amount":     order_amount,
            "refund_amount":    refund_amount,
            "applies_penalty":  applies_penalty,
            "payment_method":   payment_method,
        }

        refund_id, rc = self.repository.create(data)
        if rc != 200:
            return refund_id, rc

        # Save attached evidence files
        files = request.files.getlist("files[]")
        for f in files:
            if not f or not f.filename:
                continue
            if not allowed_extension(f.filename):
                continue
            self._save_file(refund_id, user_id, f)

        socketio.emit("refund_update", {})

        # Push to validate-permission holders when it's a commercial register at status 1
        if initial_status == 1 and not is_admin_reg_flag:
            user, _ = self.user_repository.get_user_by_id(user_id)
            name = format_name(user.name, True) if user else "Alguien"
            self._push_to_perm(
                "validate",
                f"Nuevo extorno #{refund_id}",
                f"{name} registró un extorno",
                exclude_id=user_id,
            )

        return {"id": refund_id}, 200

    # ── Update status ──

    @handle_exceptions
    def update_status(self, data):
        user_id   = int(get_jwt_identity())
        refund_id = data.get("refund_id")
        status_id = data.get("status_id")

        if not refund_id or not status_id:
            return "refund_id y status_id requeridos", 400

        req, rc = self.repository.get_by_id(refund_id)
        if rc != 200:
            return req, rc

        # States: 1=registered 2=reviewing 3=area_pending 4=gerencia_pending
        #         5=scheduled 6=executed 7=reverted
        can_high = any(self._has_perm(user_id, p) for p in _HIGH_PERMS)

        if status_id == 2:
            if not self._has_perm(user_id, "move"):
                return "Sin permiso para mover a En revisión", 403
        elif status_id == 3:
            if not self._has_perm(user_id, "validate"):
                return "Sin permiso para enviar a área", 403
        elif status_id == 4:
            if not self._has_perm(user_id, "approve_area"):
                return "Sin permiso para aprobar área", 403
        elif status_id == 5:
            if not self._has_perm(user_id, "approve_gerencia"):
                return "Sin permiso para programar", 403
        elif status_id == 6:
            if not can_high:
                return "Sin permiso para ejecutar", 403
            if req.status_id != 5:
                return "Solo se puede ejecutar desde Programado", 400
        elif status_id == 7:
            if not can_high:
                return "Sin permiso para revertir", 403
            if req.status_id >= 6:
                return "No se puede revertir un extorno ya ejecutado", 400
        else:
            return "Estado inválido", 400

        # Gerencia approval (→5) auto-schedules
        if status_id == 5:
            now = peru_time()
            scheduled = self._next_valid_friday(now)
            result, rc = self.repository.update_scheduled_date(refund_id, scheduled)
            if rc != 200:
                return result, rc
        else:
            result, rc = self.repository.update_status(refund_id, status_id)
            if rc != 200:
                return result, rc

        socketio.emit("refund_update", {})

        user, _ = self.user_repository.get_user_by_id(user_id)
        name = format_name(user.name, True) if user else "Alguien"

        if status_id == 3:
            self._push_to_perm("approve_area", f"Extorno #{refund_id} pendiente", f"{name} envió el extorno a área", user_id)
        elif status_id == 4:
            self._push_to_perm("approve_gerencia", f"Extorno #{refund_id} pendiente", f"{name} aprobó en área", user_id)
        elif status_id == 5:
            now = peru_time()
            scheduled = self._next_valid_friday(now)
            self._push_to_perms(
                ["validate", "approve_area"],
                f"Extorno #{refund_id} programado",
                f"Agendado para el {scheduled.strftime('%d/%m/%Y')}",
                user_id,
            )

        return "OK", 200

    # ── Update penalty ──

    @handle_exceptions
    def update_penalty(self, refund_id, data):
        user_id = int(get_jwt_identity())

        req, rc = self.repository.get_by_id(refund_id)
        if rc != 200:
            return req, rc

        if req.status_id >= 6:
            return "No se puede modificar la penalidad en este estado", 400

        if req.status_id == 1:
            if req.registered_by != user_id:
                return "Solo el creador puede modificar la penalidad en este estado", 403
        else:
            if not any(self._has_perm(user_id, p) for p in _HIGH_PERMS):
                return "Sin permiso para modificar la penalidad", 403

        applies = bool(data.get("applies_penalty"))
        result, rc = self.repository.update_penalty(refund_id, applies)
        if rc != 200:
            return result, rc

        socketio.emit("refund_update", {})
        return "OK", 200

    # ── Delete ──

    @handle_exceptions
    def delete(self, refund_id):
        user_id = int(get_jwt_identity())
        req, rc = self.repository.get_by_id(refund_id)
        if rc != 200:
            return req, rc
        if req.registered_by != user_id and not any(self._has_perm(user_id, p) for p in _HIGH_PERMS):
            return "Sin permiso", 403
        result, rc = self.repository.soft_delete(refund_id)
        if rc == 200:
            socketio.emit("refund_update", {})
        return result, rc

    # ── Attachments ──

    def _save_file(self, refund_id, user_id, f):
        ext  = file_extension(f.filename)
        safe = secure_filename(f.filename) or f"file.{ext}"
        stored_name = f"{uuid.uuid4().hex}_{safe}"
        path = os.path.join(Paths.REFUND, stored_name)
        f.save(path)
        self.repository.add_attachment(
            refund_id=refund_id,
            user_id=user_id,
            original_name=f.filename,
            stored_name=stored_name,
            mime_type=getattr(f, "mimetype", None),
            size_bytes=os.path.getsize(path),
        )

    @handle_exceptions
    def attachments_upload(self):
        user_id   = int(get_jwt_identity())
        refund_id = request.form.get("refund_id")
        files     = request.files.getlist("files[]")

        if not refund_id:
            return "refund_id requerido", 400

        req, rc = self.repository.get_by_id(int(refund_id))
        if rc != 200:
            return req, rc

        # Creator OR high-perm can upload in Registrado (status 1)
        can_upload = req.status_id == 1 and (
            req.registered_by == user_id or
            any(self._has_perm(user_id, p) for p in _HIGH_PERMS)
        )
        if not can_upload:
            return "Sin permiso para agregar archivos en este estado", 403

        if not files:
            return "Sin archivos", 400

        saved = []
        for f in files:
            if not f or not f.filename:
                continue
            if not allowed_extension(f.filename):
                return f"Tipo no permitido: {f.filename}", 400
            try:
                pos = f.stream.tell()
                f.stream.seek(0, os.SEEK_END)
                f_size = f.stream.tell()
                f.stream.seek(pos)
                if f_size > Paths.MAX_BYTES:
                    return f"Archivo muy grande: {f.filename}", 400
            except Exception:
                pass

            self._save_file(int(refund_id), user_id, f)
            saved.append(f.filename)

        socketio.emit("refund_update", {})
        return {"uploaded": saved}, 200

    def attachment_stream(self, attachment_id, disposition="inline"):
        row, rc = self.repository.get_attachment_by_id(int(attachment_id))
        if rc != 200:
            return row, rc
        path = os.path.join(Paths.REFUND, row.stored_name)
        if not os.path.exists(path):
            return "Archivo no encontrado", 404
        return send_file(
            path,
            mimetype=row.mime_type or "application/octet-stream",
            as_attachment=(disposition == "attachment"),
            download_name=row.original_name,
        )

    def attachment_preview(self, attachment_id):
        row, rc = self.repository.get_attachment_by_id(int(attachment_id))
        if rc != 200:
            return row, rc
        ext = (row.original_name.rsplit(".", 1)[-1] if "." in row.original_name else "").lower()
        inline_url = f"/refund/attachment/{row.id}?disposition=inline"
        if ext in {"png", "jpg", "jpeg", "webp", "gif", "pdf"}:
            return {"kind": "url", "url": inline_url, "name": row.original_name}, 200
        return {
            "kind": "download",
            "name": row.original_name,
            "message": "Vista previa no disponible",
            "download_url": f"/refund/attachment/{row.id}?disposition=attachment",
        }, 200

    @handle_exceptions
    def delete_attachment(self, attachment_id):
        user_id = int(get_jwt_identity())
        row, rc = self.repository.get_attachment_by_id(int(attachment_id))
        if rc != 200:
            return row, rc

        req, rrc = self.repository.get_by_id(row.refund_id)
        if rrc != 200:
            return req, rrc

        # Only high-perm users can delete attachments (creator can upload but not delete after creation)
        if req.status_id != 1 or not any(self._has_perm(user_id, p) for p in _HIGH_PERMS):
            return "Sin permiso para eliminar archivos en este estado", 403

        path = os.path.join(Paths.REFUND, row.stored_name)
        if os.path.exists(path):
            os.remove(path)

        result, rc = self.repository.delete_attachment(attachment_id)
        if rc == 200:
            socketio.emit("refund_update", {})
        return result, rc

    # ── Chat ──

    @handle_exceptions
    def chat(self, data):
        refund_id = data.get("refund_id")
        if not refund_id:
            return "refund_id requerido", 400
        comment = (data.get("comment") or "").strip()
        if not comment:
            return "Comentario vacío", 400

        current_user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(current_user_id)
        if uc != 200:
            return user, uc

        req, rc = self.repository.get_by_id(refund_id)
        if rc != 200:
            return req, rc

        chat, cc = self.repository.add_chat(refund_id=refund_id, user_id=current_user_id, comment=comment)
        if cc != 200:
            return chat, cc

        participants, _ = self.repository.get_chat_participants(refund_id, exclude_user_id=current_user_id)
        title = f"Nuevo mensaje, Extorno #{refund_id}"
        body  = f"{format_name(user.name, True)}: {comment}"
        tokens, _ = self.push_service.prefetch_registration_tokens(participants)
        socketio.start_background_task(self.push_service.send_to_tokens, tokens, title, body, None)

        return {
            "id": chat.id,
            "comment": chat.comment,
            "commenter_id": chat.commenter_id,
            "commenter_name": format_name(chat.commenter.name),
            "commenter_image": chat.commenter.image,
            "created_at": format_datetime(chat.created_at),
        }, 200
