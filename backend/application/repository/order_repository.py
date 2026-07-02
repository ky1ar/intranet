import logging
from datetime import datetime
from flask import g
from sqlalchemy import or_
from application.handlers import handle_db_exceptions
from application.utils import peru_time
from application.db_models.order_model import Order, OrderItem
from application.models import Clients, Users
from application.proxy.apiperu import ApiPeru


# Estados internos del tablero. El movimiento entre ellos es manual.
DASHBOARD_STATUSES = [
    {"slug": "registered",  "name": "Registrado"},
    {"slug": "in_process",  "name": "En proceso"},
    {"slug": "completed",   "name": "Completado"},
    {"slug": "discarded",   "name": "Descartado"},
]

# Transiciones permitidas desde cada estado.
STATUS_TRANSITIONS = {
    "registered": {"in_process"},
    "in_process": {"completed", "discarded"},
}


class OrderRepository:

    # ───────────────────────── Cliente ─────────────────────────
    def _clean_phone(self, phone):
        """Celular peruano válido: 9 dígitos que empiezan con 9 -> 51XXXXXXXXX.
        Cualquier otro caso se descarta (devuelve None)."""
        cleaned = (phone or "").strip()
        if len(cleaned) == 9 and cleaned.isdigit() and cleaned.startswith("9"):
            return f"51{cleaned}"
        return None

    def _resolve_name(self, document):
        """Nombre del titular vía API Perú (DNI 8 díg. / RUC 11 díg.). Cacheado en
        Redis por el proxy. Devuelve None si la consulta falla (no bloquea el pedido)."""
        doc = (document or "").strip()
        if not doc:
            return None
        try:
            doc_type = "ruc" if len(doc) == 11 else "dni"
            info, sc = ApiPeru().get_name(doc_type, doc)
            if sc == 200 and info and info.get("name"):
                return info["name"]
        except Exception:
            logging.exception("No se pudo resolver el nombre por documento %s", doc)
        return None

    def _wc_name(self, customer):
        first = (customer.get("first_name") or "").strip()
        last  = (customer.get("last_name") or "").strip()
        return f"{first} {last}".strip().title() or None

    @handle_db_exceptions
    def get_or_create_client(self, customer, address):
        """Busca por DNI/RUC. Si existe, solo actualiza correo y teléfono. Si no,
        lo crea con el nombre de API Perú y la dirección recibida."""
        document = (customer.get("dni_ruc") or "").strip()
        email    = (customer.get("email") or "").strip() or None
        phone    = self._clean_phone(customer.get("phone"))

        client = (
            g.db_session.query(Clients)
            .filter(Clients.document == document)
            .first()
        )

        if client:
            if email:
                client.email = email
            if phone:
                client.phone = phone
            g.db_session.commit()
        else:
            name = self._resolve_name(document) or self._wc_name(customer)
            client = Clients(
                document=document,
                name=name,
                email=email,
                phone=phone,
                address=address or "",
            )
            g.db_session.add(client)
            g.db_session.flush()
            g.db_session.commit()

        return client.id, 200

    def _resolve_seller(self, atencion):
        """El payload trae vendedor_id, que ya es el user.id de la intranet.
        Se valida que exista para no violar la FK con un id obsoleto."""
        vendedor_id = atencion.get("vendedor_id")
        if not vendedor_id:
            return None
        try:
            vendedor_id = int(vendedor_id)
        except (TypeError, ValueError):
            return None
        user = g.db_session.query(Users).filter(Users.id == vendedor_id).first()
        return user.id if user else None

    def _parse_date(self, value):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return None

    def _replace_items(self, order_id, items):
        g.db_session.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
        for it in items:
            g.db_session.add(OrderItem(
                order_id=order_id,
                product_id=it.get("product_id"),
                name=it.get("name"),
                quantity=it.get("quantity") or 1,
                total=it.get("total"),
            ))

    # ───────────────────────── Ingesta ─────────────────────────
    @handle_db_exceptions
    def upsert_order(self, payload):
        order    = payload.get("order") or {}
        customer = payload.get("customer") or {}
        address  = payload.get("address") or {}
        atencion = payload.get("atencion") or {}
        items    = payload.get("items") or []

        document = (customer.get("dni_ruc") or "").strip()
        if not document:
            return "El pedido no incluye DNI/RUC del cliente", 400

        wc_order_id = order.get("order_id")
        if not wc_order_id:
            return "El pedido no incluye order_id", 400

        full_address = " ".join(filter(None, [
            (address.get("address_1") or "").strip(),
            (address.get("address_2") or "").strip(),
        ]))

        client_id, sc = self.get_or_create_client(customer, full_address)
        if sc != 200:
            return client_id, sc

        seller_id = None
        if (atencion.get("ejecutivo_ayuda") or "").lower() == "si":
            seller_id = self._resolve_seller(atencion)

        existing = (
            g.db_session.query(Order)
            .filter(Order.wc_order_id == wc_order_id)
            .first()
        )

        if existing:
            # El pedido puede reenviarse (p.ej. cambio de método de pago). Actualizamos
            # los datos mutables y la lista de productos, pero NO el estado del tablero.
            existing.wc_status            = order.get("status")
            existing.total                = order.get("total")
            existing.currency             = order.get("currency")
            existing.payment_method       = order.get("payment_method")
            existing.payment_method_title = order.get("payment_method_title")
            if seller_id:
                existing.seller_id = seller_id
            self._replace_items(existing.id, items)
            g.db_session.commit()
            return {"id": existing.id, "updated": True}, 200

        new_order = Order(
            client_id=client_id,
            wc_order_id=wc_order_id,
            order_number=order.get("order_number"),
            status="registered",
            wc_status=order.get("status"),
            total=order.get("total"),
            currency=order.get("currency"),
            payment_method=order.get("payment_method"),
            payment_method_title=order.get("payment_method_title"),
            order_date=self._parse_date(order.get("date_created")),
            seller_id=seller_id,
            created_at=peru_time(),
        )
        g.db_session.add(new_order)
        g.db_session.flush()
        self._replace_items(new_order.id, items)
        g.db_session.commit()
        return {"id": new_order.id, "updated": False}, 200

    # ───────────────────────── Lectura ─────────────────────────
    @handle_db_exceptions
    def get_dashboard(self):
        orders = (
            g.db_session.query(Order)
            .order_by(Order.created_at.desc())
            .all()
        )
        return orders or [], 200

    @handle_db_exceptions
    def get_order_by_id(self, order_id):
        order = (
            g.db_session.query(Order)
            .filter(Order.id == order_id)
            .first()
        )
        if not order:
            return "Pedido no encontrado", 404
        return order, 200

    @handle_db_exceptions
    def search_orders(self, term, limit=20):
        like = f"%{term}%"
        orders = (
            g.db_session.query(Order)
            .join(Clients, Order.client_id == Clients.id)
            .filter(
                or_(
                    Clients.name.ilike(like),
                    Clients.document.ilike(like),
                    Order.order_number.ilike(like),
                )
            )
            .order_by(Order.created_at.desc())
            .limit(limit)
            .all()
        )
        return orders or [], 200

    @handle_db_exceptions
    def get_orders_paginated(self, page=1, per_page=12):
        query = (
            g.db_session.query(Order)
            .order_by(Order.created_at.desc())
        )
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return {
            "list": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }, 200

    # ───────────────────────── Estado ─────────────────────────
    @handle_db_exceptions
    def set_status(self, order_id, new_status, processed_by=None):
        order = (
            g.db_session.query(Order)
            .filter(Order.id == order_id)
            .first()
        )
        if not order:
            return "Pedido no encontrado", 404
        allowed = STATUS_TRANSITIONS.get(order.status, set())
        if new_status not in allowed:
            return "Transición de estado no permitida", 400
        order.status = new_status
        # Traza: registra quién pasó el pedido a "en proceso" (independiente del seller).
        if new_status == "in_process" and processed_by:
            order.processed_by = processed_by
            order.processed_at = peru_time()
        g.db_session.commit()
        return {"id": order.id, "status": order.status}, 200

    @handle_db_exceptions
    def set_wc_status(self, wc_order_id, wc_status):
        """Actualiza únicamente el estado de WooCommerce ('Estado web'). No toca el
        estado del tablero kanban, que se mueve manualmente."""
        order = (
            g.db_session.query(Order)
            .filter(Order.wc_order_id == wc_order_id)
            .first()
        )
        if not order:
            return "Pedido no encontrado", 404
        order.wc_status = wc_status
        g.db_session.commit()
        return {"id": order.id, "wc_status": order.wc_status}, 200
