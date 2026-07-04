import json
from threading import Thread
from typing import cast
from urllib.request import urlopen

import pytest

from aqrl.dashboards.client_view import (
    DemoModelConfig,
    create_client_view_server,
    run_demo_model,
)


def test_run_demo_model_returns_interactive_payload() -> None:
    payload = run_demo_model(
        DemoModelConfig(
            strategy="moving_average_crossover",
            short_window=3,
            long_window=8,
            initial_capital=100_000,
            transaction_cost=0.001,
        )
    )

    assert payload["config"]["strategy"] == "moving_average_crossover"
    assert payload["summary"]["final_equity"] > 0
    assert "regime" in payload["latest_regime"]
    assert "momentum" in payload["latest_features"]
    assert payload["rebalance"]["turnover"] >= 0
    assert len(payload["equity_curve"]) == 20
    assert len(payload["signals"]) == 20


def test_demo_model_config_validates_strategy_windows() -> None:
    with pytest.raises(ValueError):
        DemoModelConfig(strategy="moving_average_crossover", short_window=8, long_window=3)

    with pytest.raises(ValueError):
        DemoModelConfig.from_query({"strategy": ["unknown"]})


def test_client_view_http_server_serves_page_health_and_demo_payload() -> None:
    server = create_client_view_server(port=0)
    host = cast(str, server.server_address[0])
    port = server.server_address[1]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://{host}:{port}"

    try:
        with urlopen(f"{base_url}/", timeout=10) as response:
            html = response.read().decode("utf-8")
        with urlopen(f"{base_url}/health", timeout=10) as response:
            health = json.loads(response.read().decode("utf-8"))
        with urlopen(f"{base_url}/api/demo?strategy=buy_and_hold", timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)

    assert "AQRL Local Model Client" in html
    assert health == {"status": "ok", "service": "aqrl-client-view"}
    assert payload["config"]["strategy"] == "buy_and_hold"
