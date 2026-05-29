from application.db_models.base_model import db, BaseModel


class WabaReply(BaseModel):
    __tablename__ = "waba_reply"

    id               = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wa_id            = db.Column(db.String(20), nullable=False)
    contact_name     = db.Column(db.String(100), nullable=True)
    wamid            = db.Column(db.String(200), nullable=True)
    msg_type         = db.Column(db.String(30), nullable=False)
    content          = db.Column(db.Text, nullable=True)
    conversation_id  = db.Column(db.String(100), nullable=True)
    origin_type      = db.Column(db.String(30), nullable=True)
    waba_timestamp   = db.Column(db.BigInteger, nullable=True)
    created_at       = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
