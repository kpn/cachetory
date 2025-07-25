from pytest import fixture, raises

from cachetory import serializers
from cachetory.backends import sync as sync_backends
from cachetory.caches.sync import Cache
from tests.support import if_redis_enabled


@fixture
def memory_cache() -> Cache[int, bytes]:
    return Cache(
        serializer=serializers.from_url("pickle+zstd://?pickle-protocol=4&compression-level=3"),
        backend=sync_backends.from_url("memory://"),
    )


def test_get_set_in_memory(memory_cache: Cache[int, bytes]) -> None:
    memory_cache.set("foo", 42)
    assert memory_cache.get("foo") == 42


def test_set_item(memory_cache: Cache[int, bytes]) -> None:
    memory_cache["foo"] = 42
    assert memory_cache.get("foo") == 42


def test_get_default(memory_cache: Cache[int, bytes]) -> None:
    assert memory_cache.get("missing", 100500) == 100500


def test_get_many(memory_cache: Cache[int, bytes]) -> None:
    memory_cache.set("foo", 42)
    assert memory_cache.get_many("foo", "bar") == {"foo": 42}


def test_set_many(memory_cache: Cache[int, bytes]) -> None:
    memory_cache.set_many({"foo": 42, "bar": 100500})
    assert memory_cache.get("foo") == 42
    assert memory_cache.get("bar") == 100500


def delete_many(memory_cache: Cache[int, bytes]) -> None:
    memory_cache.set_many({"1": 1, "2": 2, "3": 3})
    memory_cache.delete_many("1", "2")
    assert memory_cache.get_many("1", "2", "3") == {"3": 3}


def test_delete(memory_cache: Cache[int, bytes]) -> None:
    memory_cache.set("foo", 42)
    assert memory_cache.delete("foo")
    assert not memory_cache.delete("foo")
    assert memory_cache.get("foo") is None


def test_clear_cache(memory_cache: Cache[int, bytes]) -> None:
    memory_cache.set("foo", 42)
    memory_cache.set("bar", 42)

    memory_cache.clear()

    assert memory_cache.get("foo") is None
    assert memory_cache.get("bar") is None


def test_del_item(memory_cache: Cache[int, bytes]) -> None:
    memory_cache.set("foo", 42)
    del memory_cache["foo"]
    assert memory_cache.get("foo") is None


def test_del_missing_item(memory_cache: Cache[int, bytes]) -> None:
    with raises(KeyError):
        del memory_cache["missing"]


@if_redis_enabled
def test_get_set_in_redis() -> None:
    cache = Cache[int, bytes](
        serializer=serializers.from_url("pickle+zlib://"),
        backend=sync_backends.from_url("redis://localhost:6379"),
    )
    with cache:
        cache.set("foo", 42)
        assert cache.get("foo") == 42
