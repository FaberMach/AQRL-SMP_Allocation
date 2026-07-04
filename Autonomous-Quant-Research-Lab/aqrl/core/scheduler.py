"""Simple in-process scheduler helpers for AQRL."""

from __future__ import annotations

from typing import Any

from .registry import Registry
from .types import TaskCallable

type Task = TaskCallable


class Scheduler:
    """Register and execute synchronous in-process tasks."""

    def __init__(self) -> None:
        self._tasks: Registry[Task] = Registry()

    def register(self, name: str, task: Task) -> None:
        """Register a task by name."""
        self._validate_task(task)
        self._tasks.add(name, task)

    def run(self, name: str) -> Any:
        """Execute a registered task and return its result."""
        return self._tasks.get(name)()

    def run_all(self) -> dict[str, Any]:
        """Execute every registered task in registration order."""
        return {name: self.run(name) for name in self.list()}

    def list(self) -> tuple[str, ...]:
        """Return the registered task names."""
        return self._tasks.list()

    def remove(self, name: str) -> Task:
        """Remove a task and return the callable."""
        return self._tasks.remove(name)

    @staticmethod
    def _validate_task(task: Any) -> None:
        """Ensure a task is callable."""
        if not callable(task):
            raise TypeError("task must be callable.")


__all__ = ["Scheduler", "Task"]
