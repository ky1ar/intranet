import re
from application.handlers import handle_db_exceptions
from application.db_models.warehouse_model import WarehouseCodes, WarehouseStock
from application.models import Brands, Machines
from sqlalchemy import or_, func, cast, String
from flask import g


class WarehouseRepository:
    @handle_db_exceptions
    def get_products_like_split(self, search):
        search = (search or "").strip()
        if not search:
            return [], [], 200

        search_term = f"%{search}%"
        search_norm = re.sub(r"\s+", "", search).upper()

        base = (
            g.db_session.query(WarehouseStock)
            .join(WarehouseStock.product)
            .join(Machines.brand)
            .join(WarehouseStock.code)
            .filter(WarehouseStock.stock > 0)
        )

        # ✅ SOLO nombre (marca/modelo) para "products"
        name_filter = or_(
            Brands.name.ilike(search_term),
            Machines.model.ilike(search_term),
            func.concat(Brands.name, " ", Machines.model).ilike(search_term),
        )

        # Detecta intención de ubicación: B1, B1-, B1-1, etc.
        is_location_query = bool(re.match(r"^[A-Z]\d+", search_norm))

        rows_products = (
            base.filter(name_filter)
            .order_by(Brands.name.asc(), Machines.model.asc())
            .all()
        )

        rows_locations = []
        if is_location_query:
            location_label = func.concat(
                WarehouseCodes.block, "-",
                cast(WarehouseCodes.level, String), "-",
                cast(WarehouseCodes.position, String)
            )

            # ✅ Lógica de ubicación:
            # - "B1"     => bloque exacto B1 (no B10)
            # - "B1-"    => bloque B1 completo
            # - "B1-1"   => prefijo "B1-1%"
            # - "B1-1-A" => prefijo "B1-1-A%"
            if "-" in search_norm:
                if search_norm.endswith("-"):
                    block_part = search_norm.split("-")[0]  # "B1-"" => "B1"
                    location_filter = (func.upper(WarehouseCodes.block) == block_part)
                else:
                    location_filter = location_label.ilike(f"{search_norm}%")
            else:
                location_filter = (func.upper(WarehouseCodes.block) == search_norm)

            rows_locations = (
                base.filter(location_filter)
                .order_by(
                    WarehouseCodes.block.asc(),
                    WarehouseCodes.level.asc(),
                    WarehouseCodes.position.asc()
                )
                .all()
            )

        return rows_products, rows_locations, 200