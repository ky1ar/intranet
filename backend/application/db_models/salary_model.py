from application.db_models.base_model import db, BaseModel


class AttendancePeriodStats(BaseModel):
    __tablename__ = "attendance_period_stats"

    id                    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id               = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    period_id             = db.Column(db.Integer, db.ForeignKey("attendance_period.id"), nullable=False)
    target_min            = db.Column(db.Integer, nullable=False, default=0)
    worked_min            = db.Column(db.Integer, nullable=False, default=0)
    tolerance_planned_min = db.Column(db.Integer, nullable=False, default=0)
    tolerance_accum_min   = db.Column(db.Integer, nullable=False, default=0)
    base_excess_min       = db.Column(db.Integer, nullable=False, default=0)
    calc_excess_min       = db.Column(db.Integer, nullable=False, default=0)
    calc_obj_min          = db.Column(db.Integer, nullable=False, default=0)
    tardiness_count       = db.Column(db.Integer, nullable=False, default=0)
    vacation_days         = db.Column(db.Integer, nullable=False, default=0)
    incomplete_days       = db.Column(db.Integer, nullable=False, default=0)
    compliance_pct        = db.Column(db.Numeric(6, 2), nullable=False, default=0)
    calculated_at         = db.Column(db.DateTime, nullable=False)
    calculated_by         = db.Column(db.Integer, db.ForeignKey("user.id"))

    user   = db.relationship("Users", foreign_keys=[user_id], lazy="joined")
    period = db.relationship("AttendancePeriod", lazy="joined")

    __table_args__ = (
        db.UniqueConstraint('user_id', 'period_id', name='uq_stats_user_period'),
    )


class SalaryConfig(BaseModel):
    __tablename__ = "salary_config"

    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    business_id    = db.Column(db.Integer, db.ForeignKey("import_business.id"), nullable=False)
    base_salary    = db.Column(db.Numeric(10, 2), nullable=False)
    currency       = db.Column(db.String(3), nullable=False, default="PEN")
    effective_from = db.Column(db.Date, nullable=False)
    effective_to   = db.Column(db.Date)
    created_at     = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    user     = db.relationship("Users", lazy="joined")
    business = db.relationship("ImportBusiness", lazy="joined")


class SalaryPeriod(BaseModel):
    __tablename__ = "salary_period"

    id               = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id          = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    period_id        = db.Column(db.Integer, db.ForeignKey("attendance_period.id"), nullable=False)
    stats_id         = db.Column(db.Integer, db.ForeignKey("attendance_period_stats.id"), nullable=False)
    business_id      = db.Column(db.Integer, db.ForeignKey("import_business.id"), nullable=False)
    base_salary      = db.Column(db.Numeric(10, 2), nullable=False)
    compliance_pct   = db.Column(db.Numeric(6, 2), nullable=False)
    factor           = db.Column(db.Numeric(6, 4), nullable=False)
    final_salary     = db.Column(db.Numeric(10, 2), nullable=False)
    adjustment       = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status           = db.Column(db.String(16), nullable=False, default="draft")
    rrhh_approved_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    rrhh_approved_at = db.Column(db.DateTime)
    mgr_approved_by  = db.Column(db.Integer, db.ForeignKey("user.id"))
    mgr_approved_at  = db.Column(db.DateTime)
    approved_by      = db.Column(db.Integer, db.ForeignKey("user.id"))
    approved_at      = db.Column(db.DateTime)
    created_at       = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    user     = db.relationship("Users", foreign_keys=[user_id], lazy="joined")
    period   = db.relationship("AttendancePeriod", lazy="joined")
    stats    = db.relationship("AttendancePeriodStats", lazy="joined")
    business = db.relationship("ImportBusiness", lazy="joined")

    __table_args__ = (
        db.UniqueConstraint('user_id', 'period_id', name='uq_salary_user_period'),
    )


class UserBankAccount(BaseModel):
    __tablename__ = "user_bank_account"

    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    business_id     = db.Column(db.Integer, db.ForeignKey("import_business.id"), nullable=False)
    account_type    = db.Column(db.String(1), nullable=False, default="A")
    account_number  = db.Column(db.String(20), nullable=False)
    doc_type        = db.Column(db.String(1), nullable=False, default="1")
    currency        = db.Column(db.String(1), nullable=False, default="S")
    is_active       = db.Column(db.Boolean, nullable=False, default=True)
    created_at      = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    user     = db.relationship("Users", lazy="joined")
    business = db.relationship("ImportBusiness", lazy="joined")


class BusinessBankConfig(BaseModel):
    __tablename__ = "business_bank_config"

    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    business_id     = db.Column(db.Integer, db.ForeignKey("import_business.id"), nullable=False)
    account_type    = db.Column(db.String(1), nullable=False, default="C")
    account_number  = db.Column(db.String(20), nullable=False)
    company_code    = db.Column(db.String(20), nullable=False)
    reference       = db.Column(db.String(40), nullable=False, default="Referencia Haberes")

    business = db.relationship("ImportBusiness", lazy="joined")