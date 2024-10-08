from __future__ import annotations

from collections.abc import Awaitable
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Callable, TypeVar, cast

T = TypeVar("T")


def into_callable(value: Callable[..., T] | T) -> Callable[..., T]:
    if not callable(value):

        def callable_(*args: Any, **kwargs: Any) -> T:
            return value

        return callable_

    else:
        return value


def into_async_callable(value: Callable[..., Awaitable[T]] | Callable[..., T] | T) -> Callable[..., Awaitable[T]]:
    if not callable(value):

        async def callable_(*args: Any, **kwargs: Any) -> T:
            return value

        return callable_

    if not iscoroutinefunction(value):

        @wraps(value)
        async def callable_(*args: Any, **kwargs: Any) -> T:
            return cast(T, value(*args, **kwargs))

        return callable_

    else:
        return value
