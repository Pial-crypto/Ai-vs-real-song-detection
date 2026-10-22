"""In-memory caching service with TTL support."""

from __future__ import annotations

import time
from typing import Any, Optional


class CacheEntry:
    def __init__(self, value: Any, ttl: float) -> None:
        self.value = value
        self.expires_at = time.time() + ttl


class InMemoryCache:
    def __init__(self, default_ttl: float = 300.0, max_size: int = 1000) -> None:
        self._store: dict = {}
        self._default_ttl = default_ttl
        self._max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() > entry.expires_at:
            del self._store[key]
            return None
        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        if len(self._store) >= self._max_size:
            self._evict_expired()
            if len(self._store) >= self._max_size:
                # evict oldest
                oldest = min(self._store, key=lambda k: self._store[k].expires_at)
                del self._store[oldest]
        self._store[key] = CacheEntry(value, ttl if ttl is not None else self._default_ttl)

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()

    def size(self) -> int:
        self._evict_expired()
        return len(self._store)

    def _evict_expired(self) -> None:
        now = time.time()
        expired = [k for k, v in self._store.items() if now > v.expires_at]
        for k in expired:
            del self._store[k]

    def stats(self) -> dict:
        self._evict_expired()
        return {"size": len(self._store), "max_size": self._max_size, "default_ttl": self._default_ttl}


# Module-level singleton
_cache = InMemoryCache()


def get_cache() -> InMemoryCache:
    return _cache


def cached(key: str, ttl: Optional[float] = None):
    """Decorator for caching function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = get_cache()
            result = cache.get(key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache.set(key, result, ttl=ttl)
            return result
        return wrapper
    return decorator
