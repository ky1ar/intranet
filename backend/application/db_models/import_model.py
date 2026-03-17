from application.db_models.base_model import db, BaseModel


class ImportBusiness(BaseModel):
    __tablename__ = 'import_business'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)


class ImportIncoterm(BaseModel):
    __tablename__ = 'import_incoterm'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    code = db.Column(db.String(3), nullable=False)


class ImportPort(BaseModel):
    __tablename__ = 'import_port'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)


class ImportProvider(BaseModel):
    __tablename__ = 'import_provider'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(64))
    telephone = db.Column(db.String(64))


class ImportType(BaseModel):
    __tablename__ = 'import_type'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)


class ImportStatus(BaseModel):
    __tablename__ = 'import_status'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    image = db.Column(db.String(64), nullable=False)


class ImportShipment(BaseModel):
    __tablename__ = "import_shipment"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('import_business.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('import_type.id'), nullable=False)
    port_id = db.Column(db.Integer, db.ForeignKey('import_port.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('import_status.id'), nullable=False)
    fcl = db.Column(db.Integer, nullable=False, default=0)

    description = db.Column(db.Text)
    local_agent_name = db.Column(db.String(128))
    origin_agent_name = db.Column(db.String(128))

    advance_payment_percent = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    balance_days = db.Column(db.Integer, nullable=False, default=0)

    booking_date = db.Column(db.Date)
    etd_date = db.Column(db.Date)
    eta_date = db.Column(db.Date)
    qty = db.Column(db.Integer)
    pallets = db.Column(db.Integer)
    weight = db.Column(db.Float)
    volume = db.Column(db.Float)
    deadline_date = db.Column(db.Date)
    pay_date = db.Column(db.Date)
    traffic_light = db.Column(db.String(12))
    delivery_date = db.Column(db.Date)
    delivery_time = db.Column(db.Time)
    delivery_name = db.Column(db.String(128))
    delivery_phone = db.Column(db.String(9))
    delivery_code = db.Column(db.String(9))
    custom_port_name = db.Column(db.String(150), nullable=True)
    tracking_link = db.Column(db.Text, nullable=True)

    business = db.relationship("ImportBusiness", lazy="joined", foreign_keys=[business_id])
    type = db.relationship("ImportType", lazy="joined", foreign_keys=[type_id])
    port = db.relationship("ImportPort", lazy="joined", foreign_keys=[port_id])
    status = db.relationship("ImportStatus", lazy="joined", foreign_keys=[status_id])
    lines = db.relationship("ImportShipmentLine", back_populates="shipment", cascade="all, delete-orphan", lazy="selectin")
    attachments = db.relationship("ImportAttachment", back_populates="import_shipment", cascade="all, delete-orphan", lazy="selectin")


class ImportShipmentLine(db.Model):
    __tablename__ = "import_shipment_line"

    id = db.Column(db.Integer, primary_key=True)
    import_shipment_id = db.Column(db.Integer, db.ForeignKey("import_shipment.id", ondelete="CASCADE"), nullable=False, index=True)

    provider_id = db.Column(db.Integer, db.ForeignKey("import_provider.id"), nullable=False)
    incoterm_id = db.Column(db.Integer, db.ForeignKey("import_incoterm.id"))
    custom_incoterm_name = db.Column(db.String(120), nullable=True)
    advance_payment_percent = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    balance_days = db.Column(db.Integer, nullable=False, default=0)
    position = db.Column(db.Integer, nullable=False, default=1)

    shipment = db.relationship("ImportShipment", back_populates="lines")
    provider = db.relationship("ImportProvider", lazy="joined")
    incoterm = db.relationship("ImportIncoterm", lazy="joined")


class ImportStatusHistory(BaseModel):
    __tablename__ = "import_status_history"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    import_shipment_id = db.Column(db.Integer, db.ForeignKey('import_shipment.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('import_status.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notes = db.Column(db.Text, default=None)
    created_at = db.Column(db.DateTime, nullable=False)

    import_shipment = db.relationship("ImportShipment", lazy="joined", foreign_keys=[import_shipment_id])
    status = db.relationship("ImportStatus", lazy="joined", foreign_keys=[status_id])
    user = db.relationship("Users", lazy="joined", foreign_keys=[user_id])


class ImportAttachment(BaseModel):
    __tablename__ = "import_attachment"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    import_shipment_id = db.Column(db.Integer, db.ForeignKey('import_shipment.id'), nullable=False)
    target = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(255), nullable=False, unique=True)
    mime_type = db.Column(db.String(120))
    size_bytes = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=False)

    # import_shipment = db.relationship("ImportShipment", lazy="joined", foreign_keys=[import_shipment_id])
    import_shipment = db.relationship("ImportShipment", lazy="joined", foreign_keys=[import_shipment_id], back_populates="attachments")
    user = db.relationship("Users", lazy="joined", foreign_keys=[user_id])


class ImportChats(db.Model):
    __tablename__ = 'import_chats'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    import_shipment_id = db.Column(db.Integer, db.ForeignKey('import_shipment.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    commenter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column( db.DateTime, nullable=False)
    
    commenter = db.relationship( "Users", lazy="joined", foreign_keys=[commenter_id])
    import_shipment = db.relationship( "ImportShipment", lazy="joined", foreign_keys=[import_shipment_id], backref=db.backref("chats", lazy="selectin"))