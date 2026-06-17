from application.db_models.base_model import db, BaseModel


class ApprovalType(BaseModel):
    __tablename__ = "approval_type"

    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(30), nullable=False, unique=True)


class ApprovalRequest(BaseModel):
    __tablename__ = "approval_request"

    id                = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id         = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    type_id           = db.Column(db.Integer, db.ForeignKey("approval_type.id"), nullable=False)
    status            = db.Column(db.String(20), nullable=False, default="pending")
    approved_by       = db.Column(db.Integer, db.ForeignKey("user.id"))
    approved_at       = db.Column(db.DateTime)
    rejection_reason  = db.Column(db.Text)
    access_url        = db.Column(db.Text)
    invoice_number    = db.Column(db.String(50))
    voucher_filename  = db.Column(db.String(255))
    machine_id        = db.Column(db.Integer, db.ForeignKey("machines.id"))
    created_at        = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at        = db.Column(db.DateTime, onupdate=db.func.now())

    type_rel  = db.relationship("ApprovalType", lazy="joined")
    client    = db.relationship("Clients", foreign_keys=[client_id], lazy="joined")
    approver  = db.relationship("Users", foreign_keys=[approved_by], lazy="joined")
    machine   = db.relationship("Machines", lazy="joined")


class ApprovalChats(BaseModel):
    __tablename__ = "approval_chats"

    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    approval_id  = db.Column(db.Integer, db.ForeignKey("approval_request.id"), nullable=False)
    comment      = db.Column(db.Text, nullable=False)
    commenter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at   = db.Column(db.DateTime, nullable=False)

    commenter        = db.relationship("Users", foreign_keys=[commenter_id], lazy="joined")
    approval_request = db.relationship(
        "ApprovalRequest",
        foreign_keys=[approval_id],
        backref=db.backref("chats", lazy="selectin"),
    )
