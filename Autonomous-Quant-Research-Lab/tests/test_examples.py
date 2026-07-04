import runpy
from pathlib import Path


def test_examples_run_without_network_access() -> None:
    root = Path(__file__).resolve().parents[1]
    examples = (
        root / "examples" / "01_data_pipeline.py",
        root / "examples" / "02_strategy_backtest.py",
        root / "examples" / "03_risk_portfolio_rebalance.py",
    )

    for example in examples:
        runpy.run_path(str(example), run_name="__main__")
