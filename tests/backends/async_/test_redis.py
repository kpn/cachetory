from asyncio import sleep
from datetime import timedelta
from typing import AsyncIterable

from pytest import fixture, mark, raises

from cachetory.backends import AsyncRedisBackend
from cachetory.private.datetime import make_deadline
from tests.support import if_redis_enabled


@fixture
async def backend() -> AsyncIterable[AsyncRedisBackend]:
    async with await AsyncRedisBackend.from_url("redis://localhost:6379") as backend:
        await backend.clear()
        try:
            yield backend
        finally:
            await backend.clear()


@if_redis_enabled
@mark.asyncio
async def test_get_existing(backend: AsyncRedisBackend):
    await backend.set("foo", b"hello")
    assert await backend.get("foo") == b"hello"


@if_redis_enabled
@mark.asyncio
async def test_get_missing(backend: AsyncRedisBackend):
    with raises(KeyError):
        await backend.get("foo")


@if_redis_enabled
@mark.asyncio
async def test_set_default(backend: AsyncRedisBackend):
    assert await backend.set("foo", b"hello", if_not_exists=True)
    assert not await backend.set("foo", b"world", if_not_exists=True)
    assert await backend.get("foo") == b"hello"


@if_redis_enabled
@mark.asyncio
async def test_delete_existing(backend: AsyncRedisBackend):
    await backend.set("foo", b"hello")
    assert await backend.delete("foo")
    with raises(KeyError):
        await backend.get("foo")


@if_redis_enabled
@mark.asyncio
async def test_delete_missing(backend: AsyncRedisBackend):
    assert not await backend.delete("foo")


@if_redis_enabled
@mark.asyncio
async def test_set_get_many(backend: AsyncRedisBackend):
    await backend.set_many([("shields", b"up"), ("alert", b"red")])
    assert [entry async for entry in backend.get_many("shields", "alert")] == [("shields", b"up"), ("alert", b"red")]


@if_redis_enabled
@mark.asyncio
async def test_set_with_ttl(backend: AsyncRedisBackend):
    await backend.set("foo", b"bar", time_to_live=timedelta(seconds=0.25))
    assert await backend.get("foo") == b"bar"
    await sleep(0.5)
    with raises(KeyError):
        await backend.get("foo")


@if_redis_enabled
@mark.asyncio
async def test_expire_at(backend: AsyncRedisBackend):
    await backend.set("foo", b"bar")
    await backend.expire_at("foo", make_deadline(timedelta(seconds=0.25)))
    assert await backend.get("foo") == b"bar"
    await sleep(0.5)
    with raises(KeyError):
        await backend.get("foo")


@if_redis_enabled
@mark.asyncio
async def test_expire_in(backend: AsyncRedisBackend):
    await backend.set("foo", b"bar")
    await backend.expire_in("foo", timedelta(seconds=0.25))
    assert await backend.get("foo") == b"bar"
    await sleep(0.5)
    with raises(KeyError):
        await backend.get("foo")


@if_redis_enabled
@mark.asyncio
async def test_clear(backend: AsyncRedisBackend):
    await backend.set("foo", b"bar")
    await backend.clear()
    with raises(KeyError):
        await backend.get("foo")
