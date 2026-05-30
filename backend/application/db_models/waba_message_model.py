from application.db_models.base_model import db, BaseModel


class WabaMessage(BaseModel):
    __tablename__ = "waba_message"

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wa_id         = db.Column(db.String(20), nullable=False, index=True)
    contact_name  = db.Column(db.String(100), nullable=True)
    wamid         = db.Column(db.String(200), nullable=True)
    direction     = db.Column(db.String(5), nullable=False)   # 'in' | 'out'
    msg_type      = db.Column(db.String(30), nullable=False)  # 'text', 'template', 'image', etc.
    content       = db.Column(db.Text, nullable=True)
    template_name = db.Column(db.String(100), nullable=True)
    waba_timestamp= db.Column(db.BigInteger, nullable=True)
    created_at    = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
