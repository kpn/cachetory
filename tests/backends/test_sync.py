from collections.abc import Iterable
from datetime import timedelta
from time import sleep
from typing import cast

import pytest

from cachetory.backends.sync import DjangoBackend, MemoryBackend, RedisBackend, from_url
from cachetory.interfaces.backends.sync import SyncBackend
from cachetory.private.datetime import make_deadline


@pytest.fixture
def memory_backend() -> Iterable[MemoryBackend[bytes]]:
    with MemoryBackend[bytes]() as backend:
        yield backend


@pytest.fixture
def django_backend() -> Iterable[DjangoBackend[bytes]]:
    with DjangoBackend[bytes].from_url("django://default") as backend:
        backend.clear()
        try:
            yield backend
        finally:
            backend.clear()


@pytest.fixture
def redis_backend(request: pytest.FixtureRequest) -> Iterable[RedisBackend]:
    if not request.config.getoption("test_redis", False):
        pytest.skip("Redis is skipped")
    with RedisBackend.from_url("redis://localhost:6379") as backend:
        backend.clear()
        try:
            yield backend
        finally:
            backend.clear()


@pytest.fixture(params=["memory_backend", "django_backend", "redis_backend"])
def backend(request: pytest.FixtureRequest) -> SyncBackend[bytes]:
    return cast(SyncBackend[bytes], request.getfixturevalue(request.param))


def test_from_url_unknown_scheme() -> None:
    with pytest.raises(ValueError):
        from_url("invalid://")


def test_get_existing(backend: SyncBackend[bytes]) -> None:
    backend.set("foo", b"hello")
    assert backend.get("foo") == b"hello"


def test_get_missing(backend: SyncBackend[bytes]) -> None:
    with pytest.raises(KeyError):
        backend.get("foo")


def test_set_default(backend: SyncBackend[bytes]) -> None:
    assert backend.set("foo", b"hello", if_not_exists=True)
    assert not backend.set("foo", b"world", if_not_exists=True)
    assert backend.get("foo") == b"hello"


def test_delete_existing(backend: SyncBackend[bytes]) -> None:
    backend.set("foo", b"hello")
    assert backend.delete("foo")
    with pytest.raises(KeyError):
        backend.get("foo")


def test_delete_missing(backend: SyncBackend[bytes]) -> None:
    assert not backend.delete("foo")


def test_delete_many(backend: SyncBackend[bytes]) -> None:
    backend.set("foo", b"foo")
    backend.set("qux", b"qux")
    backend.delete_many("foo", "bar")

    with pytest.raises(KeyError):
        backend.get("foo")
    assert backend.get("qux") == b"qux"


def test_delete_many_without_arguments(backend: SyncBackend[bytes]) -> None:
    """Verify that it does not raise an error."""
    backend.delete_many()


def test_set_get_many(backend: SyncBackend[bytes]) -> None:
    backend.set_many([("non-empty", b"foo"), ("empty", b"")])
    assert list(backend.get_many("non-empty", "missing", "empty")) == [("non-empty", b"foo"), ("empty", b"")]


def test_set_with_ttl(backend: SyncBackend[bytes]) -> None:
    backend.set("foo", b"bar", time_to_live=timedelta(seconds=0.1))
    assert backend.get("foo") == b"bar"
    sleep(0.2)
    with pytest.raises(KeyError):
        backend.get("foo")


def test_expire_at(backend: SyncBackend[bytes]) -> None:
    backend.set("foo", b"bar")
    backend.expire_at("foo", make_deadline(timedelta(seconds=0.1)))
    assert backend.get("foo") == b"bar"
    sleep(0.2)
    with pytest.raises(KeyError):
        backend.get("foo")


def test_expire_in(backend: SyncBackend[bytes]) -> None:
    backend.set("foo", b"bar")
    backend.expire_in("foo", timedelta(seconds=0.1))
    assert backend.get("foo") == b"bar"
    sleep(0.2)
    with pytest.raises(KeyError):
        backend.get("foo")


def test_clear(backend: SyncBackend[bytes]) -> None:
    backend.set("foo", b"bar")
    backend.clear()
    with pytest.raises(KeyError):
        backend.get("foo")


def test_get_empty_value(backend: SyncBackend[bytes]) -> None:
    backend.set("foo", b"")
    assert backend.get("foo") == b""
