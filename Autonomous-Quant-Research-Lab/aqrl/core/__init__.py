"""Core infrastructure primitives for AQRL."""

from .config import Config
from .constants import (
    DEFAULT_ARTIFACTS_DIR,
    DEFAULT_CACHE_DIR,
    DEFAULT_CORE_LOGGER_NAME,
    DEFAULT_DATA_DIR,
    DEFAULT_ENV_PREFIX,
    DEFAULT_ENVIRONMENT,
    DEFAULT_LOG_LEVEL,
    DEFAULT_PLUGIN_LOGGER_NAME,
    DEFAULT_SCHEDULER_LOGGER_NAME,
    PROJECT_NAME,
)
from .events import Event, EventBus, EventHandler
from .exceptions import (
    AQRLConfigurationError,
    AQRLDataError,
    AQRLEventError,
    AQRLException,
    AQRLPluginError,
    AQRLRegistryError,
    AQRLSchedulerError,
    AQRLValidationError,
)
from .logger import StructuredFormatter, create_logger
from .plugin_manager import Plugin, PluginManager
from .registry import DuplicateRegistrationError, Registry, RegistryError, RegistryNotFoundError
from .scheduler import Scheduler, Task
from .types import (
    AnyMapping,
    EventName,
    JSONMapping,
    JSONScalar,
    JSONValue,
    PathLikeValue,
    PluginName,
    RegistryName,
    TaskCallable,
)
from .utils import coerce_bool, coerce_path, ensure_mapping, json_safe, normalize_name, utc_now

__all__ = [
    "AQRLConfigurationError",
    "AQRLDataError",
    "AQRLEventError",
    "AQRLException",
    "AQRLPluginError",
    "AQRLRegistryError",
    "AQRLSchedulerError",
    "AQRLValidationError",
    "AnyMapping",
    "Config",
    "DEFAULT_ARTIFACTS_DIR",
    "DEFAULT_CACHE_DIR",
    "DEFAULT_CORE_LOGGER_NAME",
    "DEFAULT_DATA_DIR",
    "DEFAULT_ENVIRONMENT",
    "DEFAULT_ENV_PREFIX",
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_PLUGIN_LOGGER_NAME",
    "DEFAULT_SCHEDULER_LOGGER_NAME",
    "DuplicateRegistrationError",
    "Event",
    "EventBus",
    "EventHandler",
    "EventName",
    "JSONMapping",
    "JSONScalar",
    "JSONValue",
    "PathLikeValue",
    "Plugin",
    "PluginManager",
    "PluginName",
    "PROJECT_NAME",
    "Registry",
    "RegistryError",
    "RegistryName",
    "RegistryNotFoundError",
    "Scheduler",
    "StructuredFormatter",
    "Task",
    "TaskCallable",
    "coerce_bool",
    "coerce_path",
    "create_logger",
    "ensure_mapping",
    "json_safe",
    "normalize_name",
    "utc_now",
]
