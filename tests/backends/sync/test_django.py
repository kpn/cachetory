from collections.abc import Iterable

import pytest

from cachetory.backends.sync import DjangoBackend


@pytest.fixture
def backend() -> Iterable[DjangoBackend[int]]:
    with DjangoBackend[int].from_url("django://default") as backend:
        backend.clear()
        try:
            yield backend
        finally:
            backend.clear()


def test_set_get(backend: DjangoBackend[int]) -> None:
    backend.set("foo", 42)
    assert backend.get("foo") == 42


def test_get_missing(backend: DjangoBackend[int]) -> None:
    with pytest.raises(KeyError):
        assert backend.get("foo") is None


async def test_set_default(backend: DjangoBackend[int]) -> None:
    backend.set("foo", 42, if_not_exists=True)
    backend.set("foo", 43, if_not_exists=True)
    assert backend.get("foo") == 42


async def test_delete_existing(backend: DjangoBackend[int]) -> None:
    backend.set("foo", 42)
    assert backend.delete("foo")
    with pytest.raises(KeyError):
        backend.get("foo")


async def test_delete_missing(backend: DjangoBackend[int]) -> None:
    assert not backend.delete("foo")


async def test_set_get_many(backend: DjangoBackend[int]) -> None:
    backend.set_many([("foo", 42)])
    assert list(backend.get_many("foo", "missing")) == [("foo", 42)]


async def test_clear(backend: DjangoBackend[int]) -> None:
    backend.set("foo", 42)
    backend.clear()
    with pytest.raises(KeyError):
        backend.get("foo")
