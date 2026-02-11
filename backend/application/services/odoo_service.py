import logging, os, re
from datetime import datetime, date, timedelta
from application.repository.odoo_repository import OdooRepository
from application.integrations.odoo_client import OdooClient
from application.proxy.whatsapp import Whatsapp
from config import Config


class OdooService:
    def __init__(self):
        self.odoo_client = OdooClient()
        self.odoo_repository = OdooRepository()
        self.whatsapp = Whatsapp()


    def _parse_ymd(self, s: str | None):
        if not s:
            return None
        try:
            return datetime.strptime(str(s)[:10], "%Y-%m-%d").date()
        except Exception:
            return None
        

    def _is_too_old(self, invoice_date: str | None, write_date: str | None = None):
        cutoff = date.today() - timedelta(days=7)

        inv_d = self._parse_ymd(invoice_date)
        if inv_d:
            return inv_d < cutoff

        wr_d = self._parse_ymd(write_date)
        if wr_d:
            return wr_d < cutoff

        return False
    
        
    def ensure_upload_folder(self, path=Config.UPLOAD_PDF_FOLDER):
        try:
            os.makedirs(path, exist_ok=True)
        except Exception:
            logging.exception("Could not create upload folder: %s", path)
            raise
        return path


    def safe_filename(self, name, default = "invoice"):
        if not name:
            name = default
        name = name.strip()
        name = re.sub(r"[^\w\-\.]+", "_", name, flags=re.UNICODE)  # letras/números/_-.
        name = re.sub(r"_+", "_", name).strip("_.")
        return name or default


    def save_pdf_bytes(self, pdf_bytes: bytes, invoice_id, invoice_name=None):

        folder = self.ensure_upload_folder(Config.UPLOAD_PDF_FOLDER)

        base = self.safe_filename(invoice_name or f"invoice_{invoice_id}")
        filename = f"{invoice_id}_{base}.pdf"
        full_path = os.path.join(folder, filename)

        tmp_path = full_path + ".tmp"
        with open(tmp_path, "wb") as f:
            f.write(pdf_bytes)
            f.flush()
            os.fsync(f.fileno())

        os.replace(tmp_path, full_path)

        return {
            "filename": filename,
            "path": full_path,
            "size": len(pdf_bytes),
        }


    def poll_paid_invoices(self):
        cursor = self.odoo_repository.get_cursor()

        if not cursor:
            invoices = self.odoo_client.list_validated_last(limit=1)
            if not invoices:
                self.cleanup_sent_pdfs()
                return [], 200

            items = self._persist_and_map(invoices)

            newest = invoices[0]
            self.odoo_repository.upsert_cursor(newest["write_date"], newest["id"])

            self.cleanup_sent_pdfs()
            return items, 200

        invoices = self.odoo_client.list_validated_since(
            last_write_date=cursor.last_write_date,
            last_id=cursor.last_id,
            limit=200,
        )

        if not invoices:
            return [], 200

        items = self._persist_and_map(invoices)

        newest = invoices[-1]
        self.odoo_repository.upsert_cursor(newest["write_date"], newest["id"])

        self.cleanup_sent_pdfs()
        return items, 200

    
    def _persist_and_map(self, invoices):
        items = []

        for inv in invoices:
            invoice_id = inv["id"]
            invoice_name = inv.get("name")
            write_date = inv.get("write_date")
            invoice_date = inv.get("invoice_date")

            if self._is_too_old(invoice_date=invoice_date, write_date=write_date):
                logging.info(
                    "Skipping old invoice: id=%s name=%s invoice_date=%s write_date=%s (max_age_days=%s)",
                    invoice_id, invoice_name, invoice_date, write_date,
                    getattr(Config, "ODOO_MAX_INVOICE_AGE_DAYS", 7)
                )
                continue

            partner_id = None
            partner_name = None
            partner_raw = inv.get("partner_id")

            if isinstance(partner_raw, list) and len(partner_raw) >= 2:
                partner_id = partner_raw[0]
                partner_name = partner_raw[1]
            elif isinstance(partner_raw, int):
                partner_id = partner_raw

            # ✅ lee fila local (si existe)
            row = self.odoo_repository.get_by_invoice_id(invoice_id)

            # ✅ si ya fue enviado por whatsapp -> skip total
            if row and row.sent_whatsapp:
                continue

            if row and (row.send_attempts or 0) >= 10:
                logging.warning(
                    "Invoice %s skipped: max send attempts reached (%s). last_error=%s",
                    invoice_id, row.send_attempts, (row.send_error or "")[:200]
                )
                continue

            phone = self.odoo_client.get_partner_phone(partner_id) if partner_id else None
            phone = phone or None

            # ✅ upsert base SIEMPRE (no hacemos continue por existir)
            row = self.odoo_repository.upsert_paid_invoice(
                invoice_id=invoice_id,
                invoice_name=invoice_name,
                write_date=write_date,
                partner_id=partner_id,
                partner_name=partner_name,
                partner_phone=phone,
            )

            pdf_ready = bool(row.pdf_ready)
            pdf_filename = row.pdf_filename
            pdf_path = row.pdf_path
            pdf_size = row.pdf_size or 0

            # ✅ si no hay PDF listo, intenta obtenerlo
            if phone and not pdf_ready:
                try:
                    pdf_bytes = self.odoo_client.get_invoice_pdf_bytes(invoice_id)

                    if pdf_bytes:
                        saved = self.save_pdf_bytes(pdf_bytes, invoice_id=invoice_id, invoice_name=invoice_name)
                        pdf_ready = True
                        pdf_filename = saved["filename"]
                        pdf_path = saved["path"]
                        pdf_size = len(pdf_bytes)

                        self.odoo_repository.update_pdf(
                            invoice_id=invoice_id,
                            pdf_ready=True,
                            pdf_filename=pdf_filename,
                            pdf_path=pdf_path,
                            pdf_size=pdf_size,
                        )
                    else:
                        # PDF todavía no existe en Odoo -> queda pendiente para el próximo minuto
                        self.odoo_repository.update_pdf(invoice_id=invoice_id, pdf_ready=False)

                except Exception as e:
                    logging.exception("PDF fetch failed invoice_id=%s", invoice_id)
                    self.odoo_repository.mark_send_failed(invoice_id, f"PDF fetch failed: {e}")

            # ✅ enviar SOLO si pdf_ready y no enviado
            sent = False
            if phone and pdf_ready and not row.sent_whatsapp:
                try:
                    waba_phone = f"51{phone}"
                    invoice_date_str = invoice_date or (write_date or "")[:10]

                    self.whatsapp.send_odoo_invoice(
                        client_phone=waba_phone,
                        client_name=partner_name,
                        invoice_number=invoice_name,
                        invoice_date=invoice_date_str,
                        pdf_filename=pdf_filename,
                    )

                    self.odoo_repository.mark_sent(invoice_id)
                    sent = True

                except Exception as e:
                    logging.exception("WhatsApp send failed invoice_id=%s", invoice_id)
                    self.odoo_repository.mark_send_failed(invoice_id, f"WABA send failed: {e}")

            items.append({
                "invoice_id": invoice_id,
                "customer_name": partner_name,
                "customer_phone": phone,
                "invoice_series": invoice_name,
                "pdf_ready": pdf_ready,
                "pdf_size": pdf_size,
                "pdf_filename": pdf_filename,
                "pdf_path": pdf_path,
                "sent_whatsapp": sent,
            })

            logging.info(
                "Validated invoice detected: id=%s name=%s phone=%s pdf_ready=%s sent=%s",
                invoice_id, invoice_name, phone, pdf_ready, sent
            )

        return items
    

    def cleanup_sent_pdfs(self):
        rows = self.odoo_repository.get_sent_with_pdf()

        for row in rows:
            try:
                if row.pdf_path and os.path.exists(row.pdf_path):
                    os.remove(row.pdf_path)
                    logging.info("Deleted PDF %s", row.pdf_path)

                self.odoo_repository.clear_pdf_fields(row.invoice_id)

            except Exception:
                logging.exception("Failed deleting PDF invoice_id=%s", row.invoice_id)