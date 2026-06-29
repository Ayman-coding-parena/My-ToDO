"""Core to-do logic: tasks stored as a list of dictionaries, persisted to JSON."""

import json
from datetime import datetime, timezone
from pathlib import Path

TASKS_FILE = Path(__file__).resolve().parent / "tasks.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _empty_store() -> dict:
    return {"next_id": 1, "tasks": []}


class TodoManager:
    def __init__(self, filepath: Path | None = None):
        self.filepath = filepath or TASKS_FILE
        self._data = _empty_store()
        self.load()

    @property
    def tasks(self) -> list[dict]:
        return self._data["tasks"]

    def load(self) -> None:
        if not self.filepath.exists():
            self._data = _empty_store()
            return
        try:
            with self.filepath.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            if not isinstance(raw, dict) or "tasks" not in raw:
                self._data = _empty_store()
                return
            self._data = {
                "next_id": int(raw.get("next_id", 1)),
                "tasks": list(raw.get("tasks", [])),
            }
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            self._data = _empty_store()

    def save(self) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with self.filepath.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def _persist(self) -> None:
        self.save()

    def _find_index(self, task_id: int) -> int | None:
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                return i
        return None

    def get_task(self, task_id: int) -> dict | None:
        idx = self._find_index(task_id)
        return self.tasks[idx] if idx is not None else None

    def add_task(self, title: str, description: str = "") -> dict:
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty.")
        task = {
            "id": self._data["next_id"],
            "title": title,
            "description": description.strip(),
            "completed": False,
            "created_at": _now_iso(),
        }
        self._data["next_id"] += 1
        self.tasks.append(task)
        self._persist()
        return task

    def delete_task(self, task_id: int) -> dict:
        idx = self._find_index(task_id)
        if idx is None:
            raise ValueError(f"Task #{task_id} not found.")
        removed = self.tasks.pop(idx)
        self._persist()
        return removed

    def mark_complete(self, task_id: int, completed: bool = True) -> dict:
        task = self.get_task(task_id)
        if task is None:
            raise ValueError(f"Task #{task_id} not found.")
        task["completed"] = completed
        self._persist()
        return task

    def edit_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
    ) -> dict:
        task = self.get_task(task_id)
        if task is None:
            raise ValueError(f"Task #{task_id} not found.")
        if title is not None:
            title = title.strip()
            if not title:
                raise ValueError("Task title cannot be empty.")
            task["title"] = title
        if description is not None:
            task["description"] = description.strip()
        self._persist()
        return task

    def clear_completed(self) -> int:
        before = len(self.tasks)
        self._data["tasks"] = [t for t in self.tasks if not t["completed"]]
        removed = before - len(self.tasks)
        if removed:
            self._persist()
        return removed

    def list_tasks(self, filter_by: str = "all") -> list[dict]:
        filter_by = filter_by.lower()
        if filter_by == "active":
            return [t for t in self.tasks if not t["completed"]]
        if filter_by == "completed":
            return [t for t in self.tasks if t["completed"]]
        return list(self.tasks)

    def search_tasks(self, keyword: str) -> list[dict]:
        keyword = keyword.strip().lower()
        if not keyword:
            return []
        results = []
        for task in self.tasks:
            haystack = f"{task['title']} {task.get('description', '')}".lower()
            if keyword in haystack:
                results.append(task)
        return results

    def progress_stats(self) -> tuple[int, int, float]:
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["completed"])
        pct = (completed / total * 100) if total else 0.0
        return completed, total, pct
