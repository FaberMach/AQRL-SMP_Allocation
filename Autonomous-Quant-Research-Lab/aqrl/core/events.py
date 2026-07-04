"""Event primitives for AQRL."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from threading import RLock
from typing import Any

from .utils import ensure_mapping, normalize_name, utc_now

type EventHandler = Callable[["Event"], Any]


@dataclass(frozen=True, slots=True)
class Event:
    """Immutable event payload dispatched by the event bus."""

    name: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    source: str | None = None
    timestamp: datetime = field(default_factory=utc_now)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", normalize_name(self.name, "name"))

        if self.source is not None:
            if not isinstance(self.source, str):
                raise TypeError("source must be a string or None.")
            normalized_source = self.source.strip()
            object.__setattr__(self, "source", normalized_source or None)

        if not isinstance(self.timestamp, datetime):
            raise TypeError("timestamp must be a datetime instance.")
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware.")

        object.__setattr__(self, "payload", ensure_mapping(self.payload, "payload"))
        object.__setattr__(self, "metadata", ensure_mapping(self.metadata, "metadata"))


class EventBus:
    """Synchronous in-process event dispatcher."""

    def __init__(self) -> None:
        self._subscriptions: dict[str, list[EventHandler]] = {}
        self._lock = RLock()

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """Register a handler for an event name."""
        normalized_event_name = normalize_name(event_name, "event_name")
        self._validate_handler(handler)
        with self._lock:
            handlers = self._subscriptions.setdefault(normalized_event_name, [])
            if handler not in handlers:
                handlers.append(handler)

    def unsubscribe(self, event_name: str, handler: EventHandler) -> bool:
        """Remove a handler from an event name."""
        normalized_event_name = normalize_name(event_name, "event_name")
        self._validate_handler(handler)
        with self._lock:
            handlers = self._subscriptions.get(normalized_event_name)
            if not handlers:
                return False
            try:
                handlers.remove(handler)
            except ValueError:
                return False
            if not handlers:
                self._subscriptions.pop(normalized_event_name, None)
            return True

    def publish(self, event: Event) -> list[Any]:
        """Dispatch an event synchronously to every subscribed handler."""
        if not isinstance(event, Event):
            raise TypeError("event must be an Event instance.")
        handlers = self._handlers_for(event.name)
        return [handler(event) for handler in handlers]

    def _handlers_for(self, event_name: str) -> tuple[EventHandler, ...]:
        """Return a snapshot of handlers registered for an event name."""
        normalized_event_name = normalize_name(event_name, "event_name")
        with self._lock:
            return tuple(self._subscriptions.get(normalized_event_name, ()))

    @staticmethod
    def _validate_handler(handler: EventHandler) -> None:
        """Ensure the handler can be invoked by the bus."""
        if not callable(handler):
            raise TypeError("handler must be callable.")


__all__ = ["Event", "EventBus", "EventHandler"]
