import logging
from application import socketio
from application.handlers import handle_exceptions
from application.utils import format_datetime, format_name
from application.repository.order_repository import OrderRepository, DASHBOARD_STATUSES
from application.services.push_service import PushSender
from application.services.module_service import ModuleService


class OrderService:
    def __init__(self):
        self.repository = OrderRepository()
        self.push_service = PushSender()
        self.module_service = ModuleService()

    # ── Ingesta del webhook de WordPress/WooCommerce ──
    @handle_exceptions
    def ingest_wc_order(self, payload):
        if not payload:
            return "Payload vacío", 400
        result, sc = self.repository.upsert_order(payload)
        if sc != 200:
            return result, sc
        if not result.get("updated"):
            self._notify_new_order(result["id"])
        socketio.emit("order_update", {})
        return {"message": "Pedido registrado", "id": result["id"]}, 200

    def _notify_new_order(self, order_id):
        """Push a quienes tengan el permiso 'notify' del módulo de pedidos."""
        try:
            user_ids, _ = self.module_service.get_user_ids_with_permission("orders", "notify")
            if not user_ids:
                return

            # Cuerpo enriquecido: número de pedido y cliente (con fallback)
            body = f"WC-{order_id}"
            order, sc = self.repository.get_order_by_id(order_id)
            if sc == 200 and order is not None:
                number = order.order_number or order.wc_order_id or order_id
                parts = [f"WC-{number}"]
                if order.client and order.client.name:
                    parts.append(format_name(order.client.name))
                body = "  ·  ".join(parts)

            self.push_service.send_to_users(
                user_ids=user_ids,
                title="Nuevo pedido registrado",
                body=body,
                data={"url": f"/orders/{order_id}", "title": "Nuevo pedido"},
            )
        except Exception:
            logging.exception("Error notificando nuevo pedido WC-%s", order_id)

    # ── Tablero ──
    @handle_exceptions
    def dashboard(self):
        orders, sc = self.repository.get_dashboard()
        if sc != 200:
            return orders, sc
        grouped = {
            g["slug"]: {"status_slug": g["slug"], "status_name": g["name"], "orders": []}
            for g in DASHBOARD_STATUSES
        }
        # Las columnas terminales (completado / descartado) pueden acumular cientos,
        # así que se topan a 20. Registrado y en proceso se muestran completas.
        for order in orders:
            st = order.status if order.status in grouped else "registered"
            if st in ("completed", "discarded") and len(grouped[st]["orders"]) >= 20:
                continue
            grouped[st]["orders"].append(self._format_order(order))
        return [grouped[g["slug"]] for g in DASHBOARD_STATUSES], 200

    @handle_exceptions
    def get_order_detail(self, order_id):
        order, sc = self.repository.get_order_by_id(order_id)
        if sc != 200:
            return order, sc
        return self._format_order(order, with_items=True), 200

    @handle_exceptions
    def search_orders(self, term):
        term = (term or "").strip()
        if len(term) < 2:
            return [], 200
        orders, sc = self.repository.search_orders(term)
        if sc != 200:
            return orders, sc
        return [self._format_order(o) for o in orders], 200

    @handle_exceptions
    def history(self, data):
        page     = data.get("page", 1)
        per_page = data.get("per_page", 12)
        result, sc = self.repository.get_orders_paginated(page, per_page)
        if sc != 200:
            return result, sc
        return {
            "list": [self._format_order(o) for o in result["list"]],
            "pagination": {
                "total":    result["total"],
                "page":     result["page"],
                "per_page": result["per_page"],
                "pages":    result["pages"],
            },
        }, 200

    @handle_exceptions
    def change_status(self, data):
        result, sc = self.repository.set_status(data.get("order_id"), data.get("status"))
        if sc != 200:
            return result, sc
        socketio.emit("order_update", {})
        return {"message": "Estado actualizado", "status": result["status"]}, 200

    # ── Serialización ──
    def _format_order(self, order, with_items=False):
        client = order.client
        data = {
            "id": order.id,
            "wc_order_id": order.wc_order_id,
            "order_number": order.order_number,
            "status": order.status,
            "wc_status": order.wc_status,
            "total": float(order.total) if order.total is not None else None,
            "currency": order.currency,
            "payment_method": order.payment_method,
            "payment_method_title": order.payment_method_title,
            "order_date": format_datetime(order.order_date) if order.order_date else None,
            "client_id": order.client_id,
            "client_name": client.name if client else None,
            "client_dni": client.document if client else None,
            "client_email": client.email if client else None,
            "client_phone": client.phone if client else None,
            "client_address": client.address if client else None,
            "seller_id": order.seller_id,
            "seller_name": format_name(order.seller.name) if order.seller else None,
            "seller_email": order.seller.email if order.seller else None,
            "created_at": format_datetime(order.created_at),
        }
        if with_items:
            data["items"] = [
                {
                    "id": it.id,
                    "product_id": it.product_id,
                    "name": it.name,
                    "quantity": it.quantity,
                    "total": float(it.total) if it.total is not None else None,
                }
                for it in sorted(order.items, key=lambda x: x.id)
            ]
        return data
