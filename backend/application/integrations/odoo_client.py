import xmlrpc.client, re, logging, base64
from config import Odoo

class OdooClient:
    def _auth(self):
        common = xmlrpc.client.ServerProxy(f"{Odoo.URL}/xmlrpc/2/common")
        uid = common.authenticate(Odoo.DB, Odoo.USER, Odoo.API_KEY, {})
        if not uid:
            raise RuntimeError("No autenticó con Odoo.")
        models = xmlrpc.client.ServerProxy(f"{Odoo.URL}/xmlrpc/2/object")
        return uid, models


    def get_invoice_pdf_bytes(self, invoice_id: int) -> bytes | None:
        uid, models = self._auth()

        inv = models.execute_kw(
            Odoo.DB, uid, Odoo.API_KEY,
            "account.move", "read",
            [[invoice_id]],
            {"fields": ["message_main_attachment_id", "name"]}
        )
        inv = inv[0] if inv else {}
        att_id = None

        mma = inv.get("message_main_attachment_id")
        if isinstance(mma, list) and mma:
            att_id = mma[0]

        if not att_id:
            # Buscar attachments PDF ligados al invoice
            att_ids = models.execute_kw(
                Odoo.DB, uid, Odoo.API_KEY,
                "ir.attachment", "search",
                [[
                    ("res_model", "=", "account.move"),
                    ("res_id", "=", invoice_id),
                    ("mimetype", "=", "application/pdf"),
                ]],
                {"order": "id desc", "limit": 1},
            )
            att_id = att_ids[0] if att_ids else None

        if not att_id:
            logging.info("Attachments for invoice_id=%s => []", invoice_id)
            return None

        # 👇 OJO: no pidas datas_fname (te dio KeyError). Usa "name" y "datas".
        recs = models.execute_kw(
            Odoo.DB, uid, Odoo.API_KEY,
            "ir.attachment", "read",
            [[att_id]],
            {"fields": ["id", "name", "mimetype", "datas"]},
        )
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

        pattern = re.compile(
            r"(?<!\d)"                       # not preceded by a digit
            r"(?:\+?51[\s\-()./]*?)?"        # optional country code
            r"(9(?:[\s\-()./]*\d){8})"       # 9 + 8 digits, with optional separators
            r"(?!\d)"                        # not followed by a digit
        )

        matches = list(pattern.finditer(text))
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
        uid, models = self._auth()
        domain = [
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("name", "!=", "/"),
        ]
        fields = ["id", "name", "partner_id", "invoice_date", "create_date", "write_date"]
        return models.execute_kw(
            Odoo.DB, uid, Odoo.API_KEY,
            "account.move", "search_read",
            [domain],
            {"fields": fields, "order": "write_date desc, id desc", "limit": limit},
        )


    def list_validated_since(self, last_write_date, last_id, limit=200):
        uid, models = self._auth()
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
        return models.execute_kw(
            Odoo.DB, uid, Odoo.API_KEY,
            "account.move", "search_read",
            [domain],
            {"fields": fields, "order": "write_date asc, id asc", "limit": limit},
        )


    def get_partner_phone(self, partner_id):
        uid, models = self._auth()
        recs = models.execute_kw(
            Odoo.DB, uid, Odoo.API_KEY,
            "res.partner", "read",
            [[partner_id]],
            {"fields": ["phone", "mobile"]}
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
