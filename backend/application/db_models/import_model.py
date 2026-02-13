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
    provider_id = db.Column(db.Integer, db.ForeignKey('import_provider.id'), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('import_business.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('import_type.id'), nullable=False)
    incoterm_id = db.Column(db.Integer, db.ForeignKey('import_incoterm.id'), nullable=False)
    port_id = db.Column(db.Integer, db.ForeignKey('import_port.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('import_status.id'), nullable=False)
    description = db.Column(db.Text)
    local_agent_name = db.Column(db.String(128))
    origin_agent_name = db.Column(db.String(128))
    booking_date = db.Column(db.Date)
    etd_date = db.Column(db.Date)

    provider = db.relationship("ImportProvider", lazy="joined", foreign_keys=[provider_id])
    business = db.relationship("ImportBusiness", lazy="joined", foreign_keys=[business_id])
    type = db.relationship("ImportType", lazy="joined", foreign_keys=[type_id])
    incoterm = db.relationship("ImportIncoterm", lazy="joined", foreign_keys=[incoterm_id])
    port = db.relationship("ImportPort", lazy="joined", foreign_keys=[port_id])
    status = db.relationship("ImportStatus", lazy="joined", foreign_keys=[status_id])


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

    import_shipment = db.relationship("ImportShipment", lazy="joined", foreign_keys=[import_shipment_id])
    user = db.relationship("Users", lazy="joined", foreign_keys=[user_id])
