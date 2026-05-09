"""
Task service — all CRUD operations isolated from route handlers.
"""
from app.extensions import db
from app.models.task_model import Task, Priority, Status
from app.utils.validators import validate_task, sanitize_string
from app.utils.helpers import parse_pagination, iso_to_datetime


class TaskService:

    @staticmethod
    def get_tasks(
        user_id: int,
        page: int = 1,
        per_page: int = 20,
        status: str | None = None,
        priority: str | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[dict], int]:
        """Return paginated, filtered task list for a user."""
        query = Task.query.filter_by(user_id=user_id)

        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if search:
            term = f"%{search}%"
            query = query.filter(
                (Task.title.ilike(term)) | (Task.description.ilike(term))
            )

        allowed_sort = {"created_at", "updated_at", "priority", "status", "title"}
        if sort_by not in allowed_sort:
            sort_by = "created_at"

        col = getattr(Task, sort_by)
        query = query.order_by(col.desc() if sort_order == "desc" else col.asc())

        total = query.count()
        tasks = query.offset((page - 1) * per_page).limit(per_page).all()
        return [t.to_dict() for t in tasks], total

    @staticmethod
    def get_task(task_id: int, user_id: int) -> Task | None:
        return Task.query.filter_by(id=task_id, user_id=user_id).first()

    @staticmethod
    def create_task(user_id: int, data: dict) -> tuple[dict | None, str | None]:
        errors = validate_task(data, is_update=False)
        if errors:
            return None, "; ".join(errors)

        task = Task(
            title=sanitize_string(data["title"]),
            description=sanitize_string(data.get("description", "")),
            priority=data.get("priority", Priority.MEDIUM.value),
            status=data.get("status", Status.PENDING.value),
            deadline=iso_to_datetime(data.get("deadline")),
            user_id=user_id,
        )
        db.session.add(task)
        db.session.commit()
        return task.to_dict(), None

    @staticmethod
    def update_task(task_id: int, user_id: int, data: dict) -> tuple[dict | None, str | None]:
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return None, "Task not found."

        errors = validate_task(data, is_update=True)
        if errors:
            return None, "; ".join(errors)

        if "title" in data:
            task.title = sanitize_string(data["title"])
        if "description" in data:
            task.description = sanitize_string(data["description"])
        if "priority" in data:
            task.priority = data["priority"]
        if "status" in data:
            task.status = data["status"]
        if "deadline" in data:
            task.deadline = iso_to_datetime(data["deadline"])

        db.session.commit()
        return task.to_dict(), None

    @staticmethod
    def delete_task(task_id: int, user_id: int) -> tuple[bool, str | None]:
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return False, "Task not found."
        db.session.delete(task)
        db.session.commit()
        return True, None

    @staticmethod
    def get_all_tasks_for_user(user_id: int) -> list[Task]:
        return Task.query.filter_by(user_id=user_id).all()
