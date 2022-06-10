from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy_typing_asserts import assert_type

from cachetory.backends.memory import MemoryBackend

if TYPE_CHECKING:
    # Verify the `__getitem__` return type.
    assert_type[int](MemoryBackend[int]()["foo"])
