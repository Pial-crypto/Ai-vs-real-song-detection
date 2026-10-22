"""Simple in-memory task queue with worker simulation."""

from __future__ import annotations

import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Task:
    id: str
    name: str
    payload: Dict[str, Any]
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retries: int = 0
    max_retries: int = 3


class TaskQueue:
    def __init__(self, max_workers: int = 4) -> None:
        self._queue: deque = deque()
        self._tasks: Dict[str, Task] = {}
        self._handlers: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        self._workers: List[threading.Thread] = []
        self._running = False
        self._max_workers = max_workers

    def register_handler(self, name: str, handler: Callable) -> None:
        self._handlers[name] = handler

    def enqueue(self, name: str, payload: Dict[str, Any], max_retries: int = 3) -> str:
        task_id = str(uuid.uuid4())
        task = Task(id=task_id, name=name, payload=payload, max_retries=max_retries)
        with self._lock:
            self._tasks[task_id] = task
            self._queue.append(task_id)
        return task_id

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def list_tasks(self, status: Optional[str] = None) -> List[Task]:
        with self._lock:
            tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    def cancel(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task and task.status == "pending":
            task.status = "cancelled"
            return True
        return False

    def process_one(self) -> Optional[str]:
        with self._lock:
            if not self._queue:
                return None
            task_id = self._queue.popleft()
        task = self._tasks[task_id]
        if task.status == "cancelled":
            return task_id
        handler = self._handlers.get(task.name)
        if handler is None:
            task.status = "failed"
            task.error = f"No handler for {task.name}"
            return task_id
        task.status = "running"
        task.started_at = time.time()
        try:
            task.result = handler(task.payload)
            task.status = "completed"
            task.completed_at = time.time()
        except Exception as exc:
            task.retries += 1
            if task.retries < task.max_retries:
                task.status = "pending"
                with self._lock:
                    self._queue.append(task_id)
            else:
                task.status = "failed"
                task.error = str(exc)
                task.completed_at = time.time()
        return task_id

    def process_all(self) -> int:
        count = 0
        while True:
            tid = self.process_one()
            if tid is None:
                break
            count += 1
        return count

    def stats(self) -> Dict[str, int]:
        with self._lock:
            tasks = list(self._tasks.values())
        stats = {"total": len(tasks), "pending": 0, "running": 0, "completed": 0, "failed": 0, "cancelled": 0}
        for t in tasks:
            if t.status in stats:
                stats[t.status] += 1
        return stats


_queue = TaskQueue()


def get_task_queue() -> TaskQueue:
    return _queue
