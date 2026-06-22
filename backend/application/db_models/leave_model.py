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
    assigned = db.relationship("Users", lazy="joined", foreign_keys=[assigned_user_id])


class LeaveAdjustment(BaseModel):
    """Legacy - mantener por compatibilidad"""
    __tablename__ = 'leave_adjustment'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    available = db.Column(db.Float, nullable=False)
    finish_date = db.Column(db.String(24), nullable=False)

    user = db.relationship("Users", lazy="joined", foreign_keys=[user_id])


class LeaveBalance(BaseModel):
    """Saldo de vacaciones acumulativo por usuario por periodo"""
    __tablename__ = 'leave_balance'

    id             = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    period_id      = db.Column(db.Integer, db.ForeignKey("attendance_period.id"), nullable=False)
    vacation_used  = db.Column(db.Integer, nullable=False, default=0)
    prev_balance   = db.Column(db.Numeric(6, 1), nullable=False, default=0)
    manual_adj     = db.Column(db.Numeric(6, 1), nullable=False, default=0)
    balance        = db.Column(db.Numeric(6, 1), nullable=False, default=0)
    adjusted_by    = db.Column(db.Integer, db.ForeignKey("user.id"))
    adjusted_at    = db.Column(db.DateTime)
    created_at     = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    user     = db.relationship("Users", foreign_keys=[user_id], lazy="joined")
    period   = db.relationship("AttendancePeriod", lazy="joined")

    __table_args__ = (
        db.UniqueConstraint('user_id', 'period_id', name='uq_leave_bal_user_period'),
    )


class LeaveAttachment(BaseModel):
    """Archivos adjuntos a solicitudes de leave (ej: certificados médicos)"""
    __tablename__ = 'leave_attachment'

    id               = db.Column(db.Integer, autoincrement=True, primary_key=True)
    leave_request_id = db.Column(db.Integer, db.ForeignKey("leave_request.id"), nullable=False)
    original_name    = db.Column(db.String(255), nullable=False)
    stored_name      = db.Column(db.String(255), nullable=False)
    mime_type        = db.Column(db.String(120))
    size_bytes       = db.Column(db.Integer, nullable=False, default=0)
    uploaded_by      = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    uploaded_at      = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    leave_request = db.relationship("LeaveRequest", foreign_keys=[leave_request_id], lazy="joined")
    uploader      = db.relationship("Users", foreign_keys=[uploaded_by], lazy="joined")