# Getting started

## Instantiating a `Cache`

Both sync and async `Cache`s requires at least these parameters to work:

- `backend`: functions as a storage
- `serializer`: is responsible for converting actual values from and to something that a backend would be able to store

`#!python Cache` may be annotated with a value type like this `#!python Cache[ValueT, WireT]`, which provides type hints for the cache methods.

## Instantiating a backend

There are a few ways to instantiate a backend:

- By **directly instantiating** a backend class via its `__init__()`
- By instantiating a specific backend class **via its `from_url()` class method**. In that case the URL is forwarded to underlying client (if any)
- **By using `cachetory.[sync|async_].from_url()` function.** In that case specific backend class is chosen by the URL's scheme, and the URL is forwarded to its `#!python from_url()` class method. This is especially useful to configure an arbitrary backend from a single configuration option – instead of hard-coding a specific backend class.

### Examples

```python
import redis
import cachetory.backends.sync
import cachetory.backends.async_

backend = cachetory.backends.sync.from_url("memory://")
backend = cachetory.backends.async_.from_url("dummy://")
backend = cachetory.backends.sync.RedisBackend(redis.Redis(...))
backend = cachetory.backends.async_.from_url("redis://localhost:6379/1")
```

## Instantiating a serializer

Instantiating of a serializer is very much similar to that of a backend. To instantiate it by a URL use [`cachetory.serializers.from_url()`][cachetory.serializers.from_url] – unlike the back-end case there are no separate sync and async versions.

!!! tip "Scheme joining"

    `#!python cachetory.serializers.from_url()` supports scheme joining with `+`, as in `pickle+zlib://`. In that case multiple serializers are instantiated and applied sequentially (in the example a value would be serialized by `pickle` and the serialized value is then compressed by `zlib`). Deserialization order is, of course, the opposite.

### Examples

```python
import pickle

import cachetory.serializers

serializer = cachetory.serializers.from_url("pickle+zstd://")
serializer = cachetory.serializers.from_url(
    "pickle+zstd://?pickle-protocol=4&compression-level=3",
)
serializer = cachetory.serializers.from_url("null://")
serializer = cachetory.serializers.NoopSerializer()
serializer = cachetory.serializers.PickleSerializer(
    pickle_protocol=pickle.DEFAULT_PROTOCOL,
)
```

::: cachetory.serializers.from_url
    options:
      heading_level: 3
