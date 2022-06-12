from pytest import mark

from cachetory import serializers
from cachetory.backends import sync as sync_backends
from cachetory.caches.sync import Cache
from tests.support import if_redis_enabled

_test_redis = mark.skipif("not config.getoption('test_redis')")


def test_get_set_in_memory():
    cache = Cache[int](
        serializer=serializers.from_url("pickle+zstd://?pickle-protocol=4&compression-level=3"),
        backend=sync_backends.from_url("memory://"),
    )
    cache.set("foo", 42)
    assert cache.get("foo") == 42


@if_redis_enabled
def test_get_set_in_redis():
    cache = Cache[int](
        serializer=serializers.from_url("pickle+zstd://?pickle-protocol=4&compression-level=3"),
        backend=sync_backends.from_url("redis://localhost:6379"),
    )
    with cache:
        cache.set("foo", 42)
        assert cache.get("foo") == 42
