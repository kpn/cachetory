from asyncio import sleep
from datetime import timedelta
from typing import AsyncIterable

from pytest import fixture, mark, raises

from cachetory.backends.async_ import RedisBackend
from cachetory.private.datetime import make_deadline
from tests.support import if_redis_enabled


@fixture
async def backend() -> AsyncIterable[RedisBackend]:
    async with RedisBackend.from_url("redis://localhost:6379") as backend:
        await backend.clear()
        try:
            yield backend
        finally:
            await backend.clear()


@if_redis_enabled
@mark.asyncio
async def test_get_existing(backend: RedisBackend) -> None:
    await backend.set("foo", b"hello")
    assert await backend.get("foo") == b"hello"


@if_redis_enabled
@mark.asyncio
async def test_get_missing(backend: RedisBackend) -> None:
    with raises(KeyError):
        await backend.get("foo")


@if_redis_enabled
@mark.asyncio
async def test_set_default(backend: RedisBackend) -> None:
    assert await backend.set("foo", b"hello", if_not_exists=True)
    assert not await backend.set("foo", b"world", if_not_exists=True)
    assert await backend.get("foo") == b"hello"


@if_redis_enabled
@mark.asyncio
async def test_delete_existing(backend: RedisBackend) -> None:
    await backend.set("foo", b"hello")
    assert await backend.delete("foo")
    with raises(KeyError):
        await backend.get("foo")


@if_redis_enabled
@mark.asyncio
async def test_delete_missing(backend: RedisBackend) -> None:
    assert not await backend.delete("foo")


@if_redis_enabled
@mark.asyncio
async def test_set_get_many(backend: RedisBackend) -> None:
    await backend.set_many([("non-empty", b"foo"), ("empty", b"")])
    assert [entry async for entry in backend.get_many("non-empty", "missing", "empty")] == [
        ("non-empty", b"foo"),
        ("empty", b""),
    ]


@if_redis_enabled
@mark.asyncio
async def test_set_with_ttl(backend: RedisBackend) -> None:
    await backend.set("foo", b"bar", time_to_live=timedelta(seconds=0.25))
    assert await backend.get("foo") == b"bar"
    await sleep(0.5)
    with raises(KeyError):
        await backend.get("foo")


@if_redis_enabled
@mark.asyncio
async def test_expire_at(backend: RedisBackend) -> None:
    await backend.set("foo", b"bar")
    await backend.expire_at("foo", make_deadline(timedelta(seconds=0.25)))
    assert await backend.get("foo") == b"bar"
    await sleep(0.5)
    with raises(KeyError):
        await backend.get("foo")


@if_redis_enabled
@mark.asyncio
async def test_expire_in(backend: RedisBackend) -> None:
    await backend.set("foo", b"bar")
    await backend.expire_in("foo", timedelta(seconds=0.25))
    assert await backend.get("foo") == b"bar"
    await sleep(0.5)
    with raises(KeyError):
        await backend.get("foo")


@if_redis_enabled
@mark.asyncio
async def test_clear(backend: RedisBackend) -> None:
    await backend.set("foo", b"bar")
    await backend.clear()
    with raises(KeyError):
        await backend.get("foo")


@if_redis_enabled
@mark.asyncio
async def test_get_empty_value(backend: RedisBackend) -> None:
    await backend.set("foo", b"")
    assert await backend.get("foo") == b""
