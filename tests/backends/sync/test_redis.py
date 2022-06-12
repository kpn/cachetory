from typing import Generator

from pytest import fixture, mark

from cachetory.backends import SyncRedisBackend

_test_redis = mark.skipif("not config.getoption('test_redis')")


@fixture
def backend() -> Generator[SyncRedisBackend, None, None]:
    with SyncRedisBackend.from_url("redis://localhost:6379") as backend:
        backend.clear()
        try:
            yield backend
        finally:
            backend.clear()


@_test_redis
def test_get_existing(backend: SyncRedisBackend):
    backend.set("foo", b"hello")
    assert backend.get("foo") == b"hello"
