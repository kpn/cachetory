"""
Re-imports of the compressors.

Compressors are basically serializers from `bytes` to `bytes`
that are grouped for convenience.
"""

from contextlib import suppress

from .zlib import ZlibCompressor  # noqa

with suppress(ImportError):
    # only available with `zstd` feature
    from .zstd import ZstdCompressor  # noqa
