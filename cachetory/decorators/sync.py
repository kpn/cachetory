from __future__ import annotations

from contextlib import suppress
from datetime import timedelta
from functools import wraps
from typing import Callable

from typing_extensions import ParamSpec, Protocol

from cachetory.caches.sync import Cache
from cachetory.decorators import shared
from cachetory.interfaces.backends.private import WireT
from cachetory.interfaces.serializers import ValueT, ValueT_co
from cachetory.private.functools import into_callable

P = ParamSpec("P")
"""Original wrapped function parameter specification."""


def cached(
    cache: Cache[ValueT, WireT] | Callable[..., Cache[ValueT, WireT] | None] | None,  # no way to use `P` here
    *,
    make_key: Callable[..., str] = shared.make_default_key,  # no way to use `P` here
    time_to_live: timedelta | Callable[..., timedelta | None] | None = None,
    if_not_exists: bool = False,
    exclude: Callable[[str, ValueT], bool] | None = None,
) -> Callable[[Callable[P, ValueT]], _CachedCallable[P, ValueT]]:
    """
    Apply memoization to the wrapped callable.

    Args:
        cache:
            `Cache` instance or a callable tha returns a `Cache` instance for each function call.
            In the latter case the specified callable gets called with a wrapped function as the first argument,
            and the rest of the arguments next to it.
            If the callable returns `None`, the cache is skipped.
        make_key: callable to generate a custom cache key per each call.
        time_to_live:
            cached value expiration time or callable that returns the expiration time.
            The callable needs to accept keyword arguments, and it is given the cache key to
            compute the expiration time.
        if_not_exists: controls concurrent sets: if `True` – avoids overwriting a cached value.
        exclude: Optional callable to prevent a key-value pair from being cached if the callable returns true.
    """

    def wrap(callable_: Callable[P, ValueT], /) -> _CachedCallable[P, ValueT]:
        get_cache = into_callable(cache)
        get_time_to_live = into_callable(time_to_live)

        @wraps(callable_)
        def cached_callable(*args: P.args, **kwargs: P.kwargs) -> ValueT:
            cache_ = get_cache(callable_, *args, **kwargs)
            key_ = make_key(callable_, *args, **kwargs)

            if cache_ is not None:
                with suppress(KeyError):
                    # `KeyError` normally means the value is «non-cached».
                    return cache_[key_]

            value = callable_(*args, **kwargs)
            if cache_ is not None and (exclude is None or not exclude(key_, value)):
                time_to_live_ = get_time_to_live(key=key_)
                cache_.set(key_, value, time_to_live=time_to_live_, if_not_exists=if_not_exists)
            return value

        def purge(*args: P.args, **kwargs: P.kwargs) -> bool:
            if (cache := get_cache(callable_, *args, **kwargs)) is not None:
                key = make_key(callable_, *args, **kwargs)
                return cache.delete(key)
            else:
                return False

        cached_callable.purge = purge  # type: ignore[attr-defined]
        return cached_callable  # type: ignore[return-value]

    return wrap


class _CachedCallable(Protocol[P, ValueT_co]):
    """Protocol of the wrapped callable."""

    def __call__(*args: P.args, **kwargs: P.kwargs) -> ValueT_co: ...

    def purge(*args: P.args, **kwargs: P.kwargs) -> bool:
        """
        Delete the value that was cached using the same call arguments.

        Returns:
            whether a cached value existed
        """
