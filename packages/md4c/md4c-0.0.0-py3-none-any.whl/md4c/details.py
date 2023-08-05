import ctypes

from . import types
from . import enums


__all__ = ('Attribute', 'Ul', 'Ol', 'Li', 'H', 'Code', 'Td', 'A', 'Img',
           'WikiLink')


class Attribute(ctypes.Structure):

    _fields_ = (
        ('text'          , types.char  ),
        ('size'          , types.size  ),
        ('substr_types'  , types.enum  ),
        ('substr_offsets', types.offset)
    )


class Ul(ctypes.Structure):

    _fields_ = (
        ('is_tight'   , ctypes.c_int),
        ('mark'       , types.char  )
    )


class Ol(ctypes.Structure):

    _fields_ = (
        ('start'         , ctypes.c_uint),
        ('is_tight'      , ctypes.c_int ),
        ('mark_delimiter', types.char   )
    )


class Li(ctypes.Structure):

    _fields_ = (
        ('is_task'         , ctypes.c_int),
        ('task_mark'       , types.char  ),
        ('task_mark_offset', types.offset)
    )


class H(ctypes.Structure):

    _fields_ = (
        ('level', ctypes.c_uint),
    )


class Code(ctypes.Structure):

    _fields_ = (
        ('info'      , Attribute ),
        ('lang'      , Attribute ),
        ('fence_char', types.char)
    )


class Td(ctypes.Structure):

    _fields_ = (
        ('align', types.enum),
    )


class A(ctypes.Structure):

    _fields_ = (
        ('href' , Attribute),
        ('title', Attribute)
    )


class Img(ctypes.Structure):

    _fields_ = (
        ('src'  , Attribute),
        ('title', Attribute)
    )


class WikiLink(ctypes.Structure):

    _fields_ = (
        ('target', Attribute),
    )
