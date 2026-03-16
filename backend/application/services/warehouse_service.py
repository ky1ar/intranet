from application.handlers import handle_exceptions
from application.repository.warehouse_repository import WarehouseRepository


class WarehouseService:
    def __init__(self):
        self.warehouse_repository = WarehouseRepository()

    def _location_label(self, block, level, position):
        return f"B{block}-{level}-{position}"

    def _serialize_row(self, row):
        return {
            "warehouse_stock_id": row.id,
            "id": row.id,
            "product_id": row.product.id,
            "brand": row.product.brand.name,
            "model": row.product.model,
            "image": row.product.image,
            "stock": row.stock,
            "category": getattr(row.product, "category", None) or "Impresoras 3D",
            "location": {
                "block": row.code.block,
                "level": row.code.level,
                "position": row.code.position,
                "label": self._location_label(
                    row.code.block,
                    row.code.level,
                    row.code.position
                ),
            }
        }

    @handle_exceptions
    def find_product(self, search):
        rows_products, rows_locations_products, rows_location_codes, pc = \
            self.warehouse_repository.get_products_like_split(search)

        if pc != 200:
            return rows_products, pc

        products = [self._serialize_row(r) for r in rows_products]

        # Pre-crear TODAS las ubicaciones encontradas, aunque tengan 0 items
        loc_map = {}
        for code in rows_location_codes:
            label = self._location_label(code.block, code.level, code.position)
            loc_map[label] = {
                "label": label,
                "block": code.block,
                "level": code.level,
                "position": code.position,
                "products": [],
                "products_count": 0,
                "preview_text": "Sin productos en esta ubicación",
            }

        # Llenar productos si existen
        for r in rows_locations_products:
            item = self._serialize_row(r)
            label = item["location"]["label"]

            if label not in loc_map:
                loc_map[label] = {
                    "label": label,
                    "block": item["location"]["block"],
                    "level": item["location"]["level"],
                    "position": item["location"]["position"],
                    "products": [],
                    "products_count": 0,
                    "preview_text": "Sin productos en esta ubicación",
                }

            loc_map[label]["products"].append(item)

        locations = []
        for loc in loc_map.values():
            loc["products"].sort(key=lambda x: (x.get("stock") or 0))
            loc["products_count"] = len(loc["products"])

            if loc["products_count"] > 0:
                top = sorted(
                    loc["products"],
                    key=lambda x: (x.get("stock") or 0),
                    reverse=True
                )[:3]

                loc["preview_text"] = " • ".join(
                    [f'{p["brand"]} {p["model"]}' for p in top]
                ) + (" …" if loc["products_count"] > 3 else "")

            locations.append(loc)

        locations.sort(key=lambda x: x["label"])

        return {"products": products, "locations": locations}, 200