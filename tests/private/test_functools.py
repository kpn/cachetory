from __future__ import annotations

from typing import Awaitable, Callable

import pytest

from cachetory.private.functools import maybe_awaitable, maybe_callable


async def _async_callable() -> int:
    return 42


@pytest.mark.parametrize("argument", [42, lambda: 42])
def test_maybe_callable(argument: int | Callable[[], int]) -> None:
    assert maybe_callable(argument) == 42


@pytest.mark.parametrize("callable_", [lambda: 42, _async_callable])
async def test_maybe_awaitable(callable_: Callable[[], int] | Callable[[], Awaitable[int]]) -> None:
    assert await maybe_awaitable(callable_())
