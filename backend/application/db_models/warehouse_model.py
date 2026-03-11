from application.db_models.base_model import db, BaseModel


class WarehouseCodes(BaseModel):
    __tablename__ = 'warehouse_codes'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    block = db.Column(db.String(5), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    position = db.Column(db.String(1), nullable=False)


class WarehouseStock(BaseModel):
    __tablename__ = 'warehouse_stock'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    code_id = db.Column(db.Integer, db.ForeignKey('warehouse_codes.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('machines.id'), nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    product = db.relationship("Machines", lazy="joined", foreign_keys=[product_id])
    code = db.relationship("WarehouseCodes", lazy="joined", foreign_keys=[code_id])
