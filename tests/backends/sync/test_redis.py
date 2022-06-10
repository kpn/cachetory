from typing import Generator

from pytest import fixture, mark

from cachetory.backends import SyncRedisBackend

test_redis = mark.skipif("not config.getoption('test_redis')")


@fixture
def backend() -> Generator[SyncRedisBackend, None, None]:
    backend = SyncRedisBackend.from_url("redis://localhost:6379")
    try:
        yield backend
    finally:
        backend._client.flushdb()  # TODO: add `.clear()` to cache backends.


@test_redis
def test_set_get(backend: SyncRedisBackend):
    backend.set("foo", b"hello")
    assert backend.get("foo") == b"hello"
