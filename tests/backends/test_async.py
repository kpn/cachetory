from asyncio import sleep
from collections.abc import AsyncIterable
from datetime import timedelta
from typing import cast

import pytest

from cachetory.backends.async_ import DjangoBackend, MemoryBackend, RedisBackend
from cachetory.backends.sync import from_url
from cachetory.interfaces.backends.async_ import AsyncBackend
from cachetory.private.datetime import make_deadline


@pytest.fixture
async def memory_backend() -> AsyncIterable[MemoryBackend[int]]:
    async with MemoryBackend[int]() as backend:
        yield backend


@pytest.fixture
async def django_backend() -> AsyncIterable[DjangoBackend[int]]:
    async with DjangoBackend[int].from_url("django://default") as backend:
        await backend.clear()
        try:
            yield backend
        finally:
            await backend.clear()


@pytest.fixture
async def redis_backend(request: pytest.FixtureRequest) -> AsyncIterable[RedisBackend]:
    if not request.config.getoption("test_redis", False):
        pytest.skip("Redis is skipped")
    async with RedisBackend.from_url("redis://localhost:6379") as backend:
        await backend.clear()
        try:
            yield backend
        finally:
            await backend.clear()


@pytest.fixture(params=["memory_backend", "django_backend", "redis_backend"])
def backend(request: pytest.FixtureRequest) -> AsyncBackend[bytes]:
    return cast(AsyncBackend[bytes], request.getfixturevalue(request.param))


def test_from_url_unknown_scheme() -> None:
    with pytest.raises(ValueError):
        from_url("invalid://")


async def test_get_existing(backend: AsyncBackend[bytes]) -> None:
    await backend.set("foo", b"hello")
    assert await backend.get("foo") == b"hello"


async def test_get_missing(backend: AsyncBackend[bytes]) -> None:
    with pytest.raises(KeyError):
        await backend.get("foo")


async def test_set_default(backend: AsyncBackend[bytes]) -> None:
    assert await backend.set("foo", b"hello", if_not_exists=True)
    assert not await backend.set("foo", b"world", if_not_exists=True)
    assert await backend.get("foo") == b"hello"


async def test_delete_existing(backend: AsyncBackend[bytes]) -> None:
    await backend.set("foo", b"hello")
    assert await backend.delete("foo")
    with pytest.raises(KeyError):
        await backend.get("foo")


async def test_delete_missing(backend: AsyncBackend[bytes]) -> None:
    assert not await backend.delete("foo")


async def test_set_get_many(backend: AsyncBackend[bytes]) -> None:
    await backend.set_many([("non-empty", b"foo"), ("empty", b"")])
    assert [entry async for entry in backend.get_many("non-empty", "missing", "empty")] == [
        ("non-empty", b"foo"),
        ("empty", b""),
    ]


async def test_set_with_ttl(backend: AsyncBackend[bytes]) -> None:
    await backend.set("foo", b"bar", time_to_live=timedelta(seconds=0.1))
    assert await backend.get("foo") == b"bar"
    await sleep(0.2)
    with pytest.raises(KeyError):
        await backend.get("foo")


async def test_expire_at(backend: AsyncBackend[bytes]) -> None:
    await backend.set("foo", b"bar")
    await backend.expire_at("foo", make_deadline(timedelta(seconds=0.1)))
    assert await backend.get("foo") == b"bar"
    await sleep(0.2)
    with pytest.raises(KeyError):
        await backend.get("foo")


async def test_expire_in(backend: AsyncBackend[bytes]) -> None:
    await backend.set("foo", b"bar")
    await backend.expire_in("foo", timedelta(seconds=0.1))
    assert await backend.get("foo") == b"bar"
    await sleep(0.2)
    with pytest.raises(KeyError):
        await backend.get("foo")


async def test_clear(backend: AsyncBackend[bytes]) -> None:
    await backend.set("foo", b"bar")
    await backend.clear()
    with pytest.raises(KeyError):
        await backend.get("foo")


async def test_get_empty_value(backend: AsyncBackend[bytes]) -> None:
    await backend.set("foo", b"")
    assert await backend.get("foo") == b""
