import os, secrets
from werkzeug.utils import secure_filename
from flask import request, g
from sqlalchemy import func

from application.handlers import handle_db_exceptions
from application.utils import upload_path, file_extension, allowed_extension, peru_time
from application.models import Machines, Brands
from application.db_models.approval_model import ApprovalRequest
from application.db_models.guide_model import MachineGuide
from application.models import Clients
from config import Paths


class GuideRepository:

    # ── Request creation ────────────────────────────────────────────────────

    @handle_db_exceptions
    def create_guide_request(self, client_id, machine_id, type_id, invoice_number=None):
        existing = (
            g.db_session.query(ApprovalRequest)
            .filter(
                ApprovalRequest.client_id == client_id,
                ApprovalRequest.type_id == type_id,
                ApprovalRequest.machine_id == machine_id,
                ApprovalRequest.status.in_(["pending", "in_review", "approved"]),
            )
            .first()
        )
        if existing:
            return {"id": existing.id, "already_exists": True}, 200

        voucher_filename = self._save_voucher()

        approval = ApprovalRequest(
            client_id=client_id,
            type_id=type_id,
            status="pending",
            invoice_number=invoice_number,
            machine_id=machine_id,
            voucher_filename=voucher_filename,
        )
        g.db_session.add(approval)
        g.db_session.commit()
        return {"id": approval.id, "already_exists": False}, 200

    def _save_voucher(self):
        voucher = request.files.get("voucher")
        if not voucher or not voucher.filename:
            return None
        if not allowed_extension(voucher.filename):
            return None
        ext = file_extension(voucher.filename)
        filename = f"{secrets.token_hex(16)}.{ext}"
        path = os.path.join(upload_path(Paths.APPROVAL_VOUCHERS), filename)
        voucher.save(path)
        return filename

    # ── Status / listing ────────────────────────────────────────────────────

    @handle_db_exceptions
    def get_my_guides(self, wp_user_id):
        brand_image = func.concat(Brands.slug, '.', Brands.file).label("brand_image")

        rows = (
            g.db_session.query(
                ApprovalRequest.status,
                ApprovalRequest.id.label("approval_id"),
                Machines.id.label("machine_id"),
                Machines.image.label("machine_image"),
                Brands.name.label("brand_name"),
                Brands.scale.label("brand_scale"),
                Machines.model.label("full_name"),
                brand_image,
            )
            .join(Clients, ApprovalRequest.client_id == Clients.id)
            .join(Machines, ApprovalRequest.machine_id == Machines.id)
            .join(Brands, Machines.brand_id == Brands.id)
            .filter(
                Clients.wp_user_id == wp_user_id,
                ApprovalRequest.status.in_(["pending", "in_review", "approved"]),
            )
            .all()
        )
        return rows, 200

    @handle_db_exceptions
    def get_client_by_wp_user_id(self, wp_user_id):
        client = (
            g.db_session.query(Clients)
            .filter(Clients.wp_user_id == wp_user_id)
            .first()
        )
        return client, 200

    @handle_db_exceptions
    def has_approved_access(self, wp_user_id, machine_id):
        row = (
            g.db_session.query(ApprovalRequest)
            .join(Clients, ApprovalRequest.client_id == Clients.id)
            .filter(
                Clients.wp_user_id == wp_user_id,
                ApprovalRequest.machine_id == machine_id,
                ApprovalRequest.status == "approved",
            )
            .first()
        )
        return row is not None, 200

    # ── Guide content ────────────────────────────────────────────────────────

    @handle_db_exceptions
    def list_machine_guides(self):
        full_name = func.concat(Brands.name, ' ', Machines.model).label("full_name")
        rows = (
            g.db_session.query(
                MachineGuide,
                Machines.id.label("machine_id"),
                Machines.image.label("machine_image"),
                Brands.name.label("brand_name"),
                full_name,
            )
            .join(Machines, MachineGuide.machine_id == Machines.id)
            .join(Brands, Machines.brand_id == Brands.id)
            .order_by(MachineGuide.id.desc())
            .all()
        )
        return rows or [], 200

    @handle_db_exceptions
    def delete_machine_guide(self, machine_id):
        guide = (
            g.db_session.query(MachineGuide)
            .filter(MachineGuide.machine_id == machine_id)
            .first()
        )
        if not guide:
            return "Guía no encontrada", 404
        g.db_session.delete(guide)
        g.db_session.commit()
        return {"deleted": True}, 200

    @handle_db_exceptions
    def has_content(self, machine_id):
        guide = (
            g.db_session.query(MachineGuide)
            .filter(MachineGuide.machine_id == machine_id)
            .first()
        )
        return bool(guide and guide.items), 200

    @handle_db_exceptions
    def get_machine_id_by_approval(self, approval_request_id):
        ar = (
            g.db_session.query(ApprovalRequest)
            .filter(ApprovalRequest.id == approval_request_id)
            .first()
        )
        return (ar.machine_id if ar else None), 200

    @handle_db_exceptions
    def get_machine_guide(self, machine_id):
        guide = (
            g.db_session.query(MachineGuide)
            .filter(MachineGuide.machine_id == machine_id)
            .first()
        )
        return guide, 200

    @handle_db_exceptions
    def save_machine_guide(self, machine_id, description, items):
        guide = (
            g.db_session.query(MachineGuide)
            .filter(MachineGuide.machine_id == machine_id)
            .first()
        )
        if guide:
            guide.description = description
            guide.items = items
        else:
            guide = MachineGuide(
                machine_id=machine_id,
                description=description,
                items=items,
            )
            g.db_session.add(guide)
        g.db_session.commit()
        return {"id": guide.id}, 200

    # ── Media upload for guide content ───────────────────────────────────────

    @handle_db_exceptions
    def upload_guide_media(self):
        files = request.files.getlist("files[]")
        if not files:
            return "No files", 400
        saved = []
        for f in files:
            if not f or not f.filename:
                continue
            if not allowed_extension(f.filename):
                continue
            ext = file_extension(f.filename)
            filename = f"{secrets.token_hex(16)}.{ext}"
            path = os.path.join(upload_path(Paths.GUIDES_MEDIA), filename)
            f.save(path)
            saved.append(filename)
        return saved, 200
