from application.db_models.base_model import db, BaseModel


class LeaveStatus(BaseModel):
    __tablename__ = 'leave_status'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    slug = db.Column(db.String(64), nullable=False)


class LeaveDuration(BaseModel):
    __tablename__ = 'leave_duration'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    slug = db.Column(db.String(64), nullable=False)


class LeaveType(BaseModel):
    __tablename__ = 'leave_type'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    slug = db.Column(db.String(64), nullable=False)
