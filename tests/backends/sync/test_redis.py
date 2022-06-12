from datetime import timedelta
from time import sleep
from typing import Generator

from pytest import fixture, raises

from cachetory.backends import SyncRedisBackend
from cachetory.private.datetime import make_deadline
from tests.support import if_redis_enabled


@fixture
def backend() -> Generator[SyncRedisBackend, None, None]:
    with SyncRedisBackend.from_url("redis://localhost:6379") as backend:
        backend.clear()
        try:
            yield backend
        finally:
            backend.clear()


@if_redis_enabled
def test_get_existing(backend: SyncRedisBackend):
    backend.set("foo", b"hello")
    assert backend.get("foo") == b"hello"


@if_redis_enabled
async def test_get_missing(backend: SyncRedisBackend):
    with raises(KeyError):
        backend.get("foo")


@if_redis_enabled
async def test_set_default(backend: SyncRedisBackend):
    assert backend.set("foo", b"hello", if_not_exists=True)
    assert not backend.set("foo", b"world", if_not_exists=True)
    assert backend.get("foo") == b"hello"


@if_redis_enabled
async def test_delete_existing(backend: SyncRedisBackend):
    backend.set("foo", b"hello")
    assert backend.delete("foo")
    with raises(KeyError):
        backend.get("foo")


@if_redis_enabled
async def test_delete_missing(backend: SyncRedisBackend):
    assert not backend.delete("foo")


@if_redis_enabled
async def test_set_get_many(backend: SyncRedisBackend):
    backend.set_many([("shields", b"up"), ("alert", b"red")])
    assert list(backend.get_many("shields", "alert")) == [("shields", b"up"), ("alert", b"red")]


@if_redis_enabled
async def test_set_with_ttl(backend: SyncRedisBackend):
    backend.set("foo", b"bar", time_to_live=timedelta(seconds=0.25))
    assert backend.get("foo") == b"bar"
    sleep(0.5)
    with raises(KeyError):
        backend.get("foo")


@if_redis_enabled
async def test_expire_at(backend: SyncRedisBackend):
    backend.set("foo", b"bar")
    backend.expire_at("foo", make_deadline(timedelta(seconds=0.25)))
    assert backend.get("foo") == b"bar"
    sleep(0.5)
    with raises(KeyError):
        backend.get("foo")


@if_redis_enabled
async def test_expire_in(backend: SyncRedisBackend):
    backend.set("foo", b"bar")
    backend.expire_in("foo", timedelta(seconds=0.25))
    assert backend.get("foo") == b"bar"
    sleep(0.5)
    with raises(KeyError):
        backend.get("foo")


@if_redis_enabled
async def test_clear(backend: SyncRedisBackend):
    backend.set("foo", b"bar")
    backend.clear()
    with raises(KeyError):
        backend.get("foo")
