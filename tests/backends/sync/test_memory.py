from datetime import datetime, timedelta, timezone

from pytest import fixture, raises
from freezegun import freeze_time

from cachetory.backends.sync.memory import SyncMemoryBackend


@fixture
def backend() -> SyncMemoryBackend[int]:
    return SyncMemoryBackend[int]()


def test_get_item_existing(backend: SyncMemoryBackend[int]):
    backend.set("foo", 42)
    assert backend["foo"] == 42


def test_get_item_missing(backend: SyncMemoryBackend[int]):
    with raises(KeyError):
        _ = backend["foo"]


def test_set_default(backend: SyncMemoryBackend[int]):
    backend.set_default("foo", 42)
    backend.set_default("foo", 43)
    assert backend["foo"] == 42
    assert backend.size == 1


def test_delete_existing(backend: SyncMemoryBackend[int]):
    backend.set("foo", 42)
    assert backend.delete("foo")


def test_delete_missing(backend: SyncMemoryBackend[int]):
    assert not backend.delete("foo")


def test_del_item_existing(backend: SyncMemoryBackend[int]):
    backend.set("foo", 42)
    del backend["foo"]
    assert backend.get("foo") is None


def test_del_item_missing(backend: SyncMemoryBackend[int]):
    with raises(KeyError):
        del backend["foo"]


def test_set_get_many(backend: SyncMemoryBackend[int]):
    backend.set_many([("foo", 42), ("bar", 100500)])
    assert backend.size == 2
    assert backend.get_many("foo", "bar") == {"foo": 42, "bar": 100500}


def test_set_with_ttl(backend: SyncMemoryBackend[int]):
    with freeze_time("2022-06-11 21:33:00"):
        backend.set("foo", 42, timedelta(seconds=59))
    with freeze_time("2022-06-11 21:33:58"):
        assert backend["foo"] == 42
    with freeze_time("2022-06-11 21:34:00"):
        assert backend.get("foo") is None
    assert backend.size == 0


def test_expire_at(backend: SyncMemoryBackend[int]):
    backend.set("foo", 42)
    backend.expire_at("foo", datetime(2022, 6, 10, 21, 50, 00, tzinfo=timezone.utc))

    with freeze_time("2022-06-10 21:49:59"):
        assert backend["foo"] == 42
    with freeze_time("2022-06-10 21:50:00"):
        assert backend.get("foo") is None
    assert backend.size == 0


def test_expire_in(backend: SyncMemoryBackend[int]):
    with freeze_time("2022-06-10 21:49:00"):
        backend.set("foo", 42)
        backend.expire_in("foo", timedelta(seconds=59))
    with freeze_time("2022-06-10 21:50:00"):
        assert backend.get("foo") is None
    assert backend.size == 0
