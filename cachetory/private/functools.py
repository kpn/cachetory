from __future__ import annotations

from inspect import isawaitable
from typing import Any, Awaitable, Callable, TypeVar

from typing_extensions import overload

T = TypeVar("T")


@overload
def maybe_callable(__value: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    ...


@overload
def maybe_callable(__value: T, *args: Any, **kwargs: Any) -> T:
    ...


def maybe_callable(__value, *args, **kwargs):
    if callable(__value):
        return __value(*args, **kwargs)
    return __value


async def maybe_awaitable(__value: T | Awaitable[T]) -> T:
    return await __value if isawaitable(__value) else __value
