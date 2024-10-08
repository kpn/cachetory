from __future__ import annotations

from collections.abc import Awaitable
from datetime import timedelta
from functools import wraps
from typing import Callable, Protocol

from typing_extensions import ParamSpec

from cachetory.caches.async_ import Cache
from cachetory.decorators import shared
from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.serializers import ValueT, ValueT_co
from cachetory.private.functools import into_async_callable

P = ParamSpec("P")
"""Original wrapped function parameter specification."""


def cached(
    cache: Cache[ValueT, WireT]
    | Callable[..., Cache[ValueT, WireT] | None]
    | Callable[..., Awaitable[Cache[ValueT, WireT] | None]]
    | None,
    *,
    make_key: Callable[..., str] = shared.make_default_key,  # no way to use `P` here
    time_to_live: timedelta | Callable[..., timedelta | None] | Callable[..., Awaitable[timedelta]] | None = None,
    if_not_exists: bool = False,
    exclude: Callable[[str, ValueT], bool] | Callable[[str, ValueT], Awaitable[bool]] | None = None,
) -> Callable[[Callable[P, Awaitable[ValueT]]], _CachedCallable[P, Awaitable[ValueT]]]:
    """
    Apply memoization to the wrapped callable.

    Args:
        cache:
            `Cache` instance or a callable (sync or async) that returns a `Cache` instance for each function call.
            In the latter case the specific callable gets called with a wrapped function as the first argument,
            and the rest of the arguments next to it.
            If the callable returns `None`, the cache is skipped.
        make_key: callable to generate a custom cache key per each call.
        time_to_live:
            cached value expiration time or a callable (sync or async) that returns the expiration time.
            The callable needs to accept keyword arguments, and it is given the cache key to
            compute the expiration time.
        if_not_exists: controls concurrent sets: if `True` – avoids overwriting a cached value.
        exclude: Optional callable to prevent a key-value pair from being cached if the callable returns true.
    """

    def wrap(callable_: Callable[P, Awaitable[ValueT]], /) -> _CachedCallable[P, Awaitable[ValueT]]:
        get_cache = into_async_callable(cache)
        get_time_to_live = into_async_callable(time_to_live)
        exclude_: Callable[[str, ValueT], Awaitable[bool]] | None = (
            into_async_callable(exclude) if exclude is not None else None
        )

        @wraps(callable_)
        async def cached_callable(*args: P.args, **kwargs: P.kwargs) -> ValueT:
            cache_ = await get_cache(callable_, *args, **kwargs)
            key_ = make_key(callable_, *args, **kwargs)

            if cache_ is not None:
                value = await cache_.get(key_)
            else:
                value = None

            if value is None:
                value = await callable_(*args, **kwargs)
                if cache_ is not None and (exclude_ is None or not await exclude_(key_, value)):
                    time_to_live_ = await get_time_to_live(key=key_)
                    await cache_.set(key_, value, time_to_live=time_to_live_, if_not_exists=if_not_exists)

            return value

        async def purge(*args: P.args, **kwargs: P.kwargs) -> bool:
            """
            Delete the value that was cached using the same call arguments.

            Returns:
                whether a cached value existed
            """
            if (cache := await get_cache(callable_, *args, **kwargs)) is not None:
                key = make_key(callable_, *args, **kwargs)
                return await cache.delete(key)
            else:
                return False

        cached_callable.purge = purge  # type: ignore[attr-defined]
        return cached_callable  # type: ignore[return-value]

    return wrap


class _CachedCallable(Protocol[P, ValueT_co]):
    """Protocol of the wrapped callable."""

    def __call__(*args: P.args, **kwargs: P.kwargs) -> ValueT_co: ...

    async def purge(*args: P.args, **kwargs: P.kwargs) -> bool:
        """
        Delete the value that was cached using the same call arguments.

        Returns:
            whether a cached value existed
        """
