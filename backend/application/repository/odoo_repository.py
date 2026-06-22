from datetime import datetime, timedelta
from application.db_models.odoo_model import OdooInvoiceCursor, OdooPaidInvoice
from flask import g


class OdooRepository:
    def get_cursor(self):
        return g.db_session.query(OdooInvoiceCursor).filter_by(id=1).first()


    def get_sent_with_pdf(self):
        cutoff = datetime.utcnow() - timedelta(days=7)

        return (
            g.db_session.query(OdooPaidInvoice)
            .filter(
                OdooPaidInvoice.sent_whatsapp == True,
                OdooPaidInvoice.pdf_ready == True,
                OdooPaidInvoice.pdf_path.isnot(None),
                OdooPaidInvoice.sent_at.isnot(None),
                OdooPaidInvoice.sent_at <= cutoff,
            )
            .all()
        )
    

    def clear_pdf_fields(self, invoice_id):
        row = self.get_by_invoice_id(invoice_id)
        if not row:
            return

        row.pdf_ready = False
        row.pdf_filename = None
        row.pdf_path = None
        row.pdf_size = 0
        g.db_session.commit()

        
    def upsert_cursor(self, last_write_date, last_id):
        row = self.get_cursor()
        if not row:
            row = OdooInvoiceCursor(id=1, last_write_date=last_write_date, last_id=last_id)
            g.db_session.add(row)
        else:
            row.last_write_date = last_write_date
            row.last_id = last_id

        g.db_session.commit()
        return row


    def get_by_invoice_id(self, invoice_id):
        return g.db_session.query(OdooPaidInvoice).filter_by(invoice_id=invoice_id).first()


    def upsert_paid_invoice(self, invoice_id, invoice_name, write_date, partner_id=None, partner_name=None, partner_phone=None):
        row = self.get_by_invoice_id(invoice_id)
        if not row:
            row = OdooPaidInvoice(
                invoice_id=invoice_id,
                invoice_name=invoice_name,
                write_date=write_date,
                partner_id=partner_id,
                partner_name=partner_name,
                partner_phone=partner_phone,
            )
            g.db_session.add(row)
        else:
            row.invoice_name = invoice_name
            row.write_date = write_date
            row.partner_id = partner_id
            row.partner_name = partner_name
            row.partner_phone = partner_phone

        g.db_session.commit()
        return row


    def update_pdf(self, invoice_id, pdf_ready=False, pdf_filename=None, pdf_path=None, pdf_size=0):
        row = self.get_by_invoice_id(invoice_id)
        if not row:
            return None
        row.pdf_ready = bool(pdf_ready)
        row.pdf_filename = pdf_filename
        row.pdf_path = pdf_path
        row.pdf_size = int(pdf_size or 0)
        g.db_session.commit()
        return row


    def mark_sent(self, invoice_id):
        row = self.get_by_invoice_id(invoice_id)
        if not row:
            return None
        row.sent_whatsapp = True
        row.sent_at = datetime.utcnow()
        row.send_error = None
        g.db_session.commit()
        return row


    def mark_send_failed(self, invoice_id, err: str):
        row = self.get_by_invoice_id(invoice_id)
        if not row:
            return None
        row.sent_whatsapp = False
        row.send_attempts = (row.send_attempts or 0) + 1
        row.send_error = (err or "")[:4000]
        g.db_session.commit()
        return row
