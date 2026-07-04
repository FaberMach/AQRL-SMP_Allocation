"""Shared constants for AQRL core infrastructure."""

from __future__ import annotations

from pathlib import Path

PROJECT_NAME = "AQRL"
DEFAULT_ENVIRONMENT = "development"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_ENV_PREFIX = "AQRL_"
DEFAULT_CORE_LOGGER_NAME = "aqrl"
DEFAULT_PLUGIN_LOGGER_NAME = "aqrl.plugins"
DEFAULT_SCHEDULER_LOGGER_NAME = "aqrl.scheduler"
DEFAULT_DATA_DIR = Path("data")
DEFAULT_CACHE_DIR = Path(".cache")
DEFAULT_ARTIFACTS_DIR = Path("artifacts")

__all__ = [
    "DEFAULT_ARTIFACTS_DIR",
    "DEFAULT_CACHE_DIR",
    "DEFAULT_CORE_LOGGER_NAME",
    "DEFAULT_DATA_DIR",
    "DEFAULT_ENVIRONMENT",
    "DEFAULT_ENV_PREFIX",
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_PLUGIN_LOGGER_NAME",
    "DEFAULT_SCHEDULER_LOGGER_NAME",
    "PROJECT_NAME",
]
