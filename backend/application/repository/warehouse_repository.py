import re, logging
from application.handlers import handle_db_exceptions
from application.db_models.warehouse_model import WarehouseCodes, WarehouseStock, WarehouseLog
from application.models import Brands, Machines, Category
from sqlalchemy import or_, func, cast, String, not_, exists
from flask import g


class WarehouseRepository:
    def _build_location_filter(self, search_norm):
        block_match = re.match(r"^B(\d+)(.*)", search_norm)
        if not block_match:
            return False, None

        block_number = int(block_match.group(1))
        rest = block_match.group(2)  # e.g. "" | "-" | "-01" | "-01-A"

        normalized_search = f"B{block_number}"
        if rest and rest.startswith("-") and len(rest) > 1:
            rest_parts = rest[1:].split("-")
            norm_parts = []
            for i, part in enumerate(rest_parts):
                if i == 0 and re.match(r"^\d+$", part):  # componente level
                    norm_parts.append(str(int(part)))
                else:
                    norm_parts.append(part)
            normalized_search = f"B{block_number}-" + "-".join(norm_parts)

        location_label = func.concat(
            "B",
            cast(WarehouseCodes.block, String),
            "-",
            cast(WarehouseCodes.level, String),
            "-",
            cast(WarehouseCodes.position, String)
        )

        # Sin guión o sólo "B1-" → todo el bloque
        if "-" not in normalized_search or normalized_search.endswith("-"):
            location_filter = (WarehouseCodes.block == block_number)
        else:
            location_filter = location_label.ilike(f"{normalized_search}%")

        return True, location_filter
    

    @handle_db_exceptions
    def get_products_like_split(self, search):
        search = (search or "").strip()
        if not search:
            return [], [], [], 200

        search_term = f"%{search}%"
        search_norm = re.sub(r"\s+", "", search).upper()

        base_products = (
            g.db_session.query(WarehouseStock)
            .join(WarehouseStock.product)
            .join(Machines.brand)
            .join(WarehouseStock.code)
            .filter(WarehouseStock.stock > 0)
        )

        name_filter = or_(
            Brands.name.ilike(search_term),
            Machines.model.ilike(search_term),
            func.concat(Brands.name, " ", Machines.model).ilike(search_term),
        )

        rows_products = (
            base_products
            .filter(name_filter)
            .order_by(Brands.name.asc(), Machines.model.asc())
            .all()
        )

        rows_locations_products = []
        rows_location_codes = []

        is_location_query, location_filter = self._build_location_filter(search_norm)

        if is_location_query:
            rows_location_codes = (
                g.db_session.query(WarehouseCodes)
                .filter(location_filter)
                .order_by(
                    WarehouseCodes.block.asc(),
                    WarehouseCodes.level.asc(),
                    WarehouseCodes.position.asc()
                )
                .all()
            )

            rows_locations_products = (
                base_products
                .filter(location_filter)
                .order_by(
                    WarehouseCodes.block.asc(),
                    WarehouseCodes.level.asc(),
                    WarehouseCodes.position.asc(),
                    Brands.name.asc(),
                    Machines.model.asc()
                )
                .all()
            )

        return rows_products, rows_locations_products, rows_location_codes, 200


    @handle_db_exceptions
    def get_location_detail(self, label):
        label_norm = re.sub(r"\s+", "", (label or "")).upper()

        match = re.match(r"^B(\d+)-(\d+)-([A-Z0-9])$", label_norm)
        if not match:
            return {"message": "Formato de ubicación inválido"}, [], 400

        block, level, position = match.groups()

        code = (
            g.db_session.query(WarehouseCodes)
            .filter(
                WarehouseCodes.block == int(block),
                WarehouseCodes.level == int(level),
                func.upper(WarehouseCodes.position) == position
            )
            .first()
        )

        if not code:
            return {"message": "Ubicación no encontrada"}, [], 404

        rows = (
            g.db_session.query(WarehouseStock)
            .join(WarehouseStock.product)
            .join(Machines.brand)
            .join(WarehouseStock.code)
            .filter(
                WarehouseStock.code_id == code.id,
                WarehouseStock.stock > 0
            )
            .order_by(
                Brands.name.asc(),
                Machines.model.asc()
            )
            .all()
        )

        return code, rows, 200


    @handle_db_exceptions
    def remove_stock(self, warehouse_stock_id, quantity):
        stock_row = (
            g.db_session.query(WarehouseStock)
            .join(WarehouseStock.code)
            .filter(WarehouseStock.id == warehouse_stock_id)
            .with_for_update()
            .first()
        )

        if not stock_row:
            return "Registro de stock no encontrado", 404

        if quantity < 1:
            return "La cantidad debe ser mayor a 0", 400

        if stock_row.stock < quantity:
            return "La cantidad excede el stock disponible", 400

        stock_row.stock = stock_row.stock - quantity
        g.db_session.commit()

        code = stock_row.code
        label = f"B{code.block}-{code.level}-{code.position}"

        return {
            "warehouse_stock_id": stock_row.id,
            "product_id":         stock_row.product_id,
            "product_name":       f"{stock_row.product.brand.name} {stock_row.product.model}",
            "stock":              stock_row.stock,
            "label":              label,
            "code_id":            stock_row.code_id,
        }, 200


    @handle_db_exceptions
    def load_excel_rows(self, rows):
        def slugify(text):
            return re.sub(r'[\s]+', '-', text.lower().strip())

        stats = {
            "processed": 0,
            "skipped":   0,
            "errors":    [],
            "created_brands":     [],
            "created_categories": [],
            "created_machines":   [],
        }

        for row in rows:
            rack_raw = row["rack"]
            nivel    = row["nivel"]
            marca    = row["marca"]
            producto = row["producto"]
            modelo   = row["modelo"]
            qty      = row["qty"]

            # RACK: quitar cero a la izquierda → entero
            try:
                rack_int = int(rack_raw.lstrip("0") or "0")
            except ValueError:
                stats["errors"].append(f"RACK inválido: '{rack_raw}' | modelo: {modelo}")
                stats["skipped"] += 1
                continue

            # ── MARCA → brands ─────────────────────────────────────────────────
            brand = (
                g.db_session.query(Brands)
                .filter(func.lower(Brands.name) == marca.lower())
                .first()
            )
            if not brand:
                brand = Brands(name=marca.title(), slug=slugify(marca))
                g.db_session.add(brand)
                g.db_session.flush()
                stats["created_brands"].append(brand.name)

            # ── PRODUCTO → category ────────────────────────────────────────────
            category = (
                g.db_session.query(Category)
                .filter(func.lower(Category.name) == producto.lower())
                .first()
            )
            if not category:
                category = Category(name=producto.title(), slug=slugify(producto))
                g.db_session.add(category)
                g.db_session.flush()
                stats["created_categories"].append(category.name)

            # ── MODELO → machines ──────────────────────────────────────────────
            machine = (
                g.db_session.query(Machines)
                .filter(
                    func.lower(Machines.model) == modelo.lower(),
                    Machines.brand_id == brand.id,
                )
                .first()
            )
            if not machine:
                machine = Machines(
                    brand_id=brand.id,
                    category_id=category.id,
                    model=modelo.title().strip(),
                    image="",          # columna NOT NULL; sin imagen por ahora
                )
                g.db_session.add(machine)
                g.db_session.flush()
                stats["created_machines"].append(machine.model)

            # ── warehouse_codes: level=RACK, position=NIVEL ────────────────────
            code = (
                g.db_session.query(WarehouseCodes)
                .filter(
                    WarehouseCodes.level    == rack_int,
                    func.upper(WarehouseCodes.position) == nivel,
                )
                .first()
            )
            if not code:
                logging.warning(
                    f"[load_excel] warehouse_code no encontrado → "
                    f"level={rack_int}, position={nivel} | modelo: {modelo}"
                )
                stats["errors"].append(
                    f"Ubicación no encontrada: rack={rack_int}, nivel={nivel} | {marca} {modelo}"
                )
                stats["skipped"] += 1
                continue

            # ── warehouse_stock: upsert ────────────────────────────────────────
            stock_row = (
                g.db_session.query(WarehouseStock)
                .filter(
                    WarehouseStock.code_id    == code.id,
                    WarehouseStock.product_id == machine.id,
                )
                .first()
            )
            if stock_row:
                stock_row.stock = qty
            else:
                stock_row = WarehouseStock(
                    code_id=code.id,
                    product_id=machine.id,
                    stock=qty,
                )
                g.db_session.add(stock_row)

            stats["processed"] += 1

        g.db_session.commit()
        return stats, 200


    @handle_db_exceptions
    def get_occupied_locations(self):
        codes = (
            g.db_session.query(WarehouseCodes)
            .filter(
                exists().where(
                    (WarehouseStock.code_id == WarehouseCodes.id) &
                    (WarehouseStock.stock > 0)
                )
            )
            .all()
        )
        return [f"B{c.block}-{c.level}-{c.position}" for c in codes], 200


    @handle_db_exceptions
    def get_total_stock_for_product(self, product_id):
        total = (
            g.db_session.query(func.sum(WarehouseStock.stock))
            .filter(
                WarehouseStock.product_id == product_id,
                WarehouseStock.stock > 0,
            )
            .scalar()
        ) or 0
        return total, 200


    def resolve_product_id(self, warehouse_stock_id):
        try:
            row = g.db_session.query(WarehouseStock).filter_by(id=warehouse_stock_id).first()
            return row.product_id if row else None
        except Exception:
            return None


    @handle_db_exceptions
    def save_log(self, action, product_id=None, user_id=None, quantity=None, from_code_id=None, to_code_id=None):
        log = WarehouseLog(
            action=action,
            product_id=product_id,
            user_id=user_id,
            quantity=quantity,
            from_code_id=from_code_id,
            to_code_id=to_code_id,
        )
        g.db_session.add(log)
        g.db_session.commit()
        return True, 200


    @handle_db_exceptions
    def get_available_locations(self):

        codes = (
            g.db_session.query(WarehouseCodes)
            .filter(
                ~exists().where(
                    (WarehouseStock.code_id == WarehouseCodes.id) &
                    (WarehouseStock.stock > 0)
                )
            )
            .order_by(
                WarehouseCodes.block.asc(),
                WarehouseCodes.level.asc(),
                WarehouseCodes.position.asc(),
            )
            .all()
        )
        return codes, 200


    @handle_db_exceptions
    def search_machines(self, query):
        query = (query or "").strip()
        if len(query) < 2:
            return [], 200

        search_term = f"%{query}%"
        machines = (
            g.db_session.query(Machines)
            .join(Machines.brand)
            .filter(
                or_(
                    Brands.name.ilike(search_term),
                    Machines.model.ilike(search_term),
                    func.concat(Brands.name, " ", Machines.model).ilike(search_term),
                )
            )
            .order_by(Brands.name.asc(), Machines.model.asc())
            .limit(10)
            .all()
        )
        return [
            {
                "id": m.id,
                "brand": m.brand.name,
                "model": m.model,
                "image": m.image if m.image != "" else "impresoras-varias1.webp",
            }
            for m in machines
        ], 200


    @handle_db_exceptions
    def add_stock(self, product_id, location_label, quantity):
        label_norm = re.sub(r"\s+", "", (location_label or "")).upper()
        match = re.match(r"^B(\d+)-(\d+)-([A-Z0-9])$", label_norm)
        if not match:
            return {"message": "Formato de ubicación inválido"}, 400

        block, level, position = match.groups()

        code = (
            g.db_session.query(WarehouseCodes)
            .filter(
                WarehouseCodes.block == int(block),
                WarehouseCodes.level == int(level),
                func.upper(WarehouseCodes.position) == position,
            )
            .first()
        )
        if not code:
            return {"message": "Ubicación no encontrada"}, 404

        stock_row = (
            g.db_session.query(WarehouseStock)
            .filter(
                WarehouseStock.code_id    == code.id,
                WarehouseStock.product_id == product_id,
            )
            .with_for_update()
            .first()
        )

        if stock_row:
            stock_row.stock += quantity
        else:
            stock_row = WarehouseStock(
                code_id=code.id,
                product_id=product_id,
                stock=quantity,
            )
            g.db_session.add(stock_row)

        g.db_session.commit()
        return {"label": label_norm, "code_id": code.id}, 200


    @handle_db_exceptions
    def move_stock(self, warehouse_stock_id, quantity, destination_label):
        dest_norm = re.sub(r"\s+", "", (destination_label or "")).upper()
        match = re.match(r"^B(\d+)-(\d+)-([A-Z0-9])$", dest_norm)
        if not match:
            return {"message": "Formato de ubicación destino inválido"}, 400

        src_row = (
            g.db_session.query(WarehouseStock)
            .join(WarehouseStock.code)
            .filter(WarehouseStock.id == warehouse_stock_id)
            .with_for_update()
            .first()
        )
        if not src_row:
            return {"message": "Registro de stock origen no encontrado"}, 404

        if src_row.stock < quantity:
            return {"message": "La cantidad supera el stock disponible"}, 400

        block, level, position = match.groups()
        dest_code = (
            g.db_session.query(WarehouseCodes)
            .filter(
                WarehouseCodes.block == int(block),
                WarehouseCodes.level == int(level),
                func.upper(WarehouseCodes.position) == position,
            )
            .first()
        )
        if not dest_code:
            return {"message": "Ubicación destino no encontrada"}, 404

        if dest_code.id == src_row.code_id:
            return {"message": "El origen y destino son la misma ubicación"}, 400

        dest_row = (
            g.db_session.query(WarehouseStock)
            .filter(
                WarehouseStock.code_id    == dest_code.id,
                WarehouseStock.product_id == src_row.product_id,
            )
            .with_for_update()
            .first()
        )

        src_row.stock -= quantity

        if dest_row:
            dest_row.stock += quantity
        else:
            dest_row = WarehouseStock(
                code_id=dest_code.id,
                product_id=src_row.product_id,
                stock=quantity,
            )
            g.db_session.add(dest_row)

        source_code = src_row.code
        source_label = f"B{source_code.block}-{source_code.level}-{source_code.position}"

        g.db_session.commit()
        return {
            "source_label":   source_label,
            "dest_label":     dest_norm,
            "from_code_id":   source_code.id,
            "to_code_id":     dest_code.id,
        }, 200