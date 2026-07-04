"""Plugin management helpers for AQRL."""

from __future__ import annotations

import logging
from typing import Any, Protocol

from .config import Config
from .constants import DEFAULT_PLUGIN_LOGGER_NAME
from .events import EventBus
from .registry import Registry
from .utils import normalize_name


class Plugin(Protocol):
    """Protocol for AQRL plugins."""

    name: str

    def initialize(self, manager: PluginManager) -> None:
        """Initialize the plugin within a manager context."""


class PluginManager:
    """Register and initialize in-process AQRL plugins."""

    def __init__(
        self,
        *,
        config: Config | None = None,
        event_bus: EventBus | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._config = Config() if config is None else config
        self._event_bus = EventBus() if event_bus is None else event_bus
        self._logger = logging.getLogger(DEFAULT_PLUGIN_LOGGER_NAME) if logger is None else logger
        self._plugins: Registry[Plugin] = Registry()
        self._initialized: set[str] = set()

    @property
    def config(self) -> Config:
        """Return the manager configuration."""
        return self._config

    @property
    def event_bus(self) -> EventBus:
        """Return the shared event bus."""
        return self._event_bus

    @property
    def logger(self) -> logging.Logger:
        """Return the manager logger."""
        return self._logger

    def register(self, plugin: Plugin) -> None:
        """Register a plugin by its declared name."""
        self._validate_plugin(plugin)
        plugin_name = normalize_name(plugin.name, "plugin.name")
        self._plugins.add(plugin_name, plugin)

    def get(self, name: str) -> Plugin:
        """Return a registered plugin by name."""
        return self._plugins.get(normalize_name(name, "name"))

    def list(self) -> tuple[str, ...]:
        """Return the registered plugin names."""
        return self._plugins.list()

    def initialize(self, name: str) -> Plugin:
        """Initialize a registered plugin once and return it."""
        normalized_name = normalize_name(name, "name")
        plugin = self._plugins.get(normalized_name)
        if normalized_name not in self._initialized:
            plugin.initialize(self)
            self._initialized.add(normalized_name)
        return plugin

    def initialize_all(self) -> tuple[Plugin, ...]:
        """Initialize every registered plugin in registration order."""
        return tuple(self.initialize(name) for name in self.list())

    def is_initialized(self, name: str) -> bool:
        """Return whether a plugin has already been initialized."""
        return normalize_name(name, "name") in self._initialized

    @staticmethod
    def _validate_plugin(plugin: Any) -> None:
        """Validate the plugin surface expected by the manager."""
        name = getattr(plugin, "name", None)
        if not isinstance(name, str):
            raise TypeError("plugin.name must be a string.")
        if not name.strip():
            raise ValueError("plugin.name must not be empty.")

        initialize = getattr(plugin, "initialize", None)
        if not callable(initialize):
            raise TypeError("plugin.initialize must be callable.")


__all__ = ["Plugin", "PluginManager"]
