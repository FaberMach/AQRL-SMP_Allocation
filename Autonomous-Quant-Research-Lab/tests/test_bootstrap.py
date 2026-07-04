from pathlib import Path


def test_bootstrap_files_exist() -> None:
    required = [
        "README.md",
        "PROJECT_BIBLE.md",
        "AQRL_SPEC.yaml",
        "TASKS.yaml",
        "AGENTS.md",
        "pyproject.toml",
    ]
    for item in required:
        assert Path(item).exists()
