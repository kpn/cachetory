# Redis

!!! warning ""

    This backend requires the `redis` extra.

!!! tip "Atomicity"

    All the operations are **atomic** in both sync and async caches, including `get_many()` and `set_many()`.

!!! tip "Performance"

    Consider explicitly adding [`hiredis`](https://github.com/redis/hiredis) to your dependencies for better performance.

## Supported URL schema's

- `redis://`
- `rediss://`
- `redis+unix://`

!!! note "URL handling"

    The URL is forwarded to the underlying client, which means one can use whatever options the client provides. The only special case is `redis+unix`, for which the leading `redis+` is first stripped and the rest is forwarded to the client.

---

::: cachetory.backends.sync.RedisBackend
    options:
      heading_level: 2

---

::: cachetory.backends.async_.RedisBackend
    options:
      heading_level: 2
