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


class LeaveRequest(BaseModel):
    __tablename__ = 'leave_request'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    request_type = db.Column(db.String(24), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey("leave_status.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    duration_id = db.Column(db.Integer, db.ForeignKey("leave_duration.id"))
    leave_type_id = db.Column(db.Integer, db.ForeignKey("leave_type.id"))
    leave_type_detail = db.Column(db.String(255))
    description = db.Column(db.Text)
    motive = db.Column(db.Text)
    recovery_plan = db.Column(db.Text)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, nullable=False)
    deleted_at = db.Column(db.DateTime)

    user = db.relationship("Users", lazy="joined", foreign_keys=[user_id])
    status = db.relationship("LeaveStatus", lazy="joined", foreign_keys=[status_id])
    duration = db.relationship("LeaveDuration", lazy="joined", foreign_keys=[duration_id])
    type = db.relationship("LeaveType", lazy="joined", foreign_keys=[leave_type_id])
