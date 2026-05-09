"""
Input validation utilities — reusable across all routes.
"""
import re
from typing import Any


EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"pending", "in_progress", "completed"}


def validate_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))


def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit."
    return True, ""


def validate_registration(data: dict) -> list[str]:
    errors: list[str] = []
    if not data.get("full_name", "").strip():
        errors.append("full_name is required.")
    if not data.get("email", "").strip():
        errors.append("email is required.")
    elif not validate_email(data["email"]):
        errors.append("email is not valid.")
    if not data.get("password", ""):
        errors.append("password is required.")
    else:
        ok, msg = validate_password(data["password"])
        if not ok:
            errors.append(msg)
    return errors


def validate_task(data: dict, is_update: bool = False) -> list[str]:
    errors: list[str] = []
    if not is_update:
        if not data.get("title", "").strip():
            errors.append("title is required.")
    else:
        if "title" in data and not data["title"].strip():
            errors.append("title cannot be empty.")

    if "priority" in data and data["priority"] not in VALID_PRIORITIES:
        errors.append(f"priority must be one of: {', '.join(VALID_PRIORITIES)}.")
    if "status" in data and data["status"] not in VALID_STATUSES:
        errors.append(f"status must be one of: {', '.join(VALID_STATUSES)}.")
    return errors


def sanitize_string(value: Any, max_length: int = 512) -> str:
    """Strip whitespace and cap length to prevent oversized inputs."""
    if not isinstance(value, str):
        return ""
    return value.strip()[:max_length]
