from pytest import mark

from cachetory.backends.async_ import DummyBackend


@mark.asyncio
async def test_get_many():
    async with DummyBackend() as backend:
        assert [item async for item in backend.get_many("foo")] == []
