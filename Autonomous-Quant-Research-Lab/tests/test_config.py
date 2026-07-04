from pathlib import Path

from aqrl.core.config import Config


def test_config_defaults() -> None:
    config = Config()

    assert config.project_name == "AQRL"
    assert config.environment == "development"
    assert config.debug is False
    assert config.log_level == "INFO"
    assert config.data_dir == Path("data")
    assert config.cache_dir == Path(".cache")
    assert config.artifacts_dir == Path("artifacts")
    assert config.random_seed is None


def test_config_from_env_overrides_defaults() -> None:
    config = Config.from_env(
        {
            "AQRL_PROJECT_NAME": "Quant Lab",
            "AQRL_ENVIRONMENT": "staging",
            "AQRL_DEBUG": "true",
            "AQRL_LOG_LEVEL": "DEBUG",
            "AQRL_DATA_DIR": "data/staging",
            "AQRL_CACHE_DIR": "cache/staging",
            "AQRL_ARTIFACTS_DIR": "artifacts/staging",
            "AQRL_RANDOM_SEED": "7",
        }
    )

    assert config.project_name == "Quant Lab"
    assert config.environment == "staging"
    assert config.debug is True
    assert config.log_level == "DEBUG"
    assert config.data_dir == Path("data/staging")
    assert config.cache_dir == Path("cache/staging")
    assert config.artifacts_dir == Path("artifacts/staging")
    assert config.random_seed == 7


def test_config_from_yaml_and_env_precedence(tmp_path: Path) -> None:
    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text(
        """\
project_name: Research Lab
environment: staging
debug: false
log_level: WARNING
data_dir: data/staging
cache_dir: cache/staging
artifacts_dir: artifacts/staging
random_seed: 21
""",
        encoding="utf-8",
    )

    yaml_config = Config.from_yaml(yaml_path)
    assert yaml_config.project_name == "Research Lab"
    assert yaml_config.environment == "staging"
    assert yaml_config.debug is False
    assert yaml_config.log_level == "WARNING"
    assert yaml_config.data_dir == Path("data/staging")
    assert yaml_config.cache_dir == Path("cache/staging")
    assert yaml_config.artifacts_dir == Path("artifacts/staging")
    assert yaml_config.random_seed == 21

    merged = Config.load(
        yaml_path=yaml_path,
        environ={
            "AQRL_DEBUG": "true",
            "AQRL_LOG_LEVEL": "ERROR",
            "AQRL_RANDOM_SEED": "99",
        },
    )

    assert merged.project_name == "Research Lab"
    assert merged.environment == "staging"
    assert merged.debug is True
    assert merged.log_level == "ERROR"
    assert merged.data_dir == Path("data/staging")
    assert merged.cache_dir == Path("cache/staging")
    assert merged.artifacts_dir == Path("artifacts/staging")
    assert merged.random_seed == 99
