import json
import logging
from io import StringIO
from pathlib import Path

from aqrl.core.logger import StructuredFormatter, create_logger


def test_create_logger_writes_structured_console_output() -> None:
    stream = StringIO()

    logger = create_logger(
        "aqrl.tests.console",
        level="DEBUG",
        stream=stream,
    )
    logger.info("pipeline started", extra={"run_id": "demo-1"})

    payload = json.loads(stream.getvalue().strip())
    assert payload["level"] == "INFO"
    assert payload["logger"] == "aqrl.tests.console"
    assert payload["message"] == "pipeline started"
    assert payload["extra"]["run_id"] == "demo-1"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0].formatter, StructuredFormatter)


def test_create_logger_adds_optional_file_handler(tmp_path: Path) -> None:
    stream = StringIO()
    log_path = tmp_path / "logs" / "aqrl.log"

    logger = create_logger(
        "aqrl.tests.file",
        stream=stream,
        log_file=log_path,
    )
    logger.warning("persisted")

    for handler in logger.handlers:
        handler.flush()

    payload = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert payload["level"] == "WARNING"
    assert payload["message"] == "persisted"
    assert log_path.exists()
    assert len(logger.handlers) == 2
