"""
Task CRUD routes with pagination, filtering, sorting, and real-time SocketIO broadcast.
"""
from flask import Blueprint, request
from app.services.task_service import TaskService
from app.middleware.auth_middleware import jwt_required_middleware, get_current_user_id
from app.utils.response_handler import success_response, error_response, paginated_response
from app.utils.helpers import parse_pagination
from app.extensions import socketio

task_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


def _broadcast(event: str, payload: dict) -> None:
    socketio.emit(event, payload, namespace="/tasks")


@task_bp.get("")
@jwt_required_middleware
def list_tasks():
    uid = get_current_user_id()
    page, per_page = parse_pagination(request.args)
    tasks, total = TaskService.get_tasks(
        user_id=uid,
        page=page,
        per_page=per_page,
        status=request.args.get("status"),
        priority=request.args.get("priority"),
        search=request.args.get("search"),
        sort_by=request.args.get("sort_by", "created_at"),
        sort_order=request.args.get("sort_order", "desc"),
    )
    return paginated_response(tasks, total, page, per_page)


@task_bp.get("/<int:task_id>")
@jwt_required_middleware
def get_task(task_id: int):
    uid = get_current_user_id()
    task = TaskService.get_task(task_id, uid)
    if not task:
        return error_response("Task not found.", 404)
    return success_response(task.to_dict())


@task_bp.post("")
@jwt_required_middleware
def create_task():
    uid = get_current_user_id()
    data: dict = request.get_json(silent=True) or {}
    task, err = TaskService.create_task(uid, data)
    if err:
        return error_response(err, 400)
    _broadcast("task_created", task)
    return success_response(task, "Task created.", 201)


@task_bp.put("/<int:task_id>")
@jwt_required_middleware
def update_task(task_id: int):
    uid = get_current_user_id()
    data: dict = request.get_json(silent=True) or {}
    task, err = TaskService.update_task(task_id, uid, data)
    if err:
        status = 404 if err == "Task not found." else 400
        return error_response(err, status)
    _broadcast("task_updated", task)
    return success_response(task, "Task updated.")


@task_bp.delete("/<int:task_id>")
@jwt_required_middleware
def delete_task(task_id: int):
    uid = get_current_user_id()
    ok, err = TaskService.delete_task(task_id, uid)
    if not ok:
        return error_response(err, 404)
    _broadcast("task_deleted", {"id": task_id})
    return success_response(message="Task deleted.")
