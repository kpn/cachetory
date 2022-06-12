from typing import Generator

from pytest import fixture

from cachetory.backends import SyncRedisBackend
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
