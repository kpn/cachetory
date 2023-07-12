from typing import AsyncIterable

import pytest

from cachetory.backends.async_ import DjangoBackend


@pytest.fixture
async def backend() -> AsyncIterable[DjangoBackend[int]]:
    async with DjangoBackend[int].from_url("django://default") as backend:
        backend.clear()
        try:
            yield backend
        finally:
            await backend.clear()


async def test_set_get(backend: DjangoBackend[int]) -> None:
    await backend.set("foo", 42)
    assert await backend.get("foo") == 42


async def test_get_missing(backend: DjangoBackend[int]) -> None:
    with pytest.raises(KeyError):
        assert await backend.get("foo") is None


async def test_set_default(backend: DjangoBackend[int]) -> None:
    await backend.set("foo", 42, if_not_exists=True)
    await backend.set("foo", 43, if_not_exists=True)
    assert await backend.get("foo") == 42


async def test_delete_existing(backend: DjangoBackend[int]) -> None:
    await backend.set("foo", 42)
    assert await backend.delete("foo")
    with pytest.raises(KeyError):
        await backend.get("foo")


async def test_delete_missing(backend: DjangoBackend[int]) -> None:
    assert not await backend.delete("foo")


async def test_set_get_many(backend: DjangoBackend[int]) -> None:
    await backend.set_many([("foo", 42)])
    assert [value async for value in backend.get_many("foo", "missing")] == [("foo", 42)]


async def test_clear(backend: DjangoBackend[int]) -> None:
    await backend.set("foo", 42)
    await backend.clear()
    with pytest.raises(KeyError):
        await backend.get("foo")
