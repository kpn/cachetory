from pytest import fixture

from cachetory.backends import SyncMemoryBackend
from cachetory.caches.sync import Cache
from cachetory.decorators.sync import cached
from cachetory.serializers import NoopSerializer


@fixture
def cache() -> Cache[int]:
    return Cache(serializer=NoopSerializer(), backend=SyncMemoryBackend[int]())


def test_simple(cache: Cache[int]):
    call_counter = 0

    @cached(cache)
    def expensive_function(arg: int, *, kwarg: int) -> int:
        assert arg == 1, "the positional argument is not forwarded"
        assert kwarg == 2, "the keyword argument is not forwarded"
        nonlocal call_counter
        call_counter += 1
        return 42

    assert expensive_function(1, kwarg=2) == 42, "the return value is not forwarded"
    assert call_counter == 1
    expensive_function(1, kwarg=2)
    assert call_counter == 1, "cache did not work"
