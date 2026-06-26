import logging, os, re, uuid
from werkzeug.utils import secure_filename
from application.handlers import handle_exceptions
from application.utils import allowed_extension, file_extension, upload_path
from application.repository.machine_repository import MachineRepository
from config import Paths

IMAGE_BASE_URL = "/static/images/uploads/machines/"


class MachineService:
    def __init__(self):
        self.repository = MachineRepository()

    # ------------------------------------------------------------- helpers
    def _slugify(self, name):
        slug = re.sub(r"[^a-z0-9]+", "-", (name or "").strip().lower())
        return slug.strip("-")

    def _save_image(self, file):
        """Guarda la imagen en /shared_uploads/machines/ y devuelve (stored_name, error)."""
        if not file or not file.filename:
            return None, None
        if not allowed_extension(file.filename):
            return None, "Formato de imagen no permitido"

        try:
            pos = file.stream.tell()
            file.stream.seek(0, os.SEEK_END)
            file_size = file.stream.tell()
            file.stream.seek(pos)
        except Exception:
            file_size = None
        if file_size and file_size > Paths.MAX_BYTES:
            return None, "La imagen excede el tamaño máximo permitido"

        ext = file_extension(file.filename)
        safe = secure_filename(file.filename) or f"image.{ext}"
        stored_name = f"{uuid.uuid4().hex}_{safe}"
        file.save(os.path.join(upload_path(Paths.MACHINES), stored_name))
        return stored_name, None

    def _machine_dict(self, m):
        return {
            "id": m.id,
            "model": m.model,
            "type": m.type,
            "brand_id": m.brand_id,
            "brand_name": m.brand.name if m.brand else None,
            "category_id": m.category_id,
            "category_name": m.category.name if m.category else None,
            "image": m.image,
            "image_url": f"{IMAGE_BASE_URL}{m.image}" if m.image else None,
        }

    # ------------------------------------------------------------- machines
    @handle_exceptions
    def find_machines(self, machine_name):
        if len(machine_name) < 2:
            return None, 400

        machines, machines_status = self.repository.get_machines(machine_name)
        if machines_status != 200:
            return machines, machines_status

        machines_list = [
            {"id": machine.id, "name": machine.full_name, "image": machine.image}
            for machine in machines
        ]
        return machines_list, 200

    @handle_exceptions
    def list_machines(self, page=1, per_page=12, q=None, category_id=None, brand_id=None):
        result, code = self.repository.get_machines_paginated(page, per_page, q, category_id, brand_id)
        if code != 200:
            return result, code

        return {
            "list": [self._machine_dict(m) for m in result["list"]],
            "pagination": {
                "total": result["total"],
                "page": result["page"],
                "per_page": result["per_page"],
                "pages": result["pages"],
            },
        }, 200

    @handle_exceptions
    def get_machine_detail(self, machine_id):
        machine, code = self.repository.get_machine_full(machine_id)
        if code != 200:
            return "Máquina no encontrada", code
        return self._machine_dict(machine), 200

    @handle_exceptions
    def create_machine(self, data, file):
        model = (data.get("model") or "").strip()
        brand_id = data.get("brand_id")
        category_id = data.get("category_id")
        type_ = (data.get("type") or "").strip()

        if not model or not brand_id or not category_id or not type_:
            return "Faltan datos obligatorios", 400

        stored_name, error = self._save_image(file)
        if error:
            return error, 400
        if not stored_name:
            return "La imagen es obligatoria", 400

        machine_id, code = self.repository.create_machine({
            "brand_id": int(brand_id),
            "category_id": int(category_id),
            "model": model,
            "type": type_,
            "image": stored_name,
        })
        if code != 200:
            return machine_id, code
        return {"id": machine_id, "message": "Producto creado correctamente"}, 200

    @handle_exceptions
    def update_machine(self, machine_id, data, file):
        machine, code = self.repository.get_machine_full(machine_id)
        if code != 200:
            return "Máquina no encontrada", code

        payload = {}
        if data.get("model") is not None:
            model = data.get("model").strip()
            if not model:
                return "El nombre no puede estar vacío", 400
            payload["model"] = model
        if data.get("brand_id"):
            payload["brand_id"] = int(data["brand_id"])
        if data.get("category_id"):
            payload["category_id"] = int(data["category_id"])
        if data.get("type") is not None:
            payload["type"] = data.get("type").strip()

        # Imagen opcional: si llega una nueva, solo se actualiza la ruta.
        # NUNCA se borra el archivo anterior del disco.
        stored_name, error = self._save_image(file)
        if error:
            return error, 400
        if stored_name:
            payload["image"] = stored_name

        if not payload:
            return "No hay cambios para guardar", 400

        ok, code = self.repository.update_machine(machine, payload)
        if code != 200:
            return ok, code
        return "Producto actualizado correctamente", 200

    # ----------------------------------------------------------- categories
    @handle_exceptions
    def list_categories(self):
        categories, code = self.repository.list_categories()
        if code != 200:
            return categories, code
        return [{"id": c.id, "name": c.name, "slug": c.slug} for c in categories], 200

    @handle_exceptions
    def create_category(self, data):
        name = (data.get("name") or "").strip()
        if not name:
            return "El nombre es obligatorio", 400
        category_id, code = self.repository.create_category(name, self._slugify(name))
        if code != 200:
            return category_id, code
        return {"id": category_id, "message": "Categoría creada"}, 200

    @handle_exceptions
    def update_category(self, category_id, data):
        name = (data.get("name") or "").strip()
        if not name:
            return "El nombre es obligatorio", 400
        category, code = self.repository.get_category(category_id)
        if code != 200:
            return "Categoría no encontrada", code
        ok, code = self.repository.update_category(category, name, self._slugify(name))
        if code != 200:
            return ok, code
        return "Categoría actualizada", 200

    # --------------------------------------------------------------- brands
    @handle_exceptions
    def list_brands(self):
        brands, code = self.repository.list_brands()
        if code != 200:
            return brands, code
        return [{"id": b.id, "name": b.name, "slug": b.slug} for b in brands], 200

    @handle_exceptions
    def create_brand(self, data):
        name = (data.get("name") or "").strip()
        if not name:
            return "El nombre es obligatorio", 400
        brand_id, code = self.repository.create_brand(name, self._slugify(name))
        if code != 200:
            return brand_id, code
        return {"id": brand_id, "message": "Marca creada"}, 200

    @handle_exceptions
    def update_brand(self, brand_id, data):
        name = (data.get("name") or "").strip()
        if not name:
            return "El nombre es obligatorio", 400
        brand, code = self.repository.get_brand(brand_id)
        if code != 200:
            return "Marca no encontrada", code
        ok, code = self.repository.update_brand(brand, name, self._slugify(name))
        if code != 200:
            return ok, code
        return "Marca actualizada", 200
