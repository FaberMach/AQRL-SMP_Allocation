"""Configuration helpers for AQRL."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, fields, replace
from pathlib import Path
from typing import Any, Self

import yaml

from .constants import (
    DEFAULT_ARTIFACTS_DIR,
    DEFAULT_CACHE_DIR,
    DEFAULT_DATA_DIR,
    DEFAULT_ENV_PREFIX,
    DEFAULT_ENVIRONMENT,
    DEFAULT_LOG_LEVEL,
    PROJECT_NAME,
)
from .utils import coerce_bool, coerce_path


@dataclass(frozen=True, slots=True)
class Config:
    """Immutable bootstrap configuration for AQRL.

    The configuration is resolved in three layers: defaults, YAML files, and
    environment variable overrides. Environment variables use the ``AQRL_``
    prefix and map to the dataclass field names in lowercase.
    """

    project_name: str = PROJECT_NAME
    environment: str = DEFAULT_ENVIRONMENT
    debug: bool = False
    log_level: str = DEFAULT_LOG_LEVEL
    data_dir: Path = DEFAULT_DATA_DIR
    cache_dir: Path = DEFAULT_CACHE_DIR
    artifacts_dir: Path = DEFAULT_ARTIFACTS_DIR
    random_seed: int | None = None

    @classmethod
    def from_yaml(cls, path: Path | str) -> Self:
        """Load configuration values from a YAML file.

        Args:
            path: Path to a YAML file whose top-level value is a mapping.

        Returns:
            A ``Config`` instance with YAML values applied over the defaults.
        """
        return cls.load(yaml_path=path, environ={})

    @classmethod
    def from_env(
        cls,
        environ: Mapping[str, str] | None = None,
        *,
        prefix: str = DEFAULT_ENV_PREFIX,
    ) -> Self:
        """Load configuration values from environment variables.

        Args:
            environ: Mapping of environment variables to inspect. ``os.environ``
                is used when omitted.
            prefix: Environment variable prefix to read.

        Returns:
            A ``Config`` instance with environment overrides applied.
        """
        return cls.load(environ=os.environ if environ is None else environ, env_prefix=prefix)

    @classmethod
    def load(
        cls,
        *,
        yaml_path: Path | str | None = None,
        environ: Mapping[str, str] | None = None,
        env_prefix: str = DEFAULT_ENV_PREFIX,
    ) -> Self:
        """Load defaults, then YAML, then environment overrides.

        Args:
            yaml_path: Optional YAML file path.
            environ: Mapping of environment variables. ``os.environ`` is used
                when omitted.
            env_prefix: Environment variable prefix used to select overrides.

        Returns:
            A ``Config`` instance containing the merged configuration.
        """
        config = cls()

        if yaml_path is not None:
            config = config._apply_overrides(cls._read_yaml(yaml_path))

        env_mapping = os.environ if environ is None else environ
        config = config._apply_overrides(cls._read_environment(env_mapping, env_prefix))
        return config

    def _apply_overrides(self, overrides: Mapping[str, Any]) -> Self:
        """Return a new config with validated overrides applied."""
        valid_fields = {field.name for field in fields(type(self))}
        values: dict[str, Any] = {}
        for key, raw_value in overrides.items():
            if key not in valid_fields:
                raise ValueError(f"Unknown configuration key: {key}")
            values[key] = self._coerce_value(key, raw_value)
        return replace(self, **values)

    @classmethod
    def _read_yaml(cls, path: Path | str) -> Mapping[str, Any]:
        """Read a YAML mapping from disk."""
        config_path = Path(path)
        with config_path.open("r", encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}
        if not isinstance(raw, Mapping):
            raise TypeError("YAML configuration must contain a mapping at the top level.")
        return dict(raw)

    @classmethod
    def _read_environment(
        cls,
        environ: Mapping[str, str],
        prefix: str,
    ) -> Mapping[str, str]:
        """Filter and normalize environment variables for the config layer."""
        normalized_prefix = prefix.upper()
        overrides: dict[str, str] = {}
        for key, value in environ.items():
            if not key.upper().startswith(normalized_prefix):
                continue
            field_name = key[len(prefix) :].lower()
            overrides[field_name] = value
        return overrides

    def _coerce_value(self, key: str, value: Any) -> Any:
        """Coerce a raw value into the field type expected by the dataclass."""
        if key in {"project_name", "environment", "log_level"}:
            if not isinstance(value, str):
                raise TypeError(f"{key} must be a string.")
            return value

        if key in {"data_dir", "cache_dir", "artifacts_dir"}:
            return coerce_path(value, key)

        if key == "debug":
            return coerce_bool(value, key)

        if key == "random_seed":
            if value is None or value == "":
                return None
            if isinstance(value, bool):
                raise TypeError("random_seed must be an integer or null.")
            if isinstance(value, int):
                return value
            if isinstance(value, str):
                return int(value)
            raise TypeError("random_seed must be an integer or null.")

        raise ValueError(f"Unknown configuration key: {key}")
