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


class WorkProfile(BaseModel):
    __tablename__ = "attendance_profile"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(80), unique=True)
    is_active = db.Column(db.Boolean, default=True)

    shifts = db.relationship("WorkProfileShift", lazy="joined", backref="profile")


class WorkProfileShift(BaseModel):
    __tablename__ = "attendance_profile_shift"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("attendance_profile.id"), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)


class UserWorkProfile(BaseModel):
    __tablename__ = "attendance_user_profile"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey("attendance_profile.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)

    profile = db.relationship("WorkProfile", lazy="joined")
