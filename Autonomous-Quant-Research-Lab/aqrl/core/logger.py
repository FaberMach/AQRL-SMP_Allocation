"""Structured logging helpers for AQRL."""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TextIO

from .constants import DEFAULT_CORE_LOGGER_NAME
from .utils import json_safe

_LOG_RECORD_KEYS = frozenset(logging.LogRecord("", 0, "", 0, "", (), None).__dict__)


class StructuredFormatter(logging.Formatter):
    """Format log records as compact JSON lines.

    The formatter keeps console and file output machine-readable while still
    preserving the most important diagnostic fields.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Render a log record as a JSON line.

        Args:
            record: Log record emitted by the standard ``logging`` package.

        Returns:
            A compact JSON string containing the log payload.
        """
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        extras = _extract_extras(record)
        if extras:
            payload["extra"] = extras
        if record.exc_info is not None:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info is not None:
            payload["stack_info"] = record.stack_info
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def create_logger(
    name: str = DEFAULT_CORE_LOGGER_NAME,
    *,
    level: int | str = logging.INFO,
    stream: TextIO | None = None,
    log_file: Path | str | None = None,
    file_level: int | str | None = None,
) -> logging.Logger:
    """Create a structured AQRL logger.

    Args:
        name: Logger name to configure.
        level: Console log level as an integer or standard level name.
        stream: Optional text stream for the console handler. ``sys.stdout`` is
            used when omitted.
        log_file: Optional file path for persisted JSON-line logs.
        file_level: Optional log level for the file handler. When omitted, the
            console level is reused.

    Returns:
        A configured ``logging.Logger`` instance.
    """
    console_level = _resolve_level(level)
    file_level_value = console_level if file_level is None else _resolve_level(file_level)

    logger = logging.getLogger(name)
    _remove_handlers(logger)
    logger.setLevel(min(console_level, file_level_value))
    logger.propagate = False

    console_handler = logging.StreamHandler(stream if stream is not None else sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(StructuredFormatter())
    logger.addHandler(console_handler)

    if log_file is not None:
        log_path = Path(log_file).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(file_level_value)
        file_handler.setFormatter(StructuredFormatter())
        logger.addHandler(file_handler)

    return logger


def _remove_handlers(logger: logging.Logger) -> None:
    """Detach any previously configured handlers from a logger."""
    for handler in list(logger.handlers):
        logger.removeHandler(handler)


def _resolve_level(level: int | str) -> int:
    """Resolve a logging level from either an integer or a symbolic name."""
    if isinstance(level, int):
        return level
    if isinstance(level, str):
        candidate = level.strip().upper()
        if candidate.isdigit():
            return int(candidate)
        resolved = logging.getLevelName(candidate)
        if isinstance(resolved, int):
            return resolved
    raise TypeError("level must be a logging level number or name.")


def _extract_extras(record: logging.LogRecord) -> dict[str, Any]:
    """Return non-standard log-record fields in a JSON-safe shape."""
    extras: dict[str, Any] = {}
    for key, value in record.__dict__.items():
        if key in _LOG_RECORD_KEYS or key.startswith("_"):
            continue
        extras[key] = json_safe(value)
    return extras
