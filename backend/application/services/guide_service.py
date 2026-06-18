import json
import logging
import os
from application.handlers import handle_exceptions
from application.repository.guide_repository import GuideRepository
from application.repository.approval_repository import ApprovalRepository
from application.services.push_service import PushSender
from application.services.module_service import ModuleService
from application.db_models.approval_model import ApprovalType
from config import Paths, Config
from flask import g


# Bundles JSON pre-construidos del Centro de aprendizaje (ver scripts/build_guides.py).
# Se elige uno según el tipo de máquina y la marca. Las imágenes usan el placeholder
# __GUIDE_BASE__, reemplazado por la base pública de uploads (/shared_uploads/guides).
_GUIDES_DATA_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "guides_data")
)
_WIKI_CACHE = {}


class GuideService:
    def __init__(self):
        self.repo           = GuideRepository()
        self.approval_repo  = ApprovalRepository()
        self.push_service   = PushSender()
        self.module_service = ModuleService()

    # ── WP-facing ────────────────────────────────────────────────────────────

    @handle_exceptions
    def create_request(self, data):
        # Upsert client
        client_id, sc = self.approval_repo.get_or_create_client(data)
        if sc != 200:
            return client_id, sc

        # Resolve 'guia' type_id
        type_obj = g.db_session.query(ApprovalType).filter(ApprovalType.slug == "guia").first()
        if not type_obj:
            return "Tipo 'guia' no configurado en la base de datos", 500

        result, sc = self.repo.create_guide_request(
            client_id, int(data["machine_id"]), type_obj.id, data.get("invoice_number")
        )
        if sc != 200:
            return result, sc

        if result.get("already_exists"):
            return {"message": "Ya tienes una solicitud activa para este equipo"}, 200
        self._notify_new_request(result["id"], type_obj.name)
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
    def get_my_guides(self, wp_user_id):
        rows, sc = self.repo.get_my_guides(wp_user_id)
        if sc != 200:
            return rows, sc
        result = []
        for row in rows:
            result.append({
                "approval_id":    row.approval_id,
                "machine_id":     row.machine_id,
                "machine_image":  row.machine_image,
                "brand_name":     row.brand_name,
                "brand_slug":     row.brand_slug,
                "machine_name":   row.full_name,
                "machine_type":   row.machine_type,
                "brand_image":   row.brand_image,
                "brand_scale":   row.brand_scale,
                "status":         row.status,
            })
        return result, 200

    @handle_exceptions
    def get_content(self, wp_user_id, machine_id):
        has_access, sc = self.repo.has_approved_access(wp_user_id, machine_id)
        if sc != 200:
            return has_access, sc
        if not has_access:
            return "Acceso no autorizado", 403

        guide, sc = self.repo.get_machine_guide(machine_id)
        if sc != 200:
            return guide, sc
        if not guide:
            return {"description": "", "items": []}, 200
        return {
            "description": guide.description or "",
            "items": guide.items or [],
        }, 200

    @handle_exceptions
    def get_wiki(self, wp_user_id, machine_id):
        has_access, sc = self.repo.has_approved_access(wp_user_id, machine_id)
        if sc != 200:
            return has_access, sc
        if not has_access:
            return "Acceso no autorizado", 403

        meta, sc = self.repo.get_machine_wiki_meta(machine_id)
        if sc != 200:
            return meta, sc
        if not meta:
            return "Equipo no encontrado", 404

        mtype = (meta.get("type") or "fdm").lower()
        slug  = (meta.get("brand_slug") or "").lower()
        if mtype == "lcd":
            key = "lcd"
        elif slug == "bambu-lab":
            key = "fdm_bambu"
        else:
            key = "fdm_other"

        return self._load_bundle(key)

    def _load_bundle(self, key):
        """Carga el bundle JSON pre-construido y resuelve la base de imágenes."""
        if key in _WIKI_CACHE:
            return _WIKI_CACHE[key], 200
        path = os.path.join(_GUIDES_DATA_DIR, f"{key}.json")
        if not os.path.isfile(path):
            logging.error("Bundle de guía no encontrado: %s", path)
            return "Contenido de guía no disponible", 404
        image_base = f"{(Config.BASE_URL or '').rstrip('/')}/guides"
        with open(path, encoding="utf-8") as fh:
            data = json.loads(fh.read().replace("__GUIDE_BASE__", image_base))
        _WIKI_CACHE[key] = data
        return data, 200

    def serve_media(self, filename, wp_user_id, machine_id):
        """Return (filepath, mimetype) after verifying access, or (None, error_msg)."""
        if not wp_user_id or not machine_id:
            return None, "Parámetros requeridos"
        has_access, sc = self.repo.has_approved_access(wp_user_id, machine_id)
        if sc != 200 or not has_access:
            return None, "Acceso no autorizado"
        filepath = os.path.join(Paths.GUIDES_MEDIA, filename)
        if not os.path.isfile(filepath):
            return None, "Archivo no encontrado"
        return filepath, None

    # ── Intranet-facing ──────────────────────────────────────────────────────

    @handle_exceptions
    def save_content(self, data):
        machine_id  = data.get("machine_id")
        description = data.get("description", "")
        items       = data.get("items", [])
        if not machine_id:
            return "machine_id requerido", 400
        result, sc = self.repo.save_machine_guide(int(machine_id), description, items)
        if sc != 200:
            return result, sc
        return {"message": "Guía guardada"}, 200

    @handle_exceptions
    def upload_media(self):
        filenames, sc = self.repo.upload_guide_media()
        if sc != 200:
            return filenames, sc
        return {"uploaded": filenames}, 200

    @handle_exceptions
    def list_guides(self):
        rows, sc = self.repo.list_machine_guides()
        if sc != 200:
            return rows, sc
        result = []
        for row in rows:
            guide = row[0]
            items = guide.items or []
            result.append({
                "machine_id":    row.machine_id,
                "machine_name":  row.full_name,
                "brand_name":    row.brand_name,
                "machine_image": row.machine_image,
                "item_count":    len(items),
            })
        return result, 200

    @handle_exceptions
    def delete_content(self, machine_id):
        return self.repo.delete_machine_guide(int(machine_id))

    @handle_exceptions
    def content_exists_for_request(self, approval_request_id):
        machine_id, sc = self.repo.get_machine_id_by_approval(approval_request_id)
        if sc != 200:
            return machine_id, sc
        if not machine_id:
            return False, 200
        return self.repo.has_content(machine_id)

    @handle_exceptions
    def get_content_admin(self, machine_id):
        guide, sc = self.repo.get_machine_guide(machine_id)
        if sc != 200:
            return guide, sc
        if not guide:
            return {"description": "", "items": []}, 200
        return {"description": guide.description or "", "items": guide.items or []}, 200

