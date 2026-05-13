import time
from collections.abc import Hashable
from dataclasses import dataclass
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class TTLCache:
    """Tiny in-process TTL cache used for cheap repeated lookups."""

    def __init__(self, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self._items: dict[Hashable, CacheEntry] = {}

    def get(self, key: Hashable) -> Any | None:
        entry = self._items.get(key)
        if entry is None:
            return None
        if entry.expires_at < time.monotonic():
            self._items.pop(key, None)
            return None
        return entry.value

    def set(self, key: Hashable, value: Any) -> None:
        self._items[key] = CacheEntry(
            value=value,
            expires_at=time.monotonic() + self.ttl_seconds,
        )

    def clear(self) -> None:
        self._items.clear()
