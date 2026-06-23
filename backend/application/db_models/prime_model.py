from application.db_models.base_model import db, BaseModel


class PrimeSubscription(BaseModel):
    __tablename__ = "prime_subscriptions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    culqi_subscription_id = db.Column(db.String(255), nullable=False, unique=True)
    plan_type = db.Column(db.String(50), nullable=False) # 'lite' o 'full'
    status = db.Column(db.String(50), nullable=False, default="active") # 'active', 'cancelled', 'past_due'
    started_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    client = db.relationship("Clients", foreign_keys=[client_id], lazy="joined")
