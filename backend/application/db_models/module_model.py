from application.db_models.base_model import db, BaseModel


PERU_NOW = db.text("(NOW() - INTERVAL 5 HOUR)")


class Module(BaseModel):
    __tablename__ = 'modules'

    id         = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    slug       = db.Column(db.String(50), unique=True, nullable=False)
    name       = db.Column(db.String(100), nullable=False)
    icon       = db.Column(db.String(50))
    sort_order = db.Column(db.Integer, default=0)
    is_active  = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, server_default=PERU_NOW)

    permissions = db.relationship("ModulePermission", backref="module", lazy="joined")


class ModulePermission(BaseModel):
    __tablename__ = 'module_permissions'

    id          = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    module_id   = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    slug        = db.Column(db.String(50), nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at  = db.Column(db.TIMESTAMP, server_default=PERU_NOW)

    __table_args__ = (
        db.UniqueConstraint('module_id', 'slug', name='uq_module_permission_slug'),
    )


class UserModuleAccess(BaseModel):
    __tablename__ = 'user_module_access'

    id              = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id         = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_id       = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    visible         = db.Column(db.Boolean, default=False)
    is_default      = db.Column(db.Boolean, default=False)
    is_pinned       = db.Column(db.Boolean, default=True)
    user_sort_order = db.Column(db.Integer, default=0)
    created_at      = db.Column(db.TIMESTAMP, server_default=PERU_NOW)
    updated_at      = db.Column(db.TIMESTAMP, server_default=PERU_NOW)

    module = db.relationship("Module", lazy="joined")
    user   = db.relationship("Users", lazy="select", foreign_keys=[user_id])

    __table_args__ = (
        db.UniqueConstraint('user_id', 'module_id', name='uq_user_module_access'),
    )


class UserModulePermission(BaseModel):
    __tablename__ = 'user_module_permissions'

    id                   = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id              = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_permission_id = db.Column(db.Integer, db.ForeignKey('module_permissions.id'), nullable=False)
    granted              = db.Column(db.Boolean, default=False)
    created_at           = db.Column(db.TIMESTAMP, server_default=PERU_NOW)
    updated_at           = db.Column(db.TIMESTAMP, server_default=PERU_NOW)

    permission = db.relationship("ModulePermission", lazy="joined")

    __table_args__ = (
        db.UniqueConstraint('user_id', 'module_permission_id', name='uq_user_module_permission'),
    )