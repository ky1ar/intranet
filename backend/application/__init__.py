import logging
from gevent import monkey
monkey.patch_all()

import redis
import firebase_admin
from firebase_admin import credentials
from flask import Flask, g, request
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from config import Config, Redis


app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

socketio = SocketIO(
    app,
    async_mode='gevent',
    cors_allowed_origins='*'
)

CORS(
    app,
    resources={r"/*": {"origins": "*"}}
)

redis_client = redis.StrictRedis.from_url(Redis.URL, decode_responses=True)
cred = credentials.Certificate('serviceAccountKey.json')
firebase_app = firebase_admin.initialize_app(cred)


from application.routes.dev_routes import dev_bp
from application.routes.user_routes import user_bp
from application.routes.clients_routes import client_bp
from application.routes.machine_routes import machine_bp
from application.routes.logistic_routes import logistic_bp
from application.routes.support_routes import support_bp
from application.routes.training_routes import training_bp
from application.routes.tracking_routes import tracking_bp
from application.routes.general_routes import general_bp
from application.routes.board_routes import board_bp
from application.routes.schedule_routes import schedule_bp
from application.routes.purchase_routes import purchase_bp
from application.routes.attendance_routes import attendance_bp
from application.routes.odoo_routes import odoo_bp
from application.routes.complaint_routes import complaint_bp
from application.routes.import_routes import import_bp
from application.routes.common_routes import common_bp
from application.routes.warehouse_routes import warehouse_bp
from application.routes.module_routes import module_bp
from application.routes.safebuy_routes import safebuy_bp
from application.routes.refund_routes import refund_bp
from application.routes.approval_routes import approval_bp
from application.routes.guide_routes import guide_bp
from application.routes.conversation_routes import conversation_bp
from application.routes.analytics_routes import analytics_bp
from application.routes.wordpress_routes import wordpress_bp


app.register_blueprint(dev_bp)
app.register_blueprint(user_bp)
app.register_blueprint(client_bp)
app.register_blueprint(machine_bp)
app.register_blueprint(logistic_bp)
app.register_blueprint(support_bp)
app.register_blueprint(training_bp)
app.register_blueprint(tracking_bp)
app.register_blueprint(general_bp)
app.register_blueprint(board_bp)
app.register_blueprint(schedule_bp)
app.register_blueprint(purchase_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(odoo_bp)
app.register_blueprint(complaint_bp)
app.register_blueprint(import_bp)
app.register_blueprint(common_bp)
app.register_blueprint(warehouse_bp)
app.register_blueprint(module_bp)
app.register_blueprint(safebuy_bp)
app.register_blueprint(refund_bp)
app.register_blueprint(approval_bp)
app.register_blueprint(guide_bp)
app.register_blueprint(conversation_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(wordpress_bp)


def api_key_required():
    if request.path == '/':
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        return None


@app.before_request
def before_request():
    if request.path == "/":
        log = logging.getLogger("werkzeug")

        log.setLevel(logging.ERROR)

    # pool_pre_ping (config.py) valida la conexión al sacarla del pool,
    # así que aquí solo dejamos lista la sesión que usan los repos.
    if not hasattr(g, "db_session"):
        g.db_session = db.session


@app.teardown_request
def teardown_request(exception=None):
    db_session = getattr(g, 'db_session', None)
    if db_session:
        db_session.remove()


@socketio.on_error_default
def default_error_handler(e):
    logging.info(f"[SocketIO ERROR] {str(e)}")