"""
Compressors are basically serializers from `bytes` to `bytes`
that are grouped for convenience.
"""

from .zlib import ZlibCompressor  # noqa

try:
    from .zstd import ZstdCompressor  # noqa
except ImportError:
    pass  # only available with `zstd` feature
