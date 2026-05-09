"""
Task model — supports priority/status enums, full-text search via index, timestamps.
"""
from datetime import datetime, timezone
import enum

from app.extensions import db


class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Task(db.Model):
    __tablename__ = "tasks"
    __table_args__ = (
        db.Index("ix_tasks_user_status", "user_id", "status"),
        db.Index("ix_tasks_user_priority", "user_id", "priority"),
    )

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title: str = db.Column(db.String(256), nullable=False)
    description: str = db.Column(db.Text, nullable=True)
    priority: str = db.Column(
        db.Enum(Priority, values_callable=lambda x: [e.value for e in x]),
        default=Priority.MEDIUM.value,
        nullable=False,
    )
    status: str = db.Column(
        db.Enum(Status, values_callable=lambda x: [e.value for e in x]),
        default=Status.PENDING.value,
        nullable=False,
    )
    deadline: datetime | None = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at: datetime = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user_id: int = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user = db.relationship("User", back_populates="tasks")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": self.user_id,
        }

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} status={self.status}>"
