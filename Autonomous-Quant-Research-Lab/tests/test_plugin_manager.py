from aqrl.core.config import Config
from aqrl.core.plugin_manager import PluginManager


class DemoPlugin:
    def __init__(self, name: str) -> None:
        self.name = name
        self.initialized_with: PluginManager | None = None
        self.initialize_calls = 0

    def initialize(self, manager: PluginManager) -> None:
        self.initialized_with = manager
        self.initialize_calls += 1


def test_plugin_manager_registers_and_initializes_plugins() -> None:
    config = Config(project_name="Quant Lab")
    manager = PluginManager(config=config)
    plugin = DemoPlugin("alpha")

    manager.register(plugin)
    loaded = manager.initialize("alpha")

    assert loaded is plugin
    assert plugin.initialized_with is manager
    assert plugin.initialize_calls == 1
    assert manager.config is config
    assert manager.get("alpha") is plugin
    assert manager.list() == ("alpha",)
    assert manager.is_initialized("alpha") is True


def test_plugin_manager_initializes_all_in_registration_order() -> None:
    manager = PluginManager()
    calls: list[str] = []

    class FirstPlugin:
        name = "first"

        def initialize(self, manager: PluginManager) -> None:
            calls.append(f"{self.name}:{manager.config.project_name}")

    class SecondPlugin:
        name = "second"

        def initialize(self, manager: PluginManager) -> None:
            calls.append(f"{self.name}:{manager.event_bus is not None}")

    first = FirstPlugin()
    second = SecondPlugin()

    manager.register(first)
    manager.register(second)

    initialized = manager.initialize_all()

    assert initialized == (first, second)
    assert calls == ["first:AQRL", "second:True"]
