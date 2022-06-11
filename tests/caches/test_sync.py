from pytest import fixture

from cachetory import backends, serializers
from cachetory.caches.sync import Cache


@fixture
def cache() -> Cache[int]:
    return Cache(
        serializer=serializers.from_url("pickle+zstd://pickle-protocol=5&compression-level=3"),
        backend=backends.sync.from_url("memory://"),
    )


def test_get_set(cache: Cache[int]):
    cache.set("foo", 42)
    assert cache.get("foo") == 42
