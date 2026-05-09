"""
General-purpose helpers used across the application.
"""
from datetime import datetime, timezone
from typing import Any


def parse_int(value: Any, default: int = 1, min_val: int = 1, max_val: int = 1000) -> int:
    try:
        result = int(value)
        return max(min_val, min(result, max_val))
    except (TypeError, ValueError):
        return default


def parse_pagination(args: dict) -> tuple[int, int]:
    page = parse_int(args.get("page", 1), default=1, min_val=1)
    per_page = parse_int(args.get("per_page", 20), default=20, min_val=1, max_val=100)
    return page, per_page


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso_to_datetime(iso_str: str | None) -> datetime | None:
    if not iso_str:
        return None
    try:
        return datetime.fromisoformat(iso_str)
    except ValueError:
        return None
