import ctypes

from . import types


__all__ = ()


clause = ctypes.CFUNCTYPE(
    types.ires,
    types.enum,
    types.void,
    types.void
)


text = ctypes.CFUNCTYPE(
    types.ires,
    types.enum,
    types.char,
    types.size,
    types.void
)


debug_log = ctypes.CFUNCTYPE(
    types.vres,
    types.char,
    types.void
)


syntax = ctypes.CFUNCTYPE(
    types.vres,
    types.void
)
