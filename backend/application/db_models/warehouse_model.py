from application.db_models.base_model import db, BaseModel


class WarehouseCodes(BaseModel):
    __tablename__ = 'warehouse_codes'

    id          = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    block       = db.Column(db.Integer, nullable=False)
    level       = db.Column(db.Integer, nullable=False)
    position    = db.Column(db.String(1), nullable=False)


class WarehouseStock(BaseModel):
    __tablename__ = 'warehouse_stock'

    id          = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    code_id     = db.Column(db.Integer, db.ForeignKey('warehouse_codes.id'), nullable=False)
    product_id  = db.Column(db.Integer, db.ForeignKey('machines.id'), nullable=False)
    stock       = db.Column(db.Integer, nullable=False)

    product     = db.relationship("Machines", lazy="joined", foreign_keys=[product_id])
    code        = db.relationship("WarehouseCodes", lazy="joined", foreign_keys=[code_id])


class WarehouseLog(BaseModel):
    __tablename__ = 'warehouse_log'

    id         = db.Column(db.Integer, autoincrement=True, primary_key=True)
    action     = db.Column(db.String(20), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('machines.id'), nullable=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'),     nullable=True)
    quantity   = db.Column(db.Integer, nullable=True)
    order_ref  = db.Column(db.String(20), nullable=True)
    from_code_id = db.Column(db.Integer, db.ForeignKey('warehouse_codes.id'),  nullable=True)
    to_code_id   = db.Column(db.Integer, db.ForeignKey('warehouse_codes.id'),  nullable=True)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    product     = db.relationship("Machines", lazy="joined", foreign_keys=[product_id])
    user        = db.relationship("Users",    lazy="joined", foreign_keys=[user_id])
    from_code   = db.relationship("WarehouseCodes", lazy="joined", foreign_keys=[from_code_id])
    to_code     = db.relationship("WarehouseCodes", lazy="joined", foreign_keys=[to_code_id])
