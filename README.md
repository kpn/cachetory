# Cachetory

[![PyPI](https://img.shields.io/pypi/v/cachetory?logo=python&logoColor=yellow)](https://pypi.org/project/cachetory/)
[![Python versions](https://img.shields.io/pypi/pyversions/cachetory?logo=python&logoColor=yellow)](https://pypi.org/project/cachetory/)
[![Checks](https://img.shields.io/github/actions/workflow/status/kpn/cachetory/check.yml?label=checks&logo=github)](https://github.com/kpn/cachetory/actions/workflows/check.yml)
[![Coverage](https://codecov.io/gh/kpn/cachetory/branch/main/graph/badge.svg?token=UNYTTvxiWk)](https://codecov.io/gh/kpn/cachetory)
![Code style](https://img.shields.io/badge/code%20style-ruff-000000.svg)

## Documentation

<a href="https://kpn.github.io/cachetory/">
    <img alt="Documentation" height="30em" src="https://img.shields.io/github/actions/workflow/status/kpn/cachetory/docs.yml?label=documentation&logo=github">
</a>

## Sneak peak

```python
from cachetory import serializers
from cachetory.backends import async_ as async_backends
from cachetory.caches.async_ import Cache


cache = Cache[int, bytes](
    serializer=serializers.from_url("pickle://?pickle-protocol=4"),
    backend=async_backends.from_url("redis://localhost:6379"),
)

async def main() -> None:
    await cache.set("foo", 42)
    assert await cache.get("foo") == 42
```
