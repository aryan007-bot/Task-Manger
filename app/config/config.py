"""
Centralized configuration using environment variables.
All secrets and credentials are read from the environment — never hardcoded.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


def normalize_database_url(database_url: str | None) -> str:
    """Normalize common platform database URLs for SQLAlchemy."""
    database_url = (database_url or "").strip()
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return database_url


class Config:
    """Base configuration shared across all environments."""

    # --- Core ---
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")
    DEBUG: bool = False
    TESTING: bool = False

    # --- Database ---
    DATABASE_URL: str = normalize_database_url(os.environ.get("DATABASE_URL"))
    REQUIRE_DATABASE_URL: bool = False
    SQLALCHEMY_DATABASE_URI: str = DATABASE_URL or "sqlite:///task_manager.db"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # --- JWT ---
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=1)
    JWT_TOKEN_LOCATION: list = ["headers", "cookies"]
    JWT_COOKIE_SECURE: bool = False
    JWT_COOKIE_CSRF_PROTECT: bool = False

    # --- SocketIO ---
    SOCKETIO_ASYNC_MODE: str = "eventlet"

    # --- Security headers ---
    WTF_CSRF_ENABLED: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"


class DevelopmentConfig(Config):
    DEBUG: bool = True
    JWT_COOKIE_SECURE: bool = False


class ProductionConfig(Config):
    DEBUG: bool = False
    REQUIRE_DATABASE_URL: bool = True
    JWT_COOKIE_SECURE: bool = True
    JWT_COOKIE_CSRF_PROTECT: bool = True


class TestingConfig(Config):
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    JWT_SECRET_KEY: str = "test-secret"


config_map: dict = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config() -> type[Config]:
    env = os.environ.get("FLASK_ENV", "default")
    return config_map.get(env, DevelopmentConfig)
