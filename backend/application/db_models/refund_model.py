from application.db_models.base_model import db, BaseModel


class RefundStatus(BaseModel):
    __tablename__ = "refund_status"

    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    slug = db.Column(db.String(30), nullable=False)


class RefundRequest(BaseModel):
    __tablename__ = "refund_request"

    id                = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_id         = db.Column(db.Integer, db.ForeignKey("refund_status.id"), nullable=False, default=1)
    is_admin_register = db.Column(db.Boolean, nullable=False, default=False)

    client_order_id   = db.Column(db.Integer, db.ForeignKey("client_orders.id"), nullable=False)

    client_order = db.relationship("ClientOrders", lazy="joined", foreign_keys=[client_order_id])
    reason            = db.Column(db.String(30), nullable=False)
    reason_detail     = db.Column(db.String(255))
    detail            = db.Column(db.Text)
    order_amount      = db.Column(db.Numeric(10, 2), nullable=False)
    refund_amount     = db.Column(db.Numeric(10, 2), nullable=False)
    applies_penalty   = db.Column(db.Boolean, nullable=False, default=False)
    penalty_amount    = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    net_refund        = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method         = db.Column(db.String(30), nullable=False)
    scheduled_date         = db.Column(db.Date)
    assigned_to            = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    original_order_number  = db.Column(db.String(50), nullable=True)

    created_at        = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at        = db.Column(db.DateTime, onupdate=db.func.now())
    deleted_at        = db.Column(db.DateTime)

    status   = db.relationship("RefundStatus", lazy="joined")
    assignee = db.relationship("Users", foreign_keys=[assigned_to], lazy="joined")


class RefundAttachment(BaseModel):
    __tablename__ = "refund_attachment"

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    refund_id     = db.Column(db.Integer, db.ForeignKey("refund_request.id"), nullable=False)
    user_id       = db.Column(db.Integer, db.ForeignKey("user.id"))
    original_name = db.Column(db.String(255), nullable=False)
    stored_name   = db.Column(db.String(255), nullable=False, unique=True)
    mime_type     = db.Column(db.String(120))
    size_bytes    = db.Column(db.Integer)
    created_at    = db.Column(db.DateTime, nullable=False)

    refund = db.relationship("RefundRequest", lazy="joined", foreign_keys=[refund_id])
    user   = db.relationship("Users", lazy="joined", foreign_keys=[user_id])


class RefundLink(BaseModel):
    __tablename__ = "refund_link"

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token      = db.Column(db.String(255), unique=True, nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    refund_id  = db.Column(db.Integer, db.ForeignKey("refund_request.id"))
    status_id  = db.Column(db.Integer, nullable=False, default=1)  # 1=pendiente 2=usado 3=eliminado
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    user   = db.relationship("Users", lazy="joined", foreign_keys=[user_id])
    refund = db.relationship("RefundRequest", lazy="joined", foreign_keys=[refund_id])


class RefundChat(db.Model):
    __tablename__ = "refund_chat"

    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    refund_id    = db.Column(db.Integer, db.ForeignKey("refund_request.id"), nullable=False)
    comment      = db.Column(db.Text, nullable=False)
    commenter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at   = db.Column(db.DateTime, nullable=False)

    commenter = db.relationship("Users", lazy="joined", foreign_keys=[commenter_id])
    refund    = db.relationship("RefundRequest", lazy="joined", foreign_keys=[refund_id],
                                backref=db.backref("chats", lazy="selectin"))
