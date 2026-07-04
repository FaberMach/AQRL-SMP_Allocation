from pathlib import Path

import pytest

from aqrl.core import (
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
    AQRLException,
    AQRLRegistryError,
    DuplicateRegistrationError,
    RegistryError,
    coerce_bool,
    coerce_path,
    ensure_mapping,
    json_safe,
    normalize_name,
)


def test_core_constants_expose_defaults() -> None:
    assert PROJECT_NAME == "AQRL"
    assert DEFAULT_ENVIRONMENT == "development"
    assert DEFAULT_ENV_PREFIX == "AQRL_"
    assert DEFAULT_LOG_LEVEL == "INFO"
    assert DEFAULT_CORE_LOGGER_NAME == "aqrl"
    assert DEFAULT_PLUGIN_LOGGER_NAME == "aqrl.plugins"
    assert DEFAULT_SCHEDULER_LOGGER_NAME == "aqrl.scheduler"
    assert Path("data") == DEFAULT_DATA_DIR
    assert Path(".cache") == DEFAULT_CACHE_DIR
    assert Path("artifacts") == DEFAULT_ARTIFACTS_DIR


def test_core_exception_hierarchy() -> None:
    assert issubclass(RegistryError, AQRLRegistryError)
    assert issubclass(RegistryError, AQRLException)
    assert issubclass(DuplicateRegistrationError, RegistryError)


def test_core_utils_normalize_and_coerce_values() -> None:
    assert normalize_name("  alpha  ") == "alpha"
    assert coerce_bool("true") is True
    assert coerce_bool("off") is False
    assert coerce_path("data/cache") == Path("data/cache")

    mapping = {"alpha": 1}
    copied = ensure_mapping(mapping, "mapping")
    assert copied == mapping
    assert copied is not mapping

    safe = json_safe({"path": Path("logs"), "nested": {"value": Path("artifacts/run")}})
    assert safe["path"] == "logs"
    assert safe["nested"]["value"] == str(Path("artifacts/run"))


def test_core_utils_reject_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="name"):
        normalize_name("   ", "name")

    with pytest.raises(TypeError, match="value"):
        coerce_bool("maybe")

    with pytest.raises(TypeError, match="path"):
        coerce_path(1)  # type: ignore[arg-type]
