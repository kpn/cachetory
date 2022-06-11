from datetime import datetime, timedelta, timezone

from freezegun import freeze_time
from pytest import fixture, raises

from cachetory.backends.sync.memory import SyncMemoryBackend


@fixture
def backend() -> SyncMemoryBackend[int]:
    return SyncMemoryBackend[int]()


def test_get_item_existing(backend: SyncMemoryBackend[int]):
    backend.set("foo", 42)
    assert backend.get("foo") == 42


def test_get_item_missing(backend: SyncMemoryBackend[int]):
    with raises(KeyError):
        backend.get("foo")


def test_set_default(backend: SyncMemoryBackend[int]):
    backend.set("foo", 42, if_not_exists=True)
    backend.set("foo", 43, if_not_exists=True)
    assert backend.get("foo") == 42
    assert backend.size == 1


def test_delete_existing(backend: SyncMemoryBackend[int]):
    backend.set("foo", 42)
    assert backend.delete("foo")


def test_delete_missing(backend: SyncMemoryBackend[int]):
    assert not backend.delete("foo")


def test_set_get_many(backend: SyncMemoryBackend[int]):
    backend.set_many([("foo", 42), ("bar", 100500)])
    assert backend.size == 2
    assert backend.get_many("foo", "bar") == [("foo", 42), ("bar", 100500)]


def test_set_with_ttl(backend: SyncMemoryBackend[int]):
    with freeze_time("2022-06-11 21:33:00"):
        backend.set("foo", 42, time_to_live=timedelta(seconds=59))
    with freeze_time("2022-06-11 21:33:58"):
        assert backend.get("foo") == 42
    with freeze_time("2022-06-11 21:34:00"), raises(KeyError):
        assert backend.get("foo")
    assert backend.size == 0


def test_expire_at(backend: SyncMemoryBackend[int]):
    backend.set("foo", 42)
    backend.expire_at("foo", datetime(2022, 6, 10, 21, 50, 00, tzinfo=timezone.utc))

    with freeze_time("2022-06-10 21:49:59"):
        assert backend.get("foo") == 42
    with freeze_time("2022-06-10 21:50:00"), raises(KeyError):
        assert backend.get("foo")
    assert backend.size == 0


def test_expire_in(backend: SyncMemoryBackend[int]):
    with freeze_time("2022-06-10 21:49:00"):
        backend.set("foo", 42)
        backend.expire_in("foo", timedelta(seconds=59))
    with freeze_time("2022-06-10 21:50:00"), raises(KeyError):
        assert backend.get("foo")
    assert backend.size == 0


def test_clear(backend: SyncMemoryBackend[int]):
    backend.set("foo", 42)
    backend.clear()
    assert backend.size == 0
