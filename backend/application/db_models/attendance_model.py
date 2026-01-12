from application.db_models.base import db, BaseModel


class AttendanceMark(BaseModel):
    __tablename__ = "attendance_mark"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    mark_at = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("Users", lazy="joined", foreign_keys=[user_id])


class AttendancePeriod(BaseModel):
    __tablename__ = "attendance_period"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)


# class Profile(BaseModel):
#     __tablename__ = "attendance_profile"

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(80), unique=True, nullable=False)
#     start_time = db.Column(db.Time, nullable=False)


# class ProfileRule(BaseModel):
#     __tablename__ = "attendance_profile_rule"

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     profile_id = db.Column(db.Integer, db.ForeignKey("attendance_profile.id"), nullable=False)
#     dow = db.Column(db.Integer, nullable=False)
#     expected_minutes = db.Column(db.Integer, nullable=False, default=0)

#     profile = db.relationship("WorkProfile", lazy="joined", foreign_keys=[profile_id])




# class AttendanceDaySummary(BaseModel):
#     __tablename__ = "attendance_day_summary"
#     __table_args__ = (
#         db.UniqueConstraint('user_id', 'date', name='uq_user_date'),
#         db.Index('idx_ads_user_date', 'user_id', 'date'),
#     )
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
#     date = db.Column(db.Date, nullable=False)

#     worked_minutes = db.Column(db.Integer, nullable=False, default=0)
#     expected_minutes = db.Column(db.Integer, nullable=False, default=0)
#     delta_minutes = db.Column(db.Integer, nullable=False, default=0)
#     is_open = db.Column(db.Boolean, nullable=False, default=False)

#     first_check_in = db.Column(db.DateTime)
#     last_check_out = db.Column(db.DateTime)
#     tardiness_minutes = db.Column(db.Integer, nullable=False, default=0)

#     status = db.Column(db.String(20), default="normal")  # normal|salud|servicio|vacaciones|feriado|falta|modificado
#     created_at = db.Column(db.DateTime, server_default=db.func.now())
#     updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())


# class AttendancePeriod(BaseModel):
#     __tablename__ = "attendance_period"
#     __table_args__ = (
#         db.CheckConstraint('start_date <= end_date', name='ck_period_range'),
#         db.Index('idx_period_start_end', 'start_date', 'end_date'),
#     )
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(120), nullable=False)
#     start_date = db.Column(db.Date, nullable=False)
#     end_date = db.Column(db.Date, nullable=False)
#     tolerance_percent = db.Column(db.Float, nullable=False, default=1.0)  # p.ej. 1%
#     is_closed = db.Column(db.Boolean, nullable=False, default=False)
#     closed_at = db.Column(db.DateTime)

#     created_at = db.Column(db.DateTime, server_default=db.func.now())
#     updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
