"""
Analytics service — uses Pandas and NumPy to derive insights from task data.
All computation is done in-memory on the current user's dataset.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from app.models.task_model import Task


class AnalyticsService:

    @staticmethod
    def get_analytics(user_id: int) -> dict:
        tasks = Task.query.filter_by(user_id=user_id).all()

        if not tasks:
            return AnalyticsService._empty_analytics()

        rows = [
            {
                "id": t.id,
                "title": t.title,
                "priority": t.priority,
                "status": t.status,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
            }
            for t in tasks
        ]
        df = pd.DataFrame(rows)
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
        df["updated_at"] = pd.to_datetime(df["updated_at"], utc=True)

        total: int = int(len(df))
        completed: int = int((df["status"] == "completed").sum())
        pending: int = int((df["status"] == "pending").sum())
        in_progress: int = int((df["status"] == "in_progress").sum())
        completion_pct: float = float(
            np.round((completed / total) * 100, 2) if total > 0 else 0.0
        )

        # Priority distribution
        priority_counts = df["priority"].value_counts().to_dict()
        priority_distribution = {
            "low": int(priority_counts.get("low", 0)),
            "medium": int(priority_counts.get("medium", 0)),
            "high": int(priority_counts.get("high", 0)),
        }

        # Weekly trend — tasks created per day (last 7 days)
        now = pd.Timestamp.now(tz="UTC")
        week_ago = now - pd.Timedelta(days=6)
        recent = df[df["created_at"] >= week_ago].copy()
        recent["day"] = recent["created_at"].dt.strftime("%Y-%m-%d")
        trend_series = recent.groupby("day").size()
        # Fill missing days with 0
        date_range = pd.date_range(week_ago.normalize(), now.normalize(), freq="D")
        date_labels = [d.strftime("%Y-%m-%d") for d in date_range]
        task_trend = [int(trend_series.get(d, 0)) for d in date_labels]

        # Average tasks per day (NumPy)
        avg_per_day: float = float(np.mean(task_trend)) if task_trend else 0.0

        # Completion rate by priority
        completion_by_priority: dict = {}
        for p in ["low", "medium", "high"]:
            subset = df[df["priority"] == p]
            if len(subset) > 0:
                rate = float(np.round((subset["status"] == "completed").sum() / len(subset) * 100, 1))
            else:
                rate = 0.0
            completion_by_priority[p] = rate

        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "in_progress_tasks": in_progress,
            "completion_percentage": completion_pct,
            "priority_distribution": priority_distribution,
            "task_trend": {
                "labels": date_labels,
                "values": task_trend,
            },
            "avg_tasks_per_day": float(np.round(avg_per_day, 2)),
            "completion_by_priority": completion_by_priority,
        }

    @staticmethod
    def _empty_analytics() -> dict:
        return {
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "in_progress_tasks": 0,
            "completion_percentage": 0.0,
            "priority_distribution": {"low": 0, "medium": 0, "high": 0},
            "task_trend": {"labels": [], "values": []},
            "avg_tasks_per_day": 0.0,
            "completion_by_priority": {"low": 0.0, "medium": 0.0, "high": 0.0},
        }
