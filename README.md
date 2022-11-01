# `cachetory`

[![PyPI](https://img.shields.io/pypi/v/cachetory)](https://pypi.org/project/cachetory/)
[![Tests](https://github.com/kpn/cachetory/actions/workflows/tests.yml/badge.svg)](https://github.com/kpn/cachetory/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/kpn/cachetory/branch/main/graph/badge.svg?token=UNYTTvxiWk)](https://codecov.io/gh/kpn/cachetory)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/kpn/cachetory)

## Quickstart

```python
from cachetory import serializers
from cachetory.backends import async_ as async_backends
from cachetory.caches.async_ import Cache


cache = Cache[int](
    serializer=serializers.from_url("pickle+zstd://?pickle-protocol=4&compression-level=3"),
    backend=async_backends.from_url("redis://localhost:6379"),
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

## Tutorial

### Supported operations

| Operation                                         |                                                              |
|:--------------------------------------------------|:-------------------------------------------------------------|
| `get(key, default)`                               | **Retrieve** a value (or return a default one)               |
| `__getitem__(key)`                                | **Retrieve** a value or raise `KeyError` (only sync `Cache`) |
| `get_many(*keys)`                                 | **Retrieve** many values as a dictionary                     |
| `set(key, value, *, time_to_live, if_not_exists)` | **Set** a value and return if the value has been changed     |
| `__setitem__(key, value)`                         | **Set** a value (only sync `Cache`)                          |
| `set_many(items)`                                 | **Set** many values                                          |
| `expire_in(key, time_to_live)`                    | **Set** an expiration duration on a key                      |
| `delete(key)`                                     | **Delete** a key and return whether the key existed          |
| `__delitem__(key)`                                | **Delete** a key (only sync `Cache`)                         |

### Instantiating a `Cache`

Both sync and async `Cache`s requires at least these parameters to work:

- `backend`: functions as a storage
- `serializer`: is responsible for converting actual values from and to something that a backend would be able to store

`Cache` may be annotated with a value type, like this: `Cache[ValueT]`, which provides type hints for the cache methods.

### Instantiating a backend

There is a few ways to instantiate a backend:

- By **directly instantiating** a backend class via its `__init__`
- By instantiating a specific backend class **via its `from_url` class method**. In that case the URL is forwarded to underlying client (if any)
- **By using `cachetory.[sync|async_].from_url` function.** In that case specific backend class is chosen by the URL's scheme (see the scheme badges below), and the URL is forwarded to its `from_url` class method. This is especially useful to configure an arbitrary backend from a single configuration option – instead of hard-coding a specific backend class.

#### Examples

```python
import redis
import cachetory.backends.sync
import cachetory.backends.async_

backend = cachetory.backends.sync.from_url("memory://")
backend = cachetory.backends.async_.from_url("dummy://")
backend = cachetory.backends.sync.RedisBackend(redis.Redis(...))
backend = cachetory.backends.async_.from_url("redis://localhost:6379/1")
```

### Instantiating a serializer

Instantiating of a serializer is very much similar to that of a backend. To instantiate it by a URL use `cachetory.serializers.from_url` – unlike the back-end case there are no separate sync and async versions.

`cachetory.serializers.from_url` supports scheme joining with `+`, as in `pickle+zlib://`. In that case multiple serializers are instantiated and applied sequentially (in the example a value would be serialized by `pickle` and the serialized value is then compressed by `zlib`). Deserialization order is, of course, the opposite.

#### Examples

```python
import pickle

import cachetory.serializers

serializer = cachetory.serializers.from_url("pickle+zstd://")
serializer = cachetory.serializers.from_url("pickle+zstd://?pickle-protocol=4&compression-level=3")
serializer = cachetory.serializers.from_url("null://")
serializer = cachetory.serializers.NoopSerializer()
serializer = cachetory.serializers.PickleSerializer(pickle_protocol=pickle.DEFAULT_PROTOCOL)
```

### Decorators

#### Decorate a function with `@cached`

`@cached` performs [memoization](https://en.wikipedia.org/wiki/Memoization) of a wrapped function:

```python
from cachetory.caches.sync import Cache
from cachetory.decorators.shared import make_default_key
from cachetory.decorators.sync import cached

cache = Cache[int](backend=..., serializer=...)
another_cache = Cache[int](backend=..., serializer=...)


@cached(
    cache,  # may also be a callable that returns a specific cache for each call, e.g.:
    # `cache=lambda wrapped_callable, *args, **kwargs: cache if … else another_cache`

    # The following parameters are optional (shown the defaults):
    make_key=make_default_key,  # cache key generator
    time_to_live=None,  # forwarded to `Cache.set`
    if_not_exists=False,  # forwarded to `Cache.set`
)
def expensive_function() -> int:
    return 42
```

There's a few `make_key` functions provided by default:

- `cachetory.decorators.shared.make_default_key` builds a human-readable cache key out of decorated function fully-qualified name and stringified arguments. The length of the key depends on the argument values.
- `cachetory.decorators.shared.make_default_hashed_key` calls `make_default_key` under the hood but hashes the key and returns a hash hex digest – making it a fixed-length key and not human-readable.

## Supported backends

The badges indicate which schemes are supported by a particular backend, and which package extras are required for it – if any:

### Redis

![scheme: redis](https://img.shields.io/badge/scheme-redis://-important)
![scheme: rediss](https://img.shields.io/badge/scheme-rediss://-important)
![scheme: redis+unix](https://img.shields.io/badge/scheme-redis+unix://-important)
![extra: redis](https://img.shields.io/badge/extra-redis-blue)

| Sync                                   | Async                                    |
|:---------------------------------------|:-----------------------------------------|
| `cachetory.backends.sync.RedisBackend` | `cachetory.backends.async_.RedisBackend` |

The URL is forwarded to the underlying client, which means one can use whatever options the client provides. The only special case is `redis+unix://`: the leading `redis+` is first stripped and the rest is forwarded to the client.

All the cache operations are **atomic** in both sync and async, including `get_many` and `set_many`.

Consider explicitly adding [`hiredis`](https://github.com/redis/hiredis) to your dependencies for faster performance.

### Memory

![scheme: memory](https://img.shields.io/badge/scheme-memory://-important)

| Sync                                    | Async                                     |
|:----------------------------------------|:------------------------------------------|
| `cachetory.backends.sync.MemoryBackend` | `cachetory.backends.async_.MemoryBackend` |

Simple memory backend that stores values in a plain dictionary.

Note the following **caveats**:

- This backend does **not** copy values. Meaning that mutating a stored value mutates it in the backend too. If this is not desirable, consider using another serializer or making up your own serializer which copies values in its `serialize` method.
- Expired items actually get deleted **only** when accessed. If you put a value into the backend and never try to retrieve it – it'll stay in memory forever.

### Dummy

![scheme: dummy](https://img.shields.io/badge/scheme-dummy://-important)

| Sync                                    | Async                                     |
|:----------------------------------------|:------------------------------------------|
| `cachetory.backends.sync.DummyBackend`  | `cachetory.backends.async_.DummyBackend`  |

Dummy backend that always succeeds but never stores anything. Any values get forgotten immediately,
and operations behave as if the cache always is empty.

## Supported serializers

### Pickle

![scheme: pickle](https://img.shields.io/badge/scheme-pickle://-important)

Serializes using the standard [`pickle`](https://docs.python.org/3/library/pickle.html) module.

| Class                                    |
|:-----------------------------------------|
| `cachetory.serializers.PickleSerializer` |

| URL parameter     |                                                                                                  |
|:------------------|--------------------------------------------------------------------------------------------------|
| `pickle-protocol` | Version of [`pickle` protocol](https://docs.python.org/3/library/pickle.html#data-stream-format) |

### No-operation

![scheme: noop](https://img.shields.io/badge/scheme-noop://-important)
![scheme: null](https://img.shields.io/badge/scheme-null://-important)

| Class                                   |
|:----------------------------------------|
| `cachetory.serializers.NoopSerializer`  |

`NoopSerializer` does nothing and just bypasses value back and forth. Most of the backends don't support that and require some kind of serialization.

However, it is possible to use `NoopSerializer` with `MemoryBackend`, because the latter just stores all values in a Python dictionary and doesn't necessarily require values to be serialized.

## Supported compressors

**Compressor** is basically just a partial case of serializer: it's a serializer from `bytes` to and from `bytes`, which by definition provides some kind of data compression.

It also means that you can use a compressor alone, effectively making a cache of compressed blobs:

```python
from datetime import timedelta

from cachetory.caches.sync import Cache
from cachetory.serializers.compressors import ZlibCompressor
from cachetory.backends.sync import RedisBackend

cache = Cache[bytes](
    serializer=ZlibCompressor(),
    backend=RedisBackend(...),
)
cache.set(
    "my-blob",
    b"this huge blob will be compressed and stored in Redis for an hour",
    time_to_live=timedelta(hours=1),
)
```

## Zlib

![scheme: zlib](https://img.shields.io/badge/scheme-zlib://-important)

Uses the built-in [`zlib`](https://docs.python.org/3/library/zlib.html) module.

| Class                                              |
|:---------------------------------------------------|
| `cachetory.serializers.compressors.ZlibCompressor` |

| URL parameter         |                                                     |
|:----------------------|-----------------------------------------------------|
| `compression-level`   | From `0` (no compression) to `9` (best compression) |

## Zstandard

![scheme: zstd](https://img.shields.io/badge/scheme-zstd://-important)
![scheme: zstandard](https://img.shields.io/badge/scheme-zstandard://-important)
![extra: zstd](https://img.shields.io/badge/extra-zstd-blue)

Uses [`python-zstd`](https://github.com/sergey-dryabzhinsky/python-zstd) for [Zstandard](https://facebook.github.io/zstd/) compression.

| Class                                              |
|:---------------------------------------------------|
| `cachetory.serializers.compressors.ZstdCompressor` |

| URL parameter         |                                                             |
|:----------------------|-------------------------------------------------------------|
| `compression-level`   | See: https://github.com/sergey-dryabzhinsky/python-zstd#api |
| `compression-threads` | See: https://github.com/sergey-dryabzhinsky/python-zstd#api |
