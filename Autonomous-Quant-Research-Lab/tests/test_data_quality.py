import pandas as pd

from aqrl.data.data_quality import DataQualityIssue, validate_market_data


def test_validate_market_data_passes_clean_dataset() -> None:
    frame = pd.DataFrame(
        {
            "open": [99.0, 100.0],
            "high": [101.0, 102.0],
            "low": [98.0, 99.0],
            "close": [100.0, 101.0],
            "volume": [1000, 1100],
        },
        index=pd.date_range("2024-01-01", periods=2, tz="UTC", name="timestamp"),
    )

    report = validate_market_data(frame, dataset_name="daily_prices")

    assert report.passed is True
    assert report.failures == ()
    assert report.dataset_name == "daily_prices"
    assert report.to_dict()["passed"] is True


def test_validate_market_data_reports_structured_failures() -> None:
    frame = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2024-01-02", "2024-01-01", "2024-01-01"], utc=True),
            "open": [10.0, -1.0, 12.0],
            "high": [11.0, 8.0, 7.0],
            "low": [9.0, 9.0, 6.0],
            "close": [10.5, 8.5, 10.0],
            "volume": [1000, None, 1200],
        }
    )

    report = validate_market_data(frame)
    checks = {issue.check for issue in report.issues}

    assert report.passed is False
    assert {
        "missing_values",
        "duplicate_timestamps",
        "non_monotonic_timestamp",
        "non_positive_prices",
        "high_below_low",
        "close_outside_high_low",
    }.issubset(checks)
    assert all(isinstance(issue, DataQualityIssue) for issue in report.issues)
    assert report.to_dict()["issues"]
