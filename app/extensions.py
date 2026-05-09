"""
Flask extensions — initialized here, bound to app in create_app().
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

db: SQLAlchemy = SQLAlchemy()
migrate: Migrate = Migrate()
jwt: JWTManager = JWTManager()
socketio: SocketIO = SocketIO(cors_allowed_origins="*", async_mode="eventlet")
