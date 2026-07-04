from pathlib import Path

from aqrl.data.cache import DataCache


def test_data_cache_persists_and_recovers_objects(tmp_path: Path) -> None:
    cache = DataCache(tmp_path / "cache")
    payload = {"symbol": "AAPL", "prices": [1, 2, 3]}

    cache.set("prices", payload)

    assert cache.exists("prices") is True
    assert cache.keys() == ("prices",)
    assert cache.get("prices") == payload

    reloaded = DataCache(tmp_path / "cache")
    assert reloaded.get("prices") == payload


def test_data_cache_delete_and_clear(tmp_path: Path) -> None:
    cache = DataCache(tmp_path / "cache")
    cache.set("alpha", 1)
    cache.set("beta", 2)

    assert cache.delete("alpha") is True
    assert cache.exists("alpha") is False
    assert cache.keys() == ("beta",)

    cache.clear()
    assert cache.keys() == ()
    assert cache.get("beta") is None
