import io, openpyxl
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
            "image": row.product.image if row.product.image != "" else "impresoras-varias1.webp",
            "stock": row.stock,
            "category": row.product.category.name,
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


    def _serialize_location(self, code, rows):
        location = {
            "label": self._location_label(code.block, code.level, code.position),
            "block": code.block,
            "level": code.level,
            "position": code.position,
            "products": [],
            "products_count": 0,
            "preview_text": "Sin productos en esta ubicación",
        }

        for r in rows:
            location["products"].append(self._serialize_row(r))

        location["products"].sort(key=lambda x: (x.get("stock") or 0))
        location["products_count"] = len(location["products"])

        if location["products_count"] > 0:
            top = sorted(
                location["products"],
                key=lambda x: (x.get("stock") or 0),
                reverse=True
            )[:3]

            location["preview_text"] = " • ".join(
                [f'{p["brand"]} {p["model"]}' for p in top]
            ) + (" …" if location["products_count"] > 3 else "")

        return location

    @handle_exceptions
    def find_product(self, search):
        # Keyword especial: ubicaciones disponibles (sin stock)
        if (search or "").strip().lower() in ("disponible"):
            codes, rc = self.warehouse_repository.get_available_locations()
            if rc != 200:
                return codes, rc

            locations = []
            for code in codes:
                locations.append({
                    "id": code.id,
                    "label": self._location_label(code.block, code.level, code.position),
                    "block": code.block,
                    "level": code.level,
                    "position": code.position,
                    "products": [],
                    "products_count": 0,
                    "preview_text": "Disponible",
                })
            return {"products": [], "locations": locations}, 200

        rows_products, rows_locations_products, rows_location_codes, pc = \
            self.warehouse_repository.get_products_like_split(search)

        if pc != 200:
            return rows_products, pc

        products = [self._serialize_row(r) for r in rows_products]

        loc_map = {}
        for code in rows_location_codes:
            label = self._location_label(code.block, code.level, code.position)
            loc_map[label] = {
                "id": code.id,
                "label": label,
                "block": code.block,
                "level": code.level,
                "position": code.position,
                "products": [],
                "products_count": 0,
                "preview_text": "Sin productos en esta ubicación",
            }

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

        locations.sort(key=lambda x: (
            int(x.get("block") or 0),
            int(x.get("level") or 0),
            str(x.get("position") or "")
        ))

        return {"products": products, "locations": locations}, 200


    @handle_exceptions
    def get_location(self, label):
        code, rows, rc = self.warehouse_repository.get_location_detail(label)
        if rc != 200:
            return code, rc

        location = self._serialize_location(code, rows)
        return {"location": location}, 200


    @handle_exceptions
    def remove_stock(self, data):
        warehouse_stock_id = data.get("warehouse_stock_id")
        quantity = data.get("quantity")

        try:
            warehouse_stock_id = int(warehouse_stock_id)
            quantity = int(quantity)
        except (TypeError, ValueError):
            return {"message": "Datos inválidos"}, 400

        if quantity < 1:
            return {"message": "La cantidad a retirar debe ser mayor a 0"}, 400

        removed_data, rc = self.warehouse_repository.remove_stock(
            warehouse_stock_id=warehouse_stock_id,
            quantity=quantity
        )
        if rc != 200:
            return removed_data, rc

        code, rows, rc = self.warehouse_repository.get_location_detail(removed_data["label"])
        if rc != 200:
            return code, rc

        location = self._serialize_location(code, rows)

        return {
            "message": "Stock retirado correctamente",
            "location": location
        }, 200


    @handle_exceptions
    def load_excel(self, file_bytes):
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), read_only=True, data_only=True)
        ws = wb.active

        headers = [str(cell.value).strip().upper() if cell.value else "" for cell in next(ws.iter_rows(max_row=1))]

        required = {"RACK", "NIVEL", "MARCA", "PRODUCTO", "MODELO", "Q CONTADA"}
        if not required.issubset(set(headers)):
            return f"El Excel no tiene las columnas requeridas: {required - set(headers)}", 400

        idx = {h: i for i, h in enumerate(headers)}

        rows = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            rack     = row[idx["RACK"]]
            nivel    = row[idx["NIVEL"]]
            marca    = row[idx["MARCA"]]
            producto = row[idx["PRODUCTO"]]
            modelo   = row[idx["MODELO"]]
            qty      = row[idx["Q CONTADA"]]

            if any(v is None for v in [rack, nivel, marca, producto, modelo, qty]):
                continue

            rows.append({
                "rack":     str(rack).strip(),
                "nivel":    str(nivel).strip().upper(),
                "marca":    str(marca).strip(),
                "producto": str(producto).strip(),
                "modelo":   str(modelo).strip(),
                "qty":      int(qty),
            })

        return self.warehouse_repository.load_excel_rows(rows)


    @handle_exceptions
    def search_machines(self, query):
        machines, rc = self.warehouse_repository.search_machines(query)
        if rc != 200:
            return machines, rc
        return machines, 200


    @handle_exceptions
    def add_stock(self, data):
        product_id     = data.get("product_id")
        location_label = data.get("location_label")
        quantity       = data.get("quantity")

        try:
            product_id = int(product_id)
            quantity   = int(quantity)
        except (TypeError, ValueError):
            return {"message": "Datos inválidos"}, 400

        if quantity < 1:
            return {"message": "La cantidad debe ser mayor a 0"}, 400

        result, rc = self.warehouse_repository.add_stock(
            product_id=product_id,
            location_label=location_label,
            quantity=quantity,
        )
        if rc != 200:
            return result, rc

        code, rows, rc = self.warehouse_repository.get_location_detail(result["label"])
        if rc != 200:
            return code, rc

        return {"message": "Stock añadido correctamente", "location": self._serialize_location(code, rows)}, 200


    @handle_exceptions
    def move_stock(self, data):
        warehouse_stock_id = data.get("warehouse_stock_id")
        quantity           = data.get("quantity")
        destination_label  = data.get("destination_label")

        try:
            warehouse_stock_id = int(warehouse_stock_id)
            quantity           = int(quantity)
        except (TypeError, ValueError):
            return "Datos inválidos", 400

        if quantity < 1:
            return "La cantidad debe ser mayor a 0", 400

        result, rc = self.warehouse_repository.move_stock(
            warehouse_stock_id=warehouse_stock_id,
            quantity=quantity,
            destination_label=destination_label,
        )
        if rc != 200:
            return result, rc

        code, rows, rc = self.warehouse_repository.get_location_detail(result["source_label"])
        if rc != 200:
            return code, rc

        return {
            "message": "Stock movido correctamente",
            "location": self._serialize_location(code, rows),
        }, 200