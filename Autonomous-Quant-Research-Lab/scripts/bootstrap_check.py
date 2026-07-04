"""Bootstrap validation script for AQRL."""

from pathlib import Path

REQUIRED_PATHS = [
    "README.md",
    "PROJECT_BIBLE.md",
    "AQRL_SPEC.yaml",
    "TASKS.yaml",
    "AGENTS.md",
    "pyproject.toml",
    "aqrl/core/__init__.py",
    "tests",
]


def main() -> None:
    """Validate that required bootstrap files exist."""
    missing = [p for p in REQUIRED_PATHS if not Path(p).exists()]
    if missing:
        raise SystemExit(f"Missing required paths: {missing}")
    print("AQRL bootstrap structure looks valid.")


if __name__ == "__main__":
    main()
