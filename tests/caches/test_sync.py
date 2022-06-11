from pytest import mark

from cachetory import backends, serializers
from cachetory.caches.sync import Cache

_test_redis = mark.skipif("not config.getoption('test_redis')")


def test_get_set_in_memory():
    cache = Cache[int](
        serializer=serializers.from_url("pickle+zstd://pickle-protocol=5&compression-level=3"),
        backend=backends.sync.from_url("memory://"),
    )
    cache.set("foo", 42)
    assert cache.get("foo") == 42


@_test_redis
def test_get_set_in_redis():
    cache = Cache[int](
        serializer=serializers.from_url("pickle+zstd://pickle-protocol=5&compression-level=3"),
        backend=backends.sync.from_url("redis://localhost:6379"),
    )
    cache.set("foo", 42)
    assert cache.get("foo") == 42
