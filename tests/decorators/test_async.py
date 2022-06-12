from pytest import fixture, mark

from cachetory.backends.async_ import MemoryBackend
from cachetory.caches.async_ import Cache
from cachetory.decorators.async_ import cached
from cachetory.serializers import NoopSerializer


@fixture
def cache() -> Cache[int]:
    return Cache(serializer=NoopSerializer(), backend=MemoryBackend[int]())


@mark.asyncio
async def test_simple(cache: Cache[int]):
    call_counter = 0

    @cached(cache)
    async def expensive_function(arg: int, *, kwarg: int) -> int:
        assert arg == 1, "the positional argument is not forwarded"
        assert kwarg == 2, "the keyword argument is not forwarded"
        nonlocal call_counter
        call_counter += 1
        return 42

    assert await expensive_function(1, kwarg=2) == 42, "the return value is not forwarded"
    assert call_counter == 1
    await expensive_function(1, kwarg=2)
    assert call_counter == 1, "cache did not work"
