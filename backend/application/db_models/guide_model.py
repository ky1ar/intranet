from application.db_models.base_model import db, BaseModel


class MachineGuide(BaseModel):
    __tablename__ = "machine_guide"

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    machine_id  = db.Column(db.Integer, db.ForeignKey("machines.id"), nullable=False, unique=True)
    description = db.Column(db.Text)
    items       = db.Column(db.JSON, default=list)
    created_at  = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at  = db.Column(db.DateTime, onupdate=db.func.now())

    machine = db.relationship("Machines", lazy="joined")
