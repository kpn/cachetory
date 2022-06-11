from pytest import fixture, mark

from cachetory import backends, serializers
from cachetory.caches.async_ import Cache


@fixture
async def cache() -> Cache[int]:
    return Cache(
        serializer=serializers.from_url("pickle+zstd://"),
        backend=(await backends.async_.from_url("memory://")),
    )


@mark.asyncio
async def test_get_set(cache: Cache[int]):
    await cache.set("foo", 42)
    assert await cache.get("foo") == 42
