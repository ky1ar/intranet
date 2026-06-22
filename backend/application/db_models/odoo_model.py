from datetime import datetime
from application.db_models.base_model import db, BaseModel


class OdooInvoiceCursor(BaseModel):
    __tablename__ = "odoo_invoice_cursor"

    id = db.Column(db.Integer, primary_key=True)  # siempre 1 fila
    last_write_date = db.Column(db.String(19), nullable=False)  # "YYYY-MM-DD HH:MM:SS"
    last_id = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class OdooPaidInvoice(BaseModel):
    __tablename__ = "odoo_paid_invoice"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invoice_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    invoice_name = db.Column(db.String(64))
    write_date = db.Column(db.String(19), nullable=False, index=True)

    partner_id = db.Column(db.Integer)
    partner_name = db.Column(db.String(255))
    partner_phone = db.Column(db.String(16))

    pdf_ready = db.Column(db.Boolean, default=False, nullable=False)
    pdf_filename = db.Column(db.String(255))
    pdf_path = db.Column(db.String(512))
    pdf_size = db.Column(db.Integer, default=0, nullable=False)

    sent_whatsapp = db.Column(db.Boolean, default=False, nullable=False)
    sent_at = db.Column(db.DateTime)
    send_attempts = db.Column(db.Integer, default=0, nullable=False)
    send_error = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
