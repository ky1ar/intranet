import xmlrpc.client, re, logging, base64
from config import Odoo

# Compilado una sola vez (antes se recompilaba en cada llamada a extract_pe_mobile)
_PE_MOBILE_RE = re.compile(
    r"(?<!\d)"                       # not preceded by a digit
    r"(?:\+?51[\s\-()./]*?)?"        # optional country code
    r"(9(?:[\s\-()./]*\d){8})"       # 9 + 8 digits, with optional separators
    r"(?!\d)"                        # not followed by a digit
)


class OdooClient:
    def __init__(self):
        # Cache de sesión: evita reautenticar y reabrir proxies en cada método.
        self._uid = None
        self._models = None

    def _auth(self):
        if self._uid and self._models is not None:
            return self._uid, self._models

        common = xmlrpc.client.ServerProxy(f"{Odoo.URL}/xmlrpc/2/common")
        uid = common.authenticate(Odoo.DB, Odoo.USER, Odoo.API_KEY, {})
        if not uid:
            raise RuntimeError("No autenticó con Odoo.")

        self._uid = uid
        self._models = xmlrpc.client.ServerProxy(f"{Odoo.URL}/xmlrpc/2/object")
        return self._uid, self._models

    def _exec(self, model, method, args, kw=None):
        """Wrapper de execute_kw. Reautentica y reintenta UNA vez ante caída de
        conexión. Seguro porque todos los métodos de esta clase son de lectura;
        si agregas create/write, no reintentes operaciones no idempotentes."""
        kw = kw or {}
        try:
            uid, models = self._auth()
            return models.execute_kw(Odoo.DB, uid, Odoo.API_KEY, model, method, args, kw)
        except (xmlrpc.client.ProtocolError, OSError) as e:
            logging.warning("Odoo conexión falló (%s); reautenticando y reintentando.", e)
            self._uid = None
            self._models = None
            uid, models = self._auth()
            return models.execute_kw(Odoo.DB, uid, Odoo.API_KEY, model, method, args, kw)

    def _exec_write(self, model, method, args, kw=None):
        """Igual que _exec PERO SIN reintento automático.
        Úsalo para create/write/unlink y cualquier método NO idempotente.
        NO reintenta: si la conexión cae después de que Odoo ya hizo commit,
        un reintento ciego duplicaría el registro o reaplicaría el cambio.
        Si la 1ra llamada falla por conexión, deja que el error suba y maneja
        el reintento a nivel de negocio (verificando antes si ya se creó)."""
        kw = kw or {}
        uid, models = self._auth()
        return models.execute_kw(Odoo.DB, uid, Odoo.API_KEY, model, method, args, kw)

    def get_invoice_pdf_bytes(self, invoice_id: int) -> bytes | None:
        inv = self._exec(
            "account.move", "read",
            [[invoice_id]],
            {"fields": ["message_main_attachment_id", "name"]},
        )
        inv = inv[0] if inv else {}

        att_id = None
        mma = inv.get("message_main_attachment_id")
        if isinstance(mma, list) and mma:
            att_id = mma[0]

        if att_id:
            # Adjunto principal conocido: lo leemos directo.
            recs = self._exec(
                "ir.attachment", "read",
                [[att_id]],
                {"fields": ["id", "name", "mimetype", "datas"]},
            )
        else:
            # search + read fusionados en un solo round-trip con search_read.
            # OJO: no pidas datas_fname (da KeyError). Usa "name" y "datas".
            recs = self._exec(
                "ir.attachment", "search_read",
                [[
                    ("res_model", "=", "account.move"),
                    ("res_id", "=", invoice_id),
                    ("mimetype", "=", "application/pdf"),
                ]],
                {"fields": ["id", "name", "mimetype", "datas"],
                 "order": "id desc", "limit": 1},
            )
            if not recs:
                logging.info("Attachments for invoice_id=%s => []", invoice_id)
                return None

        if not recs:
            return None

        b64 = recs[0].get("datas")
        if not b64:
            return None

        return base64.b64decode(b64)

    def extract_pe_mobile(self, raw=None):
        if not raw:
            return None

        text = str(raw).strip()
        if not text:
            return None

        logging.info(f"raw: {text}")

        matches = list(_PE_MOBILE_RE.finditer(text))
        if not matches:
            logging.info("No PE mobile match found.")
            return None

        candidate = matches[-1].group(1)
        phone9 = re.sub(r"\D", "", candidate)

        logging.info(f"candidate: {candidate} -> phone9: {phone9}")

        if len(phone9) == 9 and phone9.startswith("9"):
            return phone9

        return None

    def list_validated_last(self, limit=50):
        domain = [
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("name", "!=", "/"),
        ]
        fields = ["id", "name", "partner_id", "invoice_date", "create_date", "write_date"]
        return self._exec(
            "account.move", "search_read",
            [domain],
            {"fields": fields, "order": "write_date desc, id desc", "limit": limit},
        )

    def list_validated_since(self, last_write_date, last_id, limit=200):
        base = [
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("name", "!=", "/"),
        ]
        domain = base + [
            "|",
                ("write_date", ">", last_write_date),
                "&",
                    ("write_date", "=", last_write_date),
                    ("id", ">", last_id),
        ]
        fields = ["id", "name", "partner_id", "invoice_date", "create_date", "write_date"]
        return self._exec(
            "account.move", "search_read",
            [domain],
            {"fields": fields, "order": "write_date asc, id asc", "limit": limit},
        )

    def get_partner_phone(self, partner_id):
        recs = self._exec(
            "res.partner", "read",
            [[partner_id]],
            {"fields": ["phone", "mobile"]},
        )
        if not recs:
            return None

        p = recs[0]
        raw = p.get("mobile") or p.get("phone")
        phone9 = self.extract_pe_mobile(raw)

        if not phone9:
            logging.info("Partner %s phone invalid/unmatched. raw=%s", partner_id, raw)
            return None

        return phone9

    def _split_serie_correlative(self, raw):
        """Devuelve (serie, correlativo_int) si el texto tiene forma SERIE-NUMERO, si no None."""
        m = re.match(r"^\s*([A-Za-z0-9]+)\s*-\s*(\d+)\s*$", raw or "")
        if not m:
            return None
        return m.group(1).upper(), int(m.group(2))

    def get_invoice_by_name(self, invoice_number):
        """Busca un comprobante (boleta/factura) por su número y devuelve el detalle del pedido."""
        invoice_number = (invoice_number or "").strip()
        if not invoice_number:
            return None

        move_types = ["out_invoice", "out_refund"]
        fields_move = [
            "name", "partner_id", "invoice_date", "invoice_origin",
            "state", "payment_state",
            "amount_untaxed", "amount_tax", "amount_total", "currency_id",
        ]

        parsed = self._split_serie_correlative(invoice_number)
        if parsed:
            serie, correlative = parsed
            padded = f"{serie}-{str(correlative).zfill(8)}"
            domain = [("name", "=ilike", f"%{padded}"), ("move_type", "in", move_types)]
        else:
            domain = [("name", "ilike", invoice_number), ("move_type", "in", move_types)]

        moves = self._exec(
            "account.move", "search_read",
            [domain],
            {"fields": fields_move, "order": "id desc", "limit": 1},
        )
        if not moves:
            return None

        move = moves[0]
        move_id = move["id"]  # search_read siempre incluye 'id'

        def _name(rel):
            return rel[1] if isinstance(rel, list) and len(rel) >= 2 else None

        # Líneas: un solo search_read en vez de search + read.
        line_recs = self._exec(
            "account.move.line", "search_read",
            [[("move_id", "=", move_id), ("product_id", "!=", False)]],
            {"fields": ["product_id", "name", "quantity", "price_unit", "price_subtotal", "price_total"],
             "order": "id asc"},
        )

        lines = []
        for ln in line_recs:
            lines.append({
                "product": _name(ln.get("product_id")) or (ln.get("name") or "").split("\n")[0],
                "description": ln.get("name") or None,
                "quantity": ln.get("quantity") or 0,
                "price_unit": ln.get("price_unit") or 0,
                "price_subtotal": ln.get("price_subtotal") or 0,
                "price_total": ln.get("price_total") or 0,
            })

        return {
            "found": True,
            "id": move_id,
            "name": move.get("name"),
            "partner_name": _name(move.get("partner_id")),
            "invoice_date": move.get("invoice_date") or None,
            "invoice_origin": move.get("invoice_origin") or None,
            "state": move.get("state") or None,
            "payment_state": move.get("payment_state") or None,
            "amount_untaxed": move.get("amount_untaxed") or 0,
            "amount_tax": move.get("amount_tax") or 0,
            "amount_total": move.get("amount_total") or 0,
            "currency": _name(move.get("currency_id")),
            "lines": lines,
        }