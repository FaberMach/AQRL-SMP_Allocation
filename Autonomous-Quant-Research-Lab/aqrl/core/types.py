"""Common type aliases for AQRL core and data layers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

type JSONScalar = str | int | float | bool | None
type JSONValue = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]
type JSONMapping = Mapping[str, JSONValue]
type AnyMapping = Mapping[str, Any]
type PathLikeValue = str | Path
type TaskCallable = Callable[[], Any]
type EventName = str
type PluginName = str
type RegistryName = str

__all__ = [
    "AnyMapping",
    "EventName",
    "JSONMapping",
    "JSONScalar",
    "JSONValue",
    "PathLikeValue",
    "PluginName",
    "RegistryName",
    "TaskCallable",
]
