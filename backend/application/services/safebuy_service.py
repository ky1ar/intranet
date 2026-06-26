import logging, os, uuid
from flask import request, send_file
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename
from application.handlers import handle_exceptions
from application.utils import format_name, format_date, format_datetime, file_extension, size, allowed_extension, upload_path, peru_time
from application.repository.safebuy_repository import SafebuyRepository
from application.repository.user_repository import UserRepository
from application.repository.client_repository import ClientRepository
from application.repository.machine_repository import MachineRepository
from application.proxy.apiperu import ApiPeru
from application.services.push_service import PushSender
from application import socketio
from config import Paths


class SafebuyService:
    def __init__(self):
        self.repository = SafebuyRepository()
        self.user_repository = UserRepository()
        self.client_repository = ClientRepository()
        self.machine_repository = MachineRepository()
        self.apiperu = ApiPeru()
        self.push_service = PushSender()

    @handle_exceptions
    def get_statuses(self):
        statuses, sc = self.repository.get_statuses()
        if sc != 200:
            return statuses, sc
        return [{"id": s.id, "name": s.name, "image": f"{s.slug}.svg"} for s in statuses], 200

    @handle_exceptions
    def dashboard(self):
        statuses, sc = self.repository.get_statuses()
        if sc != 200:
            return statuses, sc

        requests, rc = self.repository.get_dashboard()
        if rc != 200:
            return requests, rc

        grouped = {}
        for s in statuses:
            grouped[s.id] = {
                "status_id": s.id,
                "status_name": s.name,
                "status_slug": s.slug,
                "requests": [],
            }

        for req in requests:
            sid = req.status_id
            if sid not in grouped:
                continue

            available = float(req.credit_amount or 0) - float(req.credit_used or 0)

            product_brand = req.machine.brand.name if req.machine else None
            product_model = req.machine.model if req.machine else None

            grouped[sid]["requests"].append({
                "id": req.id,
                "client_name": req.client.name if req.client else None,
                "client_document": req.client.document if req.client else None,
                "product_brand": product_brand,
                "product_model": product_model,
                "product_image": req.machine.image if req.machine.image != "" else "impresoras-varias1.webp",
                "order_number": req.order_number,
                "purchase_date": req.purchase_date.isoformat() if req.purchase_date else None,
                "original_price": float(req.original_price or 0),
                "paid_price": float(req.paid_price or 0),
                "new_price": float(req.new_price or 0),
                "price_difference": float(req.price_difference or 0),
                "credit_amount": float(req.credit_amount or 0),
                "credit_used": float(req.credit_used or 0),
                "credit_available": available,
                "assigned_name": format_name(req.assigned.name) if req.assigned else None,
                "created_at": format_datetime(req.created_at),
            })

        result = [grouped[k] for k in sorted(grouped.keys())]
        return result, 200

    def _serialize_attachment(self, r):
        return {
            "id": r.id,
            "target": r.target,
            "original_name": r.original_name,
            "mime_type": r.mime_type,
            "size_bytes": r.size_bytes,
            "size_h": size(r.size_bytes),
            "created_at": str(r.created_at),
            "ext": file_extension(r.original_name),
            "inline_url": f"/safebuy/attachment/{r.id}?disposition=inline",
            "download_url": f"/safebuy/attachment/{r.id}?disposition=attachment",
            "preview_url": f"/safebuy/attachment/{r.id}/preview",
        }

    @handle_exceptions
    def get_request(self, request_id):
        req, rc = self.repository.get_request_by_id(request_id)
        if rc != 200:
            return req, rc

        # Historial de uso
        usages, uc = self.repository.get_credit_history(request_id)
        usage_list = []
        if uc == 200:
            for u in usages:
                usage_list.append({
                    "id": u.id,
                    "amount_used": float(u.amount_used),
                    "order_number": u.order_number,
                    "order_total": float(u.order_total or 0),
                    "applied_by_name": format_name(u.user.name) if u.user else "-",
                    "notes": u.notes,
                    "created_at": format_datetime(u.created_at),
                })

        available = float(req.credit_amount or 0) - float(req.credit_used or 0)

        # Attachments
        attachments, arc = self.repository.get_attachments_by_request(request_id)
        target_labels = {
            "receipt": "Boleta / Factura",
            "screenshot": "Captura de pantalla",
            "default": "Archivos",
        }

        att_grouped = {}
        if arc == 200:
            for r in attachments:
                key = (r.target or "default").strip() or "default"
                att_grouped.setdefault(key, []).append(self._serialize_attachment(r))

        ordered_targets = ["receipt", "screenshot", "default"]
        attachment_sections = []
        for target in ordered_targets:
            files = att_grouped.get(target, [])
            if files:
                attachment_sections.append({
                    "target": target,
                    "label": target_labels.get(target, target.replace("_", " ").title()),
                    "files": files,
                })

        for target, files in att_grouped.items():
            if target not in ordered_targets and files:
                attachment_sections.append({
                    "target": target,
                    "label": target_labels.get(target, target.replace("_", " ").title()),
                    "files": files,
                })

        # Chats
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

        product_brand = req.machine.brand.name if req.machine else None
        product_model = req.machine.model if req.machine else None

        client = req.client
        return {
            "id": req.id,
            "status_id": req.status_id,
            "status_name": req.status.name,
            "status_slug": req.status.slug,
            "client_id": req.client_id,
            "client_name": client.name if client else None,
            "client_email": client.email if client else None,
            "client_phone": client.phone[2:] if client and client.phone else None,
            "client_document": client.document if client else None,
            "order_number": req.order_number,
            "purchase_date": format_date(req.purchase_date),
            "purchase_channel": req.purchase_channel,
            "product_brand": product_brand,
            "product_model": product_model,
            "product_image": req.machine.image if req.machine.image != "" else "impresoras-varias1.webp",
            "original_price": float(req.original_price or 0),
            "paid_price": float(req.paid_price or 0),
            "new_price": float(req.new_price or 0),
            "price_difference": float(req.price_difference or 0),
            "credit_amount": float(req.credit_amount or 0),
            "credit_used": float(req.credit_used or 0),
            "credit_available": available,
            "assigned_user_id": req.assigned_user_id,
            "assigned_name": format_name(req.assigned.name) if req.assigned else None,
            "approved_by_name": format_name(req.approver.name) if req.approver else None,
            "approved_at": format_datetime(req.approved_at) if req.approved_at else None,
            "rejection_reason": req.rejection_reason,
            "created_at": format_datetime(req.created_at),
            "credit_usage": usage_list,
            "attachment_sections": attachment_sections,
            "chats": chats,
        }, 200
    

    @handle_exceptions
    def create_request(self):
        client_name_form = request.form.get("client_name")
        client_email = request.form.get("client_email") or None
        client_phone = request.form.get("client_phone") or None
        client_document = request.form.get("client_document") or None
        purchase_date = request.form.get("purchase_date")
        paid_price = request.form.get("paid_price")
        new_price = request.form.get("new_price")
        product_id = request.form.get("product") or None

        if not client_name_form:
            return "client_name requerido", 400
        if not purchase_date:
            return "purchase_date requerido", 400
        if not paid_price or not new_price:
            return "Precios requeridos", 400

        # Resolver cliente via documento
        client_id = None
        resolved_name = None
        if client_document:
            existing, ec = self.client_repository.get_client_by_document(client_document)
            if ec == 200:
                client_id = existing.id
                resolved_name = existing.name
                if client_email or client_phone:
                    self.client_repository.update_client_contact(existing, client_email, client_phone)
            else:
                doc_type = 'dni' if len(client_document) == 8 else 'ruc'
                name_result, nc = self.apiperu.get_name(doc_type, client_document)
                if nc == 200:
                    resolved_name = name_result.get("name")
                if resolved_name:
                    new_id, _ = self.client_repository.add_client_minimal(
                        document=client_document,
                        name=resolved_name,
                        email=client_email,
                        phone=client_phone,
                    )
                    client_id = new_id

        data = {
            "client_id": client_id,
            "order_number": request.form.get("order_number"),
            "purchase_date": purchase_date,
            "purchase_channel": request.form.get("purchase_channel", "web"),
            "machine_id": int(product_id) if product_id else None,
            "original_price": request.form.get("original_price"),
            "paid_price": paid_price,
            "new_price": new_price,
            "assigned_user_id": request.form.get("assigned_user_id"),
        }

        result, rc = self.repository.create_request(data)
        if rc != 200:
            return result, rc

        new_request_id = result["id"]

        receipt = request.files.get("receipt")
        if receipt and receipt.filename and allowed_extension(receipt.filename):
            self._save_attachment(new_request_id, receipt, "receipt")

        screenshots = request.files.getlist("screenshots[]")
        for file in screenshots:
            if not file or not file.filename:
                continue
            if not allowed_extension(file.filename):
                continue
            self._save_attachment(new_request_id, file, "screenshot")

        product_brand = product_model = None
        if product_id:
            machine, mc = self.machine_repository.get_machine_full(int(product_id))
            if mc == 200:
                product_brand = machine.brand.name
                product_model = machine.model

        socketio.emit("safebuy_update", {})
        return {
            "id": new_request_id,
            "client_name": resolved_name,
            "product_brand": product_brand,
            "product_model": product_model,
        }, 200


    def _save_attachment(self, request_id, file, target):
        original_name = file.filename
        ext = file_extension(original_name)
        safe = secure_filename(original_name) or f"file.{ext}"
        stored_name = f"{uuid.uuid4().hex}_{safe}"

        path = os.path.join(upload_path(Paths.SAFEBUY), stored_name)
        file.save(path)

        mime = getattr(file, "mimetype", None)
        size_bytes = os.path.getsize(path)

        self.repository.add_attachment(
            request_id=request_id,
            user_id=None,
            target=target,
            original_name=original_name,
            stored_name=stored_name,
            mime_type=mime,
            size_bytes=size_bytes,
        )


    @handle_exceptions
    def update_status(self, data):
        request_id = data.get("request_id")
        status_id = data.get("status_id")
        user_id = data.get("user_id")
        reason = data.get("rejection_reason")

        result, rc = self.repository.update_status(request_id, status_id, user_id, reason)
        if rc == 200:
            socketio.emit("safebuy_update", {})
        return result, rc

    @handle_exceptions
    def update_request(self, request_id, data):
        result, rc = self.repository.update_request(request_id, data)
        if rc == 200:
            socketio.emit("safebuy_update", {})
        return result, rc

    @handle_exceptions
    def apply_credit(self, data):
        result, rc = self.repository.apply_credit(data)
        if rc == 200:
            socketio.emit("safebuy_update", {})
        return result, rc

    @handle_exceptions
    def delete_request(self, request_id):
        result, rc = self.repository.soft_delete(request_id)
        if rc == 200:
            socketio.emit("safebuy_update", {})
        return result, rc

    # ── Attachments ──

    def attachments_upload(self):
        user_id = int(get_jwt_identity()) if get_jwt_identity() else None

        request_id = request.form.get("request_id")
        target = (request.form.get("target") or "default").strip()
        files = request.files.getlist("files[]")
        if not files:
            return {"data": {"message": "No files received"}}, 400

        max_bytes = Paths.MAX_BYTES
        saved_ids = []

        for f in files:
            if not f or not f.filename:
                continue

            if not allowed_extension(f.filename):
                return {"data": {"message": f"Tipo no permitido: {f.filename}"}}, 400

            f_size = None
            try:
                pos = f.stream.tell()
                f.stream.seek(0, os.SEEK_END)
                f_size = f.stream.tell()
                f.stream.seek(pos)
            except Exception:
                pass

            if f_size is not None and f_size > max_bytes:
                return {"data": {"message": f"Archivo muy grande: {f.filename}"}}, 400

            original_name = f.filename
            ext = file_extension(original_name)
            safe = secure_filename(original_name) or f"file.{ext}"
            stored_name = f"{uuid.uuid4().hex}_{safe}"

            path = os.path.join(upload_path(Paths.SAFEBUY), stored_name)
            f.save(path)

            mime = getattr(f, "mimetype", None)
            size_bytes = os.path.getsize(path)

            new_id, nc = self.repository.add_attachment(
                request_id=request_id,
                user_id=user_id,
                target=target,
                original_name=original_name,
                stored_name=stored_name,
                mime_type=mime,
                size_bytes=size_bytes,
            )
            if nc != 200:
                return new_id, nc

            saved_ids.append(new_id)

        socketio.emit("safebuy_update", {})
        return {"data": {"uploaded": saved_ids}}, 200

    def attachment_stream(self, attachment_id, disposition="inline"):
        row, rc = self.repository.get_attachment_by_id(int(attachment_id))
        if rc != 200:
            return row, rc

        path = os.path.join(Paths.SAFEBUY, row.stored_name)
        if not os.path.exists(path):
            return "File missing on disk", 404

        as_attachment = (disposition == "attachment")
        return send_file(
            path,
            mimetype=row.mime_type or "application/octet-stream",
            as_attachment=as_attachment,
            download_name=row.original_name,
        )

    def attachment_preview(self, attachment_id):
        row, rc = self.repository.get_attachment_by_id(int(attachment_id))
        if rc != 200:
            return row, rc

        ext = (row.original_name.rsplit(".", 1)[-1] if "." in row.original_name else "").lower()
        inline_url = f"/safebuy/attachment/{row.id}?disposition=inline"

        if ext in {"png", "jpg", "jpeg", "webp", "gif", "pdf"}:
            return {"kind": "url", "url": inline_url, "name": row.original_name}, 200

        return {
            "kind": "download",
            "name": row.original_name,
            "message": "Vista previa no disponible",
            "download_url": f"/safebuy/attachment/{row.id}?disposition=attachment",
        }, 200

    # ── Chat ──

    @handle_exceptions
    def chat(self, data):
        request_id = data.get("request_id")
        if not request_id:
            return "request_id requerido", 400

        comment = (data.get("comment") or "").strip()
        if not comment:
            return "Comentario vacío", 400

        current_user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(current_user_id)
        if uc != 200:
            return user, uc

        req, rc = self.repository.get_request_by_id(request_id)
        if rc != 200:
            return req, rc

        chat, cc = self.repository.add_chat(request_id=request_id, user_id=current_user_id, comment=comment)
        if cc != 200:
            return chat, cc

        participants, _ = self.repository.get_chat_participants(request_id=request_id, exclude_user_id=current_user_id)

        title = f"Nuevo mensaje, Compra Segura #{request_id}"
        body = f"{format_name(user.name, True)}: {comment}"

        registration_tokens, _ = self.push_service.prefetch_registration_tokens(participants)
        socketio.start_background_task(self.push_service.send_to_tokens, registration_tokens, title, body, {"url": f"/safebuy/{request_id}", "title": title})

        return {
            "id": chat.id,
            "comment": chat.comment,
            "commenter_id": chat.commenter_id,
            "commenter_name": format_name(chat.commenter.name),
            "commenter_image": chat.commenter.image,
            "created_at": format_datetime(chat.created_at),
        }, 200