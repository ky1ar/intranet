import io, re, openpyxl
from application.handlers import handle_exceptions
from application.repository.warehouse_repository import WarehouseRepository
from application.services.push_service import PushSender
from application.repository.user_repository import UserRepository
from flask_jwt_extended import get_jwt_identity
from application.utils import format_name
from application.services.odoo_service import OdooService


class WarehouseService:
    def __init__(self):
        self.warehouse_repository = WarehouseRepository()
        self.push_service         = PushSender()
        self.user_repository      = UserRepository()
        self.odoo_service         = OdooService()


    def _current_user_id(self):
        try:
            return int(get_jwt_identity())
        except Exception:
            return None
        
        
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
    def get_logs(self, page=1):
        return self.warehouse_repository.get_logs(page=page)

    @handle_exceptions
    def statistics(self):
        units, _      = self.warehouse_repository.stats_total_units()
        occupied, _   = self.warehouse_repository.stats_occupied_locations()
        total_loc, _  = self.warehouse_repository.stats_total_locations()
        out_month, _  = self.warehouse_repository.stats_out_month()
        stock_rows, _ = self.warehouse_repository.stats_top_stock_products()
        removed_rows, _ = self.warehouse_repository.stats_top_removed_products()
        user_rows, _  = self.warehouse_repository.stats_by_user()

        occupancy = round((occupied / total_loc) * 100) if total_loc else 0

        by_stock   = [{"product": name, "stock": int(v or 0)} for name, v in stock_rows]
        by_removed = [{"product": name, "qty": int(v or 0)} for name, v in removed_rows]
        by_user    = [{"user": format_name(name, True), "count": c} for name, c in user_rows]

        return {
            "count": {
                "units": units,
                "occupied": occupied,
                "occupancy": occupancy,
                "out_month": out_month,
            },
            "by_stock": by_stock,
            "by_removed": by_removed,
            "by_user": by_user,
        }, 200


    @handle_exceptions
    def get_occupied_locations(self):
        labels, rc = self.warehouse_repository.get_occupied_locations()
        if rc != 200:
            return labels, rc
        return {"locations": labels}, 200

        
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


    def _picking_allocation(self, rows, needed):
        """Reparte la cantidad necesaria entre ubicaciones, consumiendo primero
        las de menor stock. Devuelve (allocations, remaining)."""
        allocations = []
        remaining = needed
        for row in rows:
            if remaining <= 0:
                break
            take = min(remaining, row.stock)
            if take <= 0:
                continue
            allocations.append({
                "warehouse_stock_id": row.id,
                "take": take,
                "stock": row.stock,
                "location": {
                    "block": row.code.block,
                    "level": row.code.level,
                    "position": row.code.position,
                    "label": self._location_label(
                        row.code.block, row.code.level, row.code.position
                    ),
                },
            })
            remaining -= take
        return allocations, remaining


    # Productos de Odoo que no son artículos físicos de almacén → se omiten.
    # Cualquier nombre que contenga "envío" también se omite (ver _is_ignored_product).
    IGNORED_PRODUCT_NAMES = {
        "ready to pick",
        "productos entregados en el evento creality",
        "descuento",
        "compra en tienda",
        "recojo (almacén)",
        "recojo (tienda)",
        "servicio de mantenimiento correctivo",
    }

    def _is_ignored_product(self, name):
        name = (name or "").strip().lower()
        return "envío" in name or name in self.IGNORED_PRODUCT_NAMES

    def _resolve_machine_id(self, line):
        """Determina el id de máquina de una línea de pedido.
        1) usa barcode si es numérico.
        2) si no, toma el id entre corchetes al inicio del nombre. El corchete
           empieza con "ID" seguido del número; puede traer más datos tras un
           espacio, que se ignoran. Ej:
           - "[ID608] ..."           -> toma 608
           - "[ID608 AR123RV] ..."   -> toma 608."""
        barcode = line.get("barcode")
        if barcode is not None and str(barcode).strip().isdigit():
            return int(str(barcode).strip())
        for field in ("product", "description"):
            match = re.match(r"^\s*\[\s*ID(\d+)", line.get(field) or "", re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None


    @handle_exceptions
    def build_picking_plan(self, order_number):
        order, rc = self.odoo_service.get_sale_order_detail(order_number)
        if rc != 200:
            return order, rc
        if not isinstance(order, dict) or not order.get("found"):
            return {"found": False}, 200

        order_name = order.get("name")
        picked_map, _ = self.warehouse_repository.get_picked_quantities_for_order(order_name)

        items = []
        for line in order.get("lines", []):
            barcode = line.get("barcode")
            raw_name = (line.get("product") or line.get("description") or "").strip()
            if self._is_ignored_product(raw_name):
                continue
            try:
                needed = int(round(float(line.get("quantity") or 0)))
            except (TypeError, ValueError):
                needed = 0
            fallback_name = line.get("product") or line.get("description") or "Producto"

            item = {
                "barcode": barcode,
                "description": fallback_name,
                "quantity": needed,
                "qty_delivered": line.get("qty_delivered") or 0,
                "found": False,
                "available": False,
                "status": "no_barcode",
                "message": "Sin código",
                "product_id": None,
                "brand": None,
                "model": None,
                "category": None,
                "image": "impresoras-varias1.webp",
                "allocations": [],
                "allocated": 0,
                "shortage": needed,
                "total_stock": 0,
                "already_picked": 0,
                "pending": needed,
            }

            product_id = self._resolve_machine_id(line)

            if product_id is None:
                items.append(item)
                continue

            machine, _ = self.warehouse_repository.get_machine(product_id)
            if not machine:
                item["status"] = "not_found"
                item["message"] = "No encontrado"
                items.append(item)
                continue

            item["found"]      = True
            item["product_id"] = product_id
            item["brand"]      = machine.brand.name if machine.brand else None
            item["model"]      = machine.model
            item["category"]   = machine.category.name if machine.category else None
            item["image"]      = machine.image if machine.image != "" else "impresoras-varias1.webp"

            already = int(picked_map.get(product_id, 0) or 0)
            pending = needed - already
            if pending < 0:
                pending = 0
            item["already_picked"] = already
            item["pending"]        = pending
            item["shortage"]       = pending

            if needed <= 0:
                item["status"]    = "ok"
                item["available"] = True
                item["message"]   = "Sin cantidad solicitada"
                item["shortage"]  = 0
                items.append(item)
                continue

            # Pedido ya recogido por completo para este producto.
            if pending <= 0:
                item["status"]   = "done"
                item["message"]  = "Ya pickeado"
                item["shortage"] = 0
                items.append(item)
                continue

            rows, _ = self.warehouse_repository.get_stock_locations_for_product(product_id)
            total_stock = sum(r.stock for r in rows)
            item["total_stock"] = total_stock

            if total_stock <= 0:
                item["status"]  = "no_stock"
                item["message"] = "Sin stock en almacén"
                items.append(item)
                continue

            # Sólo se reparte la cantidad restante (pendiente) del pedido.
            allocations, remaining = self._picking_allocation(rows, pending)
            item["allocations"] = allocations
            item["allocated"]   = pending - remaining
            item["shortage"]    = remaining
            item["available"]   = item["allocated"] > 0

            if remaining <= 0:
                item["status"]  = "ok"
                item["message"] = f"Restante: {pending} ud." if already > 0 else "Disponible para picking"
            else:
                item["status"]  = "partial"
                item["message"] = f"Stock insuficiente: faltan {remaining} ud."

            items.append(item)

        # ── Orden de ruta de picking ─────────────────────────────────────
        # El número de rack (level) es secuencial por el almacén (1..55),
        # así que ordenar por (level, position, block) genera una ruta de
        # una sola vuelta. Los ítems sin ubicación quedan al final.
        def _loc_key(loc):
            return (int(loc.get("level") or 0), str(loc.get("position") or ""), int(loc.get("block") or 0))

        for it in items:
            it["allocations"].sort(key=lambda a: _loc_key(a["location"]))

        def _route_key(it):
            allocs = it.get("allocations") or []
            if not allocs:
                return (1, 9999, "Z", 9999)
            return (0,) + min(_loc_key(a["location"]) for a in allocs)

        items.sort(key=_route_key)

        pending_items = sum(1 for it in items if it.get("found") and (it.get("pending") or 0) > 0)
        picked_items  = sum(1 for it in items if it.get("found") and it.get("status") == "done")
        fully_picked  = pending_items == 0 and picked_items > 0

        return {
            "found": True,
            "fully_picked": fully_picked,
            "pending_items": pending_items,
            "order": {
                "id":             order.get("id"),
                "name":           order.get("name"),
                "partner_name":   order.get("partner_name"),
                "date_order":     order.get("date_order"),
                "state":          order.get("state"),
                "invoice_status": order.get("invoice_status"),
                "amount_total":   order.get("amount_total"),
                "currency":       order.get("currency"),
            },
            "items": items,
        }, 200


    @handle_exceptions
    def complete_picking(self, data):
        order_name = (data or {}).get("order")
        picks      = (data or {}).get("picks") or []

        if not isinstance(picks, list) or not picks:
            return {"message": "No hay ítems para completar"}, 400

        user_id = self._current_user_id()
        results = []
        errors  = []
        total_units = 0

        for pick in picks:
            try:
                wsid     = int(pick.get("warehouse_stock_id"))
                quantity = int(pick.get("quantity"))
            except (TypeError, ValueError):
                errors.append({"warehouse_stock_id": pick.get("warehouse_stock_id"), "message": "Datos inválidos"})
                continue

            if quantity < 1:
                continue

            removed, rc = self.warehouse_repository.remove_stock(warehouse_stock_id=wsid, quantity=quantity)
            if rc != 200:
                errors.append({"warehouse_stock_id": wsid, "message": removed})
                continue

            product_id = removed.get("product_id")
            self.warehouse_repository.save_log(
                action="pick",
                product_id=product_id,
                user_id=user_id,
                quantity=quantity,
                order_ref=order_name,
                from_code_id=removed.get("code_id"),
            )

            total_units += quantity
            results.append({
                "warehouse_stock_id": wsid,
                "product_id":         product_id,
                "quantity":           quantity,
                "label":              removed.get("label"),
                "remaining_stock":    removed.get("stock"),
            })

            # Aviso de stock bajo (igual que en el retiro individual)
            if product_id:
                total, _ = self.warehouse_repository.get_total_stock_for_product(product_id)
                if total < 3:
                    user_ids, _ = self.user_repository.get_all_user_ids()
                    self.push_service.send_to_users(
                        user_ids=user_ids,
                        title="⚠️ Stock bajo en almacén",
                        body=f"{removed.get('product_name', 'Producto')} tiene {total} ud{'s' if total != 1 else ''} en total.",
                    )

        if not results and errors:
            return {"message": "No se pudo completar el picking", "errors": errors}, 400

        return {
            "message": "Picking completado",
            "order": order_name,
            "picked": results,
            "units": total_units,
            "errors": errors,
        }, 200


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
            quantity           = int(quantity)
        except (TypeError, ValueError):
            return "Datos inválidos", 400

        if quantity < 1:
            return "La cantidad a retirar debe ser mayor a 0", 400

        removed_data, rc = self.warehouse_repository.remove_stock(warehouse_stock_id=warehouse_stock_id, quantity=quantity)
        if rc != 200:
            return removed_data, rc

        user_id    = self._current_user_id()
        from_label = removed_data["label"]
        product_id = removed_data.get("product_id") or self.warehouse_repository.resolve_product_id(warehouse_stock_id)

        # ── Traza ──────────────────────────────────────────────────────────────
        self.warehouse_repository.save_log(
            action="pick",
            product_id=product_id,
            user_id=user_id,
            quantity=quantity,
            from_code_id=removed_data.get("code_id"),
        )

        if product_id:
            total, _ = self.warehouse_repository.get_total_stock_for_product(product_id)
            if total < 3:
                user_ids, _ = self.user_repository.get_all_user_ids()
                product_name = removed_data.get("product_name", "Producto")
                self.push_service.send_to_users(
                    user_ids=user_ids,
                    title="⚠️ Stock bajo en almacén",
                    body=f"{product_name} tiene {total} ud{'s' if total != 1 else ''} en total.",
                    # data={"action": "warehouse_low_stock", "product_id": str(product_id)},
                )

        code, rows, rc = self.warehouse_repository.get_location_detail(from_label)
        if rc != 200:
            return code, rc

        return {
            "message": "Stock retirado correctamente",
            "location": self._serialize_location(code, rows),
        }, 200


    @handle_exceptions
    def load_excel(self, file_bytes):
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), read_only=True, data_only=True)
        ws = wb.active

        headers = [str(cell.value).strip().upper() if cell.value else "" for cell in next(ws.iter_rows(max_row=1))]

        required = {"PISO", "RACK", "NIVEL", "MARCA", "PRODUCTO", "MODELO", "Q CONTADA"}
        if not required.issubset(set(headers)):
            return f"El Excel no tiene las columnas requeridas: {required - set(headers)}", 400

        idx = {h: i for i, h in enumerate(headers)}

        rows = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            piso     = row[idx["PISO"]]
            rack     = row[idx["RACK"]]
            nivel    = row[idx["NIVEL"]]
            marca    = row[idx["MARCA"]]
            producto = row[idx["PRODUCTO"]]
            modelo   = row[idx["MODELO"]]
            qty      = row[idx["Q CONTADA"]]

            if any(v is None for v in [rack, nivel, marca, producto, modelo, qty]):
                continue

            rows.append({
                "piso":     int(piso),
                "rack":     str(rack).strip(),
                "nivel":    str(nivel).strip().upper(),
                "marca":    str(marca).strip(),
                "producto": str(producto).strip(),
                "modelo":   str(modelo).strip(),
                "qty":      int(qty),
            })

        self.warehouse_repository.save_log(
            action="load",
            user_id=self._current_user_id(),
            quantity=len(rows),
        )
                
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

        self.warehouse_repository.save_log(
            action="add",
            product_id=product_id,
            user_id=self._current_user_id(),
            quantity=quantity,
            to_code_id=result.get("code_id"),
        )
                
        return {
            "message": "Stock añadido correctamente",
            "location": self._serialize_location(code, rows)
        }, 200


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

        self.warehouse_repository.save_log(
            action="move",
            product_id=self.warehouse_repository.resolve_product_id(warehouse_stock_id),
            user_id=self._current_user_id(),
            quantity=quantity,
            from_code_id=result.get("from_code_id"),
            to_code_id=result.get("to_code_id"),
        )
                
        return {
            "message": "Stock movido correctamente",
            "location": self._serialize_location(code, rows),
        }, 200