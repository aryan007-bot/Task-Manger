"""
Authentication middleware — JWT verification helpers and decorators.
"""
from functools import wraps
from flask import request, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.utils.response_handler import error_response


def jwt_required_middleware(fn):
    """Decorator that validates JWT and injects current user id into g."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            g.current_user_id = int(get_jwt_identity())
        except Exception as exc:
            return error_response("Authentication required. Please log in.", 401)
        return fn(*args, **kwargs)
    return wrapper


def get_current_user_id() -> int:
    """Return authenticated user id from Flask g (set by jwt_required_middleware)."""
    return g.current_user_id
