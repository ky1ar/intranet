from application.db_models.base_model import db, BaseModel


class SafebuyStatus(BaseModel):
    __tablename__ = "safebuy_status"

    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    slug = db.Column(db.String(30), nullable=False)


class SafebuyRequest(BaseModel):
    __tablename__ = "safebuy_request"

    id                = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_id         = db.Column(db.Integer, db.ForeignKey("safebuy_status.id"), nullable=False, default=1)

    client_id         = db.Column(db.Integer, db.ForeignKey("clients.id"))

    order_number      = db.Column(db.String(50))
    purchase_date     = db.Column(db.Date, nullable=False)
    purchase_channel  = db.Column(db.String(20), nullable=False, default="web")
    machine_id        = db.Column(db.Integer, db.ForeignKey("machines.id"))
    original_price    = db.Column(db.Numeric(10, 2), nullable=False)
    paid_price        = db.Column(db.Numeric(10, 2), nullable=False)

    new_price         = db.Column(db.Numeric(10, 2), nullable=False)
    price_difference  = db.Column(db.Numeric(10, 2), nullable=False)

    credit_amount     = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    credit_used       = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    assigned_user_id  = db.Column(db.Integer, db.ForeignKey("user.id"))
    approved_by       = db.Column(db.Integer, db.ForeignKey("user.id"))
    approved_at       = db.Column(db.DateTime)
    rejection_reason  = db.Column(db.Text)

    created_at        = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at        = db.Column(db.DateTime, onupdate=db.func.now())
    deleted_at        = db.Column(db.DateTime)

    status   = db.relationship("SafebuyStatus", lazy="joined")
    client   = db.relationship("Clients", foreign_keys=[client_id], lazy="joined")
    machine  = db.relationship("Machines", foreign_keys=[machine_id], lazy="joined")
    assigned = db.relationship("Users", foreign_keys=[assigned_user_id], lazy="joined")
    approver = db.relationship("Users", foreign_keys=[approved_by], lazy="joined")


class SafebuyCreditUsage(BaseModel):
    __tablename__ = "safebuy_credit_usage"

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id    = db.Column(db.Integer, db.ForeignKey("safebuy_request.id"), nullable=False)
    amount_used   = db.Column(db.Numeric(10, 2), nullable=False)
    order_number  = db.Column(db.String(50))
    order_total   = db.Column(db.Numeric(10, 2))
    applied_by    = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    notes         = db.Column(db.Text)
    created_at    = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    request = db.relationship("SafebuyRequest", lazy="joined")
    user    = db.relationship("Users", lazy="joined")


class SafebuyAttachment(BaseModel):
    __tablename__ = "safebuy_attachment"

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id    = db.Column(db.Integer, db.ForeignKey("safebuy_request.id"), nullable=False)
    target        = db.Column(db.String(100), nullable=False, default="default")
    user_id       = db.Column(db.Integer, db.ForeignKey("user.id"))
    original_name = db.Column(db.String(255), nullable=False)
    stored_name   = db.Column(db.String(255), nullable=False, unique=True)
    mime_type     = db.Column(db.String(120))
    size_bytes    = db.Column(db.Integer)
    created_at    = db.Column(db.DateTime, nullable=False)

    request = db.relationship("SafebuyRequest", lazy="joined", foreign_keys=[request_id])
    user    = db.relationship("Users", lazy="joined", foreign_keys=[user_id])


class SafebuyChat(db.Model):
    __tablename__ = "safebuy_chat"

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id    = db.Column(db.Integer, db.ForeignKey("safebuy_request.id"), nullable=False)
    comment       = db.Column(db.Text, nullable=False)
    commenter_id  = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at    = db.Column(db.DateTime, nullable=False)

    commenter = db.relationship("Users", lazy="joined", foreign_keys=[commenter_id])
    request   = db.relationship("SafebuyRequest", lazy="joined", foreign_keys=[request_id],
                                backref=db.backref("chats", lazy="selectin"))