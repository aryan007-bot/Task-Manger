"""
User model — normalized schema with hashed passwords, timestamps, and cascade.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from app.extensions import db

if TYPE_CHECKING:
    from app.models.task_model import Task


class User(db.Model):
    __tablename__ = "users"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name: str = db.Column(db.String(128), nullable=False)
    email: str = db.Column(db.String(256), unique=True, nullable=False, index=True)
    password_hash: str = db.Column(db.String(512), nullable=False)
    created_at: datetime = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship — cascade delete removes all tasks when user is deleted
    tasks = db.relationship("Task", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
