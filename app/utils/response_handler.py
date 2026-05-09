"""
Standardized JSON response helpers — consistent envelope across all endpoints.
"""
from flask import jsonify
from typing import Any


def success_response(data: Any = None, message: str = "Success", status_code: int = 200):
    payload = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


def error_response(message: str = "An error occurred", status_code: int = 400, errors: Any = None):
    payload = {"success": False, "message": message}
    if errors is not None:
        payload["errors"] = errors
    return jsonify(payload), status_code


def paginated_response(items: list, total: int, page: int, per_page: int, message: str = "Success"):
    return jsonify({
        "success": True,
        "message": message,
        "data": items,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        },
    }), 200
