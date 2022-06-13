# `cachetory`

[![Tests](https://github.com/kpn/cachetory/actions/workflows/tests.yml/badge.svg)](https://github.com/kpn/cachetory/actions/workflows/tests.yml)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/kpn/cachetory)

## Quickstart

```python
from cachetory import serializers
from cachetory.backends import async_ as async_backends
from cachetory.caches.async_ import Cache


cache = Cache[int](
    serializer=serializers.from_url("pickle+zstd://?pickle-protocol=4&compression-level=3"),
    backend=(await async_backends.from_url("redis://localhost:6379")),
)
async with cache:
    await cache.set("foo", 42)
    assert await cache.get("foo") == 42
```

### Non-async

```python
from cachetory import serializers
from cachetory.backends import sync as sync_backends
from cachetory.caches.sync import Cache


cache = Cache[int](
    serializer=serializers.from_url("pickle+zstd://"),
    backend=sync_backends.from_url("redis://localhost:6379"),
)
with cache:
    cache.set("foo", 42)
    assert cache.get("foo") == 42
```

### Specifying a backend

### Specifying a serializer

## Supported backends

### Redis

![schema: redis](https://img.shields.io/badge/schema-redis://-important)
![schema: rediss](https://img.shields.io/badge/schema-rediss://-important)
![schema: redis+unix](https://img.shields.io/badge/schema-redis+unix://-important)
![extra: redis-sync](https://img.shields.io/badge/sync-redis--sync-blue)
![extra: redis-async](https://img.shields.io/badge/async-redis--async-blueviolet)

### Memory

![schema: memory](https://img.shields.io/badge/schema-memory://-important)

### Dummy

![schema: dummy](https://img.shields.io/badge/schema-dummy://-important)

## Supported serializers

### Pickle

![schema: pickle](https://img.shields.io/badge/schema-pickle://-important)

### No-operation

![schema: noop](https://img.shields.io/badge/schema-noop://-important)
![schema: null](https://img.shields.io/badge/schema-null://-important)

`cachetory.serializers.NoopSerializer` does nothing and just bypasses value back and forth. Most of the backends don't support that and require some kind of serialization.

However, it is possible to use `NoopSerializer` with `MemoryBackend`, because the latter just stores all values in a Python dictionary and doesn't necessarily require values to be serialized.

## Supported compressors

Compressor is basically just a partial case of serializer: it's a serializer from `bytes` to and from `bytes`, which by definition provides some kind of data compression.

Compressors are packaged separately in `cachetory.serializers.compressors`.

## Zlib

![schema: zlib](https://img.shields.io/badge/schema-zlib://-important)

## Zstandard

![schema: zstd](https://img.shields.io/badge/schema-zstd://-important)
![schema: zstandard](https://img.shields.io/badge/schema-zstandard://-important)
![extra: zstd](https://img.shields.io/badge/extra-zstd-blue)
