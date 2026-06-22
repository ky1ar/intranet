from application.db_models.base_model import db, BaseModel


PERU_NOW = db.text("(NOW() - INTERVAL 5 HOUR)")


class AuditRoute(BaseModel):
    __tablename__ = 'audit_routes'

    id         = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    route      = db.Column(db.String(255), nullable=False)
    device_id  = db.Column(db.String(64), index=True)
    ip         = db.Column(db.String(64))
    user_agent = db.Column(db.String(255))
    visited_at = db.Column(db.TIMESTAMP, server_default=PERU_NOW, index=True)


class AuditAttendanceMonitor(BaseModel):
    __tablename__ = 'audit_attendance_monitor'

    id             = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    viewer_id      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    target_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    viewed_at      = db.Column(db.TIMESTAMP, server_default=PERU_NOW, index=True)
