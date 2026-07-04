"""Persistent object cache for AQRL data artifacts."""

from __future__ import annotations

import json
import pickle
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from aqrl.core.exceptions import AQRLDataError
from aqrl.core.utils import normalize_name

type CacheValue = Any


@dataclass(frozen=True, slots=True)
class CacheEntry:
    """Metadata describing an object stored in the cache."""

    key: str
    filename: str


class DataCache:
    """Store and retrieve Python objects on disk."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root).expanduser()
        self.root.mkdir(parents=True, exist_ok=True)
        self._index_path = self.root / "index.json"
        self._index: dict[str, CacheEntry] = self._load_index()

    def set(self, key: str, value: CacheValue) -> None:
        """Persist a value under the given cache key."""
        normalized_key = self._normalize_key(key)
        entry = self._index.get(normalized_key)
        filename = entry.filename if entry is not None else self._filename_for(normalized_key)
        path = self.root / filename
        payload = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        self._write_bytes(path, payload)
        self._index[normalized_key] = CacheEntry(key=normalized_key, filename=filename)
        self._write_index()

    def get(self, key: str, default: Any = None) -> Any:
        """Return a cached value or the provided default."""
        normalized_key = self._normalize_key(key)
        entry = self._index.get(normalized_key)
        if entry is None:
            return default

        path = self.root / entry.filename
        if not path.exists():
            self._index.pop(normalized_key, None)
            self._write_index()
            return default

        try:
            payload = path.read_bytes()
            return pickle.loads(payload)
        except (OSError, pickle.PickleError) as exc:
            raise AQRLDataError(f"Failed to read cache entry for key: {normalized_key}") from exc

    def get_or_set(self, key: str, factory: Callable[[], Any]) -> Any:
        """Return a cached value, computing it if necessary."""
        if self.exists(key):
            return self.get(key)
        value = factory()
        self.set(key, value)
        return value

    def exists(self, key: str) -> bool:
        """Return whether the cache contains a key."""
        normalized_key = self._normalize_key(key)
        entry = self._index.get(normalized_key)
        return entry is not None and (self.root / entry.filename).exists()

    def delete(self, key: str) -> bool:
        """Remove a cache entry if it exists."""
        normalized_key = self._normalize_key(key)
        entry = self._index.pop(normalized_key, None)
        if entry is None:
            return False

        path = self.root / entry.filename
        if path.exists():
            path.unlink()
        self._write_index()
        return True

    def clear(self) -> None:
        """Remove every cache entry and reset the cache index."""
        for entry in list(self._index.values()):
            path = self.root / entry.filename
            if path.exists():
                path.unlink()
        self._index.clear()
        self._write_index()

    def keys(self) -> tuple[str, ...]:
        """Return the cached keys in insertion order."""
        return tuple(self._index.keys())

    @staticmethod
    def _normalize_key(key: str) -> str:
        """Validate and normalize a cache key."""
        return normalize_name(key, "key")

    @staticmethod
    def _filename_for(key: str) -> str:
        """Generate a stable cache filename for a key."""
        digest = sha256(key.encode("utf-8")).hexdigest()
        return f"{digest}.pkl"

    def _load_index(self) -> dict[str, CacheEntry]:
        """Load the on-disk cache index."""
        if not self._index_path.exists():
            return {}
        try:
            raw = json.loads(self._index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AQRLDataError("Failed to load the cache index.") from exc
        if not isinstance(raw, Mapping):
            raise AQRLDataError("Cache index must contain a mapping.")

        index: dict[str, CacheEntry] = {}
        for key, filename in raw.items():
            if not isinstance(key, str) or not isinstance(filename, str):
                raise AQRLDataError("Cache index entries must be strings.")
            index[key] = CacheEntry(key=key, filename=filename)
        return index

    def _write_index(self) -> None:
        """Persist the cache index to disk."""
        payload = {key: entry.filename for key, entry in self._index.items()}
        self._write_text(self._index_path, json.dumps(payload, ensure_ascii=False, indent=2))

    @staticmethod
    def _write_bytes(path: Path, payload: bytes) -> None:
        """Write bytes atomically to a cache file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(delete=False, dir=path.parent, suffix=".tmp") as handle:
            handle.write(payload)
            temp_path = Path(handle.name)
        temp_path.replace(path)

    @staticmethod
    def _write_text(path: Path, payload: str) -> None:
        """Write text atomically to a cache file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            delete=False, dir=path.parent, suffix=".tmp", mode="w", encoding="utf-8"
        ) as handle:
            handle.write(payload)
            temp_path = Path(handle.name)
        temp_path.replace(path)


__all__ = ["CacheEntry", "DataCache"]
