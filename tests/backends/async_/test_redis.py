from typing import AsyncIterable

from pytest import fixture, mark

from cachetory.backends import AsyncRedisBackend

test_redis = mark.skipif("not config.getoption('test_redis')")


@fixture
async def backend() -> AsyncIterable[AsyncRedisBackend]:
    backend = await AsyncRedisBackend.from_url("redis://localhost:6379")
    try:
        yield backend
    finally:
        await backend.clear()


@test_redis
async def test_set_get(backend: AsyncRedisBackend):
    await backend.set("foo", b"hello")
    assert await backend.get("foo") == b"hello"
