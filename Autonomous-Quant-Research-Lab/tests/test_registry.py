import pytest

from aqrl.core.registry import DuplicateRegistrationError, Registry, RegistryNotFoundError


def test_registry_add_get_list_and_remove() -> None:
    registry: Registry[int] = Registry()

    registry.add("alpha", 1)
    registry.add("beta", 2)

    assert registry.get("alpha") == 1
    assert registry.list() == ("alpha", "beta")
    assert registry.remove("alpha") == 1
    assert registry.list() == ("beta",)


def test_registry_rejects_duplicate_registration() -> None:
    registry: Registry[str] = Registry()
    registry.add("model", "first")

    with pytest.raises(DuplicateRegistrationError, match="model"):
        registry.add("model", "second")


def test_registry_raises_when_name_is_missing() -> None:
    registry: Registry[str] = Registry()

    with pytest.raises(RegistryNotFoundError, match="missing"):
        registry.get("missing")

    with pytest.raises(RegistryNotFoundError, match="missing"):
        registry.remove("missing")
