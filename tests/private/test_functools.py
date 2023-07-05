from __future__ import annotations

from typing import Awaitable, Callable

import pytest

from cachetory.private.functools import into_async_callable, into_callable


async def _async_callable() -> int:
    return 42


@pytest.mark.parametrize("value", [42, lambda: 42])
def test_into_callable(value: int | Callable[[], int]) -> None:
    assert into_callable(value)() == 42


@pytest.mark.parametrize("value", [42, lambda: 42, _async_callable])
async def test_into_async_callable(value: int | Callable[[], int] | Callable[[], Awaitable[int]]) -> None:
    assert await into_async_callable(value)() == 42
