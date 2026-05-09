"""
Authentication service — registration, login, and password hashing logic.
All business logic lives here; routes are thin.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models.user_model import User
from app.utils.validators import validate_registration


class AuthService:

    @staticmethod
    def register(data: dict) -> tuple[dict | None, str | None]:
        """Register a new user. Returns (user_dict, error_message)."""
        errors = validate_registration(data)
        if errors:
            return None, "; ".join(errors)

        email = data["email"].strip().lower()
        if User.query.filter_by(email=email).first():
            return None, "A user with this email already exists."

        password_hash = generate_password_hash(data["password"])
        user = User(
            full_name=data["full_name"].strip(),
            email=email,
            password_hash=password_hash,
        )
        db.session.add(user)
        db.session.commit()
        return user.to_dict(), None

    @staticmethod
    def login(email: str, password: str) -> tuple[str | None, dict | None, str | None]:
        """Authenticate user. Returns (access_token, user_dict, error_message)."""
        if not email or not password:
            return None, None, "Email and password are required."

        user = User.query.filter_by(email=email.strip().lower()).first()
        if not user or not check_password_hash(user.password_hash, password):
            return None, None, "Invalid email or password."

        token = create_access_token(identity=str(user.id))
        return token, user.to_dict(), None

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        return User.query.get(user_id)
