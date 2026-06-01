"""
Modelos ORM de la plataforma de cursos (cursos.krear3d.com), accedidos vía el
bind 'courses' de Flask-SQLAlchemy (ver SQLALCHEMY_BINDS en config.py).

Es OTRA base de datos: por usar __bind_key__='courses', Flask-SQLAlchemy 3.x
ubica estas tablas en un MetaData propio, así que la tabla `clients` de cursos
NO colisiona con la `clients` del intranet.

Solo se mapean las columnas que necesitamos para crear la cuenta y otorgar el
curso (lectura/escritura parcial). Esquema espejo de courses/application/models.py.
"""
from application.db_models.base_model import db, BaseModel


class CourseAccount(BaseModel):
    __bind_key__ = "courses"
    __tablename__ = "clients"

    id         = db.Column(db.String(36), primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name  = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(255))
    password   = db.Column(db.String(255), nullable=False)
    status     = db.Column(db.String(24), nullable=False, default="ACTIVE")
    language   = db.Column(db.String(2))
    country_id = db.Column(db.Integer)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    change_pass = db.Column(db.Boolean, nullable=False, default=False)
    

class Course(BaseModel):
    __bind_key__ = "courses"
    __tablename__ = "courses"

    uuid     = db.Column(db.String(36), primary_key=True)
    slug     = db.Column(db.String(255), unique=True, nullable=False)
    name     = db.Column(db.String(255), nullable=False)
    has_lite = db.Column(db.Integer, default=0)


class CoursePurchase(BaseModel):
    __bind_key__ = "courses"
    __tablename__ = "purchases"

    id          = db.Column(db.Integer, primary_key=True)
    client_id   = db.Column(db.String(36), nullable=False)
    course_uuid = db.Column(db.String(36), nullable=False)
    is_lite     = db.Column(db.Integer, nullable=False)
    created_at  = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())


class CourseCountry(BaseModel):
    __bind_key__ = "courses"
    __tablename__ = "countries"

    id  = db.Column(db.Integer, primary_key=True)
    iso = db.Column(db.String(2), nullable=False)
