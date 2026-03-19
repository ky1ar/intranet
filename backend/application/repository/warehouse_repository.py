import re
from application.handlers import handle_db_exceptions
from application.db_models.warehouse_model import WarehouseCodes, WarehouseStock
from application.models import Brands, Machines
from sqlalchemy import or_, func, cast, String
from flask import g


class WarehouseRepository:
    def _build_location_filter(self, search_norm):
        block_match = re.match(r"^[B](\d+)", search_norm)
        is_location_query = bool(block_match)
        block_number = int(block_match.group(1)) if block_match else None

        if not is_location_query:
            return False, None

        location_label = func.concat(
            "B",
            cast(WarehouseCodes.block, String),
            "-",
            cast(WarehouseCodes.level, String),
            "-",
            cast(WarehouseCodes.position, String)
        )

        # B1     => todo el bloque 1
        # B1-    => todo el bloque 1
        # B1-1   => prefijo B1-1%
        # B1-1-C => exacto / prefijo según búsqueda
        if "-" in search_norm:
            if search_norm.endswith("-"):
                location_filter = (WarehouseCodes.block == block_number)
            else:
                location_filter = location_label.ilike(f"{search_norm}%")
        else:
            location_filter = (WarehouseCodes.block == block_number)

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
            return {"message": "Registro de stock no encontrado"}, 404

        if quantity < 1:
            return {"message": "La cantidad debe ser mayor a 0"}, 400

        if stock_row.stock < quantity:
            return {"message": "La cantidad excede el stock disponible"}, 400

        stock_row.stock = stock_row.stock - quantity
        g.db_session.commit()

        code = stock_row.code
        label = f"B{code.block}-{code.level}-{code.position}"

        return {
            "warehouse_stock_id": stock_row.id,
            "stock": stock_row.stock,
            "label": label
        }, 200