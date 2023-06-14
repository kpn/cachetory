import inspect
from hashlib import blake2s
from typing import Any, Awaitable, Callable, TypeVar, overload

from typing_extensions import ParamSpec


def make_default_key(callable_: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
    """Generate cache key given the callable and the arguments it's being called with."""

    # noinspection PyUnresolvedReferences
    parts = (
        callable_.__module__,
        callable_.__qualname__,
        # Since we join with `:`, we need to «escape» `:`s with `::`.
        *(str(arg).replace(":", "::") for arg in args),
        *(f"{str(key).replace(':', '::')}={str(value).replace(':', '::')}" for key, value in sorted(kwargs.items())),
    )
    return ":".join(parts)


def make_default_hashed_key(callable_: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
    """
    Generate a hashed cache key given the callable and the arguments it's being called with.

    Uses `blake2s` as the fastest algorithm from `hashlib`.
    """
    return blake2s(make_default_key(callable_, *args, **kwargs).encode()).hexdigest()


P = ParamSpec("P")
T = TypeVar("T")


@overload
async def call_sync_or_async(func: Callable[P, Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> T:
    ...


@overload
async def call_sync_or_async(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    ...


async def call_sync_or_async(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    return func(*args, **kwargs)
