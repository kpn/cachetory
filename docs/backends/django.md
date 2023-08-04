# Django

Adapter for the Django cache framework: allows using a pre-configured Django cache for Cachetory's `Cache`.

!!! Tip
    Django backend allows using Cachetory with an existing configured Django cache.
    That may be useful for:

    - migrating from Django cache to Cachetory
    - using Cachetory's [`@cached`][decorators] with Django

## Supported URLs

- `django://<cache-name>`

---

::: cachetory.backends.sync.DjangoBackend
    options:
      heading_level: 2

---

::: cachetory.backends.async_.DjangoBackend
    options:
      heading_level: 2
