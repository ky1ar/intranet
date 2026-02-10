from application.db_models.base_model import db, BaseModel


class ComplaintRequest(BaseModel):
    __tablename__ = "complaint_request"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    is_minor = db.Column(db.Boolean, default=False)
    order_number = db.Column(db.String(24), nullable=False)
    complaint_consumption_id = db.Column(db.Integer, db.ForeignKey('complaint_consumption.id'), nullable=False)
    amount = db.Column(db.Numeric(12, 2), default=None)
    purchase_date = db.Column(db.Date, default=None)
    consumption_description = db.Column(db.Text, nullable=False)
    complaint_type_id = db.Column(db.Integer, db.ForeignKey('complaint_type.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('complaint_category.id'), nullable=False)
    detail = db.Column(db.Text, nullable=False)
    customer_request = db.Column(db.Text, nullable=False)
    declaration_accepted = db.Column(db.Boolean, nullable=False, default=False)
    status_id = db.Column(db.Integer, db.ForeignKey('complaint_status.id'), nullable=False, default=1)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    resolved = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, nullable=False)

    client = db.relationship("Clients", lazy="joined", foreign_keys=[client_id])
    complaint_consumption = db.relationship("ComplaintConsumption", lazy="joined", foreign_keys=[complaint_consumption_id])
    complaint_type = db.relationship("ComplaintType", lazy="joined", foreign_keys=[complaint_type_id])
    category = db.relationship("ComplaintCategory", lazy="joined", foreign_keys=[category_id])
    owner = db.relationship("Users", lazy="joined", foreign_keys=[owner_id])
    seller = db.relationship("Users", lazy="joined", foreign_keys=[seller_id])
    status = db.relationship("ComplaintStatus", lazy="joined", foreign_keys=[status_id])


class ComplaintConsumption(BaseModel):
    __tablename__ = 'complaint_consumption'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)



class ComplaintCategory(BaseModel):
    __tablename__ = 'complaint_category'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)


class ComplaintType(BaseModel):
    __tablename__ = 'complaint_type'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)


class ComplaintRequestStatus(BaseModel):
    __tablename__ = "complaint_request_status"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint_request.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('complaint_status.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True, default=None)
    created_at = db.Column(db.DateTime, nullable=False)

    complaint = db.relationship("ComplaintRequest", lazy="joined", foreign_keys=[complaint_id])
    status = db.relationship("ComplaintStatus", lazy="joined", foreign_keys=[status_id])
    user = db.relationship("Users", lazy="joined", foreign_keys=[user_id])


class ComplaintStatus(BaseModel):
    __tablename__ = 'complaint_status'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)


class ComplaintAttachment(BaseModel):
    __tablename__ = "complaint_attachment"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint_request.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(255), nullable=False, unique=True)
    mime_type = db.Column(db.String(120), nullable=True)
    size_bytes = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)

    complaint = db.relationship("ComplaintRequest", lazy="joined", foreign_keys=[complaint_id])
    user = db.relationship("Users", lazy="joined", foreign_keys=[uploaded_by])


class ComplaintChats(db.Model):
    __tablename__ = 'complaint_chats'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint_request.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    commenter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column( db.DateTime, nullable=False)
    
    commenter = db.relationship( "Users", lazy="joined", foreign_keys=[commenter_id])
    complaint_request = db.relationship( "ComplaintRequest", lazy="joined", foreign_keys=[complaint_id], backref=db.backref("chats", lazy="selectin"))