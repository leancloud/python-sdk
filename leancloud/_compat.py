# -*- coding: utf-8 -*-
"""
    flask._compat
    ~~~~~~~~~~~~~

    Some py2/py3 compatibility support based on a stripped down
    version of six so we don't have to depend on a specific version
    of it.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import

import sys
import types
import io


# Check the python version.
_version = sys.version_info.major
PY2 = _version == 2
PY3 = _version == 3


_identity = lambda x: x


if PY2:
    text_type = unicode
    class_types = (type, types.ClassType)
    string_types = (str, unicode)
    integer_types = (int, long)
    range_type = xrange
    file_type = file
    buffer_type = buffer  # python 2.6 don't have memoryview.

    iterkeys = lambda d: d.iterkeys()
    itervalues = lambda d: d.itervalues()
    iteritems = lambda d: d.iteritems()

    from StringIO import StringIO
    BytesIO = StringIO

    exec('def reraise(tp, value, tb=None):\n raise tp, value, tb')

    def implements_to_string(cls):
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda x: x.__unicode__().encode('utf-8')
        return cls

    def to_bytes(x, charset=sys.getdefaultencoding(), errors='strict'):
        if x is None:
            return None
        if isinstance(x, (bytes, bytearray, buffer)):
            return bytes(x)
        if isinstance(x, unicode):
            return x.encode(charset, errors)
        raise TypeError('Expected bytes')

    def to_native(x, charset=sys.getdefaultencoding(), errors='strict'):
        if x is None or isinstance(x, str):
            return x
        return x.encode(charset, errors)
elif PY3:
    text_type = str
    class_types = (type,)
    string_types = (str,)
    integer_types = (int,)
    range_type = range
    file_type = io.IOBase
    buffer_type = memoryview

    iterkeys = lambda d: iter(d.keys())
    itervalues = lambda d: iter(d.values())
    iteritems = lambda d: iter(d.items())

    from io import StringIO, BytesIO

    def reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

    implements_to_string = _identity

    def to_bytes(x, charset=sys.getdefaultencoding(), errors='strict'):
        if x is None:
            return None
        if isinstance(x, (bytes, bytearray, memoryview)):
            return bytes(x)
        if isinstance(x, str):
            return x.encode(charset, errors)
        raise TypeError('Expected bytes')

    def to_native(x, charset=sys.getdefaultencoding(), errors='strict'):
        if x is None or isinstance(x, str):
            return x
        return x.decode(charset, errors)



def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a
    # dummy metaclass for one level of class instantiation that replaces
    # itself with the actual metaclass.
    class metaclass(type):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})