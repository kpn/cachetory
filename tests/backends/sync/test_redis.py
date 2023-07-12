from datetime import timedelta
from time import sleep
from typing import Iterable

from pytest import fixture, raises

from cachetory.backends.sync import RedisBackend
from cachetory.private.datetime import make_deadline
from tests.support import if_redis_enabled


@fixture
def backend() -> Iterable[RedisBackend]:
    with RedisBackend.from_url("redis://localhost:6379") as backend:
        backend.clear()
        try:
            yield backend
        finally:
            backend.clear()


@if_redis_enabled
def test_get_existing(backend: RedisBackend) -> None:
    backend.set("foo", b"hello")
    assert backend.get("foo") == b"hello"


@if_redis_enabled
async def test_get_missing(backend: RedisBackend) -> None:
    with raises(KeyError):
        backend.get("foo")


@if_redis_enabled
async def test_set_default(backend: RedisBackend) -> None:
    assert backend.set("foo", b"hello", if_not_exists=True)
    assert not backend.set("foo", b"world", if_not_exists=True)
    assert backend.get("foo") == b"hello"


@if_redis_enabled
async def test_delete_existing(backend: RedisBackend) -> None:
    backend.set("foo", b"hello")
    assert backend.delete("foo")
    with raises(KeyError):
        backend.get("foo")


@if_redis_enabled
async def test_delete_missing(backend: RedisBackend) -> None:
    assert not backend.delete("foo")


@if_redis_enabled
async def test_set_get_many(backend: RedisBackend) -> None:
    backend.set_many([("non-empty", b"foo"), ("empty", b"")])
    assert list(backend.get_many("non-empty", "missing", "empty")) == [("non-empty", b"foo"), ("empty", b"")]


@if_redis_enabled
async def test_set_with_ttl(backend: RedisBackend) -> None:
    backend.set("foo", b"bar", time_to_live=timedelta(seconds=0.25))
    assert backend.get("foo") == b"bar"
    sleep(0.5)
    with raises(KeyError):
        backend.get("foo")


@if_redis_enabled
async def test_expire_at(backend: RedisBackend) -> None:
    backend.set("foo", b"bar")
    backend.expire_at("foo", make_deadline(timedelta(seconds=0.25)))
    assert backend.get("foo") == b"bar"
    sleep(0.5)
    with raises(KeyError):
        backend.get("foo")


@if_redis_enabled
async def test_expire_in(backend: RedisBackend) -> None:
    backend.set("foo", b"bar")
    backend.expire_in("foo", timedelta(seconds=0.25))
    assert backend.get("foo") == b"bar"
    sleep(0.5)
    with raises(KeyError):
        backend.get("foo")


@if_redis_enabled
async def test_clear(backend: RedisBackend) -> None:
    backend.set("foo", b"bar")
    backend.clear()
    with raises(KeyError):
        backend.get("foo")


@if_redis_enabled
def test_get_empty_value(backend: RedisBackend) -> None:
    backend.set("foo", b"")
    assert backend.get("foo") == b""
