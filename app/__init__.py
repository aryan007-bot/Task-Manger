"""
Application factory — wires up all Flask extensions, blueprints, and SocketIO handlers.
"""
from flask import Flask
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

from app.config.config import get_config
from app.extensions import db, migrate, jwt, socketio


def create_app(config_class=None) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Load config
    cfg = config_class or get_config()
    app.config.from_object(cfg)

    database_url = app.config.get("DATABASE_URL")
    database_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    if app.config.get("REQUIRE_DATABASE_URL") and not database_url:
        raise RuntimeError(
            "DATABASE_URL is required when FLASK_ENV=production. "
            "On Render, attach a Postgres database and set DATABASE_URL from "
            "fromDatabase.connectionString."
        )

    try:
        make_url(database_uri)
    except ArgumentError as exc:
        raise RuntimeError(
            "DATABASE_URL is not a valid SQLAlchemy database URL. "
            "Expected a value like postgresql://user:password@host:5432/database."
        ) from exc

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # Import models so SQLAlchemy can discover them
    with app.app_context():
        from app.models import user_model, task_model  # noqa: F401
        db.create_all()

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.task_routes import task_bp
    from app.routes.analytics_routes import analytics_bp
    from app.routes.frontend_routes import frontend_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(frontend_bp)

    # Register SocketIO event handlers
    from app.sockets import socket_events  # noqa: F401

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    return app
