import logging
import eventlet
import redis

eventlet.monkey_patch()

from config import Config, Redis
from flask import Flask, g, request
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins='*')
redis_client = redis.StrictRedis.from_url(Redis.URL, decode_responses=True)
CORS(app, resources={r"/*": {"origins": "*"}})


from application.routes.user_routes import user_bp
from application.routes.clients_routes import clients_bp
from application.routes.machine_routes import machine_bp
from application.routes.logistic_routes import logistic_bp
from application.routes.support_routes import support_bp
from application.routes.training_routes import training_bp
from application.routes.tracking_routes import tracking_bp
from application.routes.general_routes import general_bp
from application.routes.order_routes import order_bp


app.register_blueprint(user_bp)
app.register_blueprint(clients_bp)
app.register_blueprint(machine_bp)
app.register_blueprint(logistic_bp)
app.register_blueprint(support_bp)
app.register_blueprint(training_bp)
app.register_blueprint(tracking_bp)
app.register_blueprint(general_bp)
app.register_blueprint(order_bp)



def api_key_required():
    if request.path == '/':
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        return None
    

def reconnect_db():
    if not hasattr(g, "db_session"):
        g.db_session = db.session

    try:
        g.db_session.execute(text("SELECT 1")) 
    except OperationalError:
        db.engine.dispose() 
        g.db_session.remove()
        g.db_session = db.session


@app.before_request
def before_request():
    if request.path == "/":
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)

    reconnect_db()


@app.teardown_request
def teardown_request(exception=None):
    db_session = getattr(g, 'db_session', None)
    if db_session:
        db_session.remove()