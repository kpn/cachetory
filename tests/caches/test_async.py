from pytest import mark

from cachetory import backends, serializers
from cachetory.caches.async_ import Cache
from tests.support import if_redis_enabled

_test_redis = mark.skipif("not config.getoption('test_redis')")


@mark.asyncio
async def test_get_set_in_memory():
    cache = Cache[int](
        serializer=serializers.from_url("pickle+zstd://"),
        backend=(await backends.async_.from_url("memory://")),
    )
    await cache.set("foo", 42)
    assert await cache.get("foo") == 42


@if_redis_enabled
@mark.asyncio
async def test_get_set_in_redis():
    cache = Cache[int](
        serializer=serializers.from_url("pickle+zstd://pickle-protocol=5&compression-level=3"),
        backend=(await backends.async_.from_url("redis://localhost:6379")),
    )
    async with cache:
        await cache.set("foo", 42)
        assert await cache.get("foo") == 42
