"""Shared AQRL exception hierarchy."""

from __future__ import annotations


class AQRLError(Exception):
    """Base exception for AQRL."""


AQRLException = AQRLError


class AQRLConfigurationError(AQRLError):
    """Raised when configuration loading or validation fails."""


class AQRLValidationError(AQRLError):
    """Raised when a model or payload fails validation."""


class AQRLRegistryError(AQRLError):
    """Raised when registry operations fail."""


class AQRLPluginError(AQRLError):
    """Raised when plugin lifecycle operations fail."""


class AQRLSchedulerError(AQRLError):
    """Raised when scheduler operations fail."""


class AQRLEventError(AQRLError):
    """Raised when event dispatch operations fail."""


class AQRLDataError(AQRLError):
    """Raised when data layer operations fail."""


__all__ = [
    "AQRLConfigurationError",
    "AQRLDataError",
    "AQRLEventError",
    "AQRLException",
    "AQRLError",
    "AQRLPluginError",
    "AQRLRegistryError",
    "AQRLSchedulerError",
    "AQRLValidationError",
]
