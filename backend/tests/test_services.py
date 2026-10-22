from __future__ import annotations

from backend.app.services.cache_service import InMemoryCache
from backend.app.services.search_service import SearchIndex


def test_cache_basic():
    c = InMemoryCache(default_ttl=10, max_size=3)
    c.set("a", 1)
    assert c.get("a") == 1
    c.delete("a")
    assert c.get("a") is None


def test_cache_eviction():
    c = InMemoryCache(default_ttl=10, max_size=2)
    c.set("a", 1)
    c.set("b", 2)
    c.set("c", 3)
    assert c.size() <= 2


def test_search_index():
    idx = SearchIndex()
    idx.add("1", "hello world")
    idx.add("2", "hello there")
    assert idx.search("hello") == {"1", "2"}
    assert idx.search("world") == {"1"}
    idx.remove("1")
    assert idx.search("world") == set()
