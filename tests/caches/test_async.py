from pytest import fixture

from cachetory import serializers
from cachetory.backends import async_ as async_backends
from cachetory.caches.async_ import Cache
from tests.support import if_redis_enabled


@fixture
async def memory_cache() -> Cache[int, bytes]:
    return Cache(
        serializer=serializers.from_url("pickle+zstd://"),
        backend=async_backends.from_url("memory://"),
    )


async def test_get_set_in_memory(memory_cache: Cache[int, bytes]) -> None:
    await memory_cache.set("foo", 42)
    assert await memory_cache.get("foo") == 42


async def test_get_default(memory_cache: Cache[int, bytes]) -> None:
    assert await memory_cache.get("missing", 100500) == 100500


async def test_get_many(memory_cache: Cache[int, bytes]) -> None:
    await memory_cache.set("foo", 42)
    assert await memory_cache.get_many("foo", "bar") == {"foo": 42}


async def test_set_many(memory_cache: Cache[int, bytes]) -> None:
    await memory_cache.set_many({"foo": 42, "bar": 100500})
    assert await memory_cache.get("foo") == 42
    assert await memory_cache.get("bar") == 100500


async def test_delete(memory_cache: Cache[int, bytes]) -> None:
    await memory_cache.set("foo", 42)
    assert await memory_cache.delete("foo")
    assert not await memory_cache.delete("foo")
    assert await memory_cache.get("foo") is None


async def delete_many(memory_cache: Cache[int, bytes]) -> None:
    await memory_cache.set_many({"1": 1, "2": 2, "3": 3})
    await memory_cache.delete_many("1", "2")
    assert await memory_cache.get_many("1", "2", "3") == {"3": 3}


async def test_clear(memory_cache: Cache[int, bytes]) -> None:
    await memory_cache.set("foo", 42)
    await memory_cache.set("bar", 42)

    await memory_cache.clear()

    assert await memory_cache.get("foo") is None
    assert await memory_cache.get("bar") is None


async def test_serialize_executor() -> None:
    cache = Cache[int, bytes](
        serializer=serializers.from_url("pickle://"),
        backend=async_backends.from_url("memory://"),
        serialize_executor=None,  # that's the default executor, NOT «no executor»
    )
    await cache.set("foo", 42)
    assert await cache.get("foo") == 42


@if_redis_enabled
async def test_get_set_in_redis() -> None:
    cache = Cache[int, bytes](
        serializer=serializers.from_url("pickle+zlib://"),
        backend=async_backends.from_url("redis://localhost:6379"),
    )
    async with cache:
        await cache.set("foo", 42)
        assert await cache.get("foo") == 42
