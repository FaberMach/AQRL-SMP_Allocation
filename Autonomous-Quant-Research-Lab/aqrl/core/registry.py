"""Named registry helpers for AQRL."""

from __future__ import annotations

from typing import TypeVar

from .exceptions import AQRLRegistryError
from .utils import normalize_name

T = TypeVar("T")


class RegistryError(AQRLRegistryError):
    """Base error for registry operations."""


class DuplicateRegistrationError(RegistryError):
    """Raised when a name is registered more than once."""


class RegistryNotFoundError(RegistryError):
    """Raised when a name is not present in the registry."""


class Registry[T]:
    """Named registry with explicit duplicate-handling semantics."""

    def __init__(self) -> None:
        self._entries: dict[str, T] = {}

    def add(self, name: str, value: T) -> None:
        """Register a value under a unique name."""
        normalized_name = self._normalize_name(name)
        if normalized_name in self._entries:
            raise DuplicateRegistrationError(f"Duplicate registration for name: {normalized_name}")
        self._entries[normalized_name] = value

    def get(self, name: str) -> T:
        """Return the value registered for a name."""
        normalized_name = self._normalize_name(name)
        try:
            return self._entries[normalized_name]
        except KeyError as exc:
            raise RegistryNotFoundError(
                f"No registration found for name: {normalized_name}"
            ) from exc

    def list(self) -> tuple[str, ...]:
        """Return registered names in insertion order."""
        return tuple(self._entries.keys())

    def remove(self, name: str) -> T:
        """Remove and return the value registered for a name."""
        normalized_name = self._normalize_name(name)
        try:
            return self._entries.pop(normalized_name)
        except KeyError as exc:
            raise RegistryNotFoundError(
                f"No registration found for name: {normalized_name}"
            ) from exc

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Validate and normalize a registry name."""
        return normalize_name(name, "name")


__all__ = [
    "DuplicateRegistrationError",
    "Registry",
    "RegistryError",
    "RegistryNotFoundError",
]
