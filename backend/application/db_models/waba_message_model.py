from application.db_models.base_model import db, BaseModel


class WabaMessage(BaseModel):
    __tablename__ = "waba_message"

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wa_id         = db.Column(db.String(20), nullable=False, index=True)
    contact_name  = db.Column(db.String(100), nullable=True)
    agent_id      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # usuario que responde de nuestro lado
    wamid         = db.Column(db.String(200), nullable=True)
    direction     = db.Column(db.String(5), nullable=False)   # 'in' | 'out'
    msg_type      = db.Column(db.String(30), nullable=False)  # 'text', 'template', 'image', etc.
    content       = db.Column(db.Text, nullable=True)
    template_name = db.Column(db.String(100), nullable=True)
    media_url     = db.Column(db.String(500), nullable=True)
    is_read       = db.Column(db.Boolean, nullable=False, default=False)  # solo relevante para entrantes
    waba_timestamp= db.Column(db.BigInteger, nullable=True)
    created_at    = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    agent = db.relationship("Users", foreign_keys=[agent_id], lazy="joined")
