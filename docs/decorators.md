# Decorators

`#!python @cached` performs [memoization](https://en.wikipedia.org/wiki/Memoization) of a wrapped function:

```python
from cachetory.caches.sync import Cache
from cachetory.decorators.sync import cached

cache = Cache[int, ...](backend=..., serializer=...)


@cached(cache)
def expensive_function(x: int) -> int:
    return 42 * x
```

## Key functions

There are a few `make_key` functions provided by default:

::: cachetory.decorators.shared.make_default_key
    options:
      heading_level: 3

::: cachetory.decorators.shared.make_default_hashed_key
    options:
      heading_level: 3

## Purging cache

Specific cached value can be deleted using the added `#!python purge()` function, which accepts the same arguments as the original wrapped callable:

```python
expensive_function(100500)
expensive_function.purge(100500)  # purge cached value for this argument
```

## Synchronous `@cached`

::: cachetory.decorators.sync.cached
    options:
      heading_level: 3
      show_root_heading: false

### Cached callable protocol

::: cachetory.decorators.sync._CachedCallable
    options:
      heading_level: 4
      show_root_heading: false

## Asynchronous `@cached`

::: cachetory.decorators.async_.cached
    options:
      heading_level: 3
      show_root_heading: false

### Cached callable protocol

::: cachetory.decorators.async_._CachedCallable
    options:
      heading_level: 4
      show_root_heading: false
