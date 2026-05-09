"""
Authentication routes — register, login, logout, and current-user profile.
"""
from flask import Blueprint, request
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import jwt_required_middleware, get_current_user_id
from app.utils.response_handler import success_response, error_response

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data: dict = request.get_json(silent=True) or {}
    user, err = AuthService.register(data)
    if err:
        return error_response(err, 400)
    return success_response(user, "Registration successful.", 201)


@auth_bp.post("/login")
def login():
    data: dict = request.get_json(silent=True) or {}
    token, user, err = AuthService.login(data.get("email", ""), data.get("password", ""))
    if err:
        return error_response(err, 401)
    return success_response({"access_token": token, "user": user}, "Login successful.")


@auth_bp.post("/logout")
@jwt_required_middleware
def logout():
    # JWT is stateless; client discards the token.
    # For token revocation, integrate a blocklist (e.g. Redis).
    return success_response(message="Logged out successfully.")


@auth_bp.get("/me")
@jwt_required_middleware
def me():
    user = AuthService.get_user_by_id(get_current_user_id())
    if not user:
        return error_response("User not found.", 404)
    return success_response(user.to_dict())
