import re
from application.handlers import handle_db_exceptions
from application.db_models.warehouse_model import WarehouseCodes, WarehouseStock
from application.models import Brands, Machines
from sqlalchemy import or_, func, cast, String
from flask import g


class WarehouseRepository:
    def _build_location_filter(self, search_norm):
        block_match = re.match(r"^[A-Z](\d+)", search_norm)
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
        # B1-1-2 => prefijo B1-1-2%
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
            # 1) TODAS las ubicaciones que coincidan, aunque no tengan productos
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

            # 2) Productos con stock dentro de esas ubicaciones
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