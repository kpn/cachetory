from typing import AsyncIterable

from pytest import fixture, mark

from cachetory.backends import AsyncRedisBackend

_test_redis = mark.skipif("not config.getoption('test_redis')")


@fixture
async def backend() -> AsyncIterable[AsyncRedisBackend]:
    async with await AsyncRedisBackend.from_url("redis://localhost:6379") as backend:
        await backend.clear()
        try:
            yield backend
        finally:
            await backend.clear()


@_test_redis
@mark.asyncio
async def test_set_get(backend: AsyncRedisBackend):
    await backend.set("foo", b"hello")
    assert await backend.get("foo") == b"hello"
