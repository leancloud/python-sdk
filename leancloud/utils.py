# coding: utf-8

__author__ = 'asaka'

from collections import Mapping, Set, Sequence
from datetime import datetime

import leancloud
from leancloud import op


def encode(value, seen_objects=None, disallow_objects=False):
    seen_objects = seen_objects or []
    if isinstance(value, leancloud.Object):
        if disallow_objects:
            raise TypeError('Object is now allowed')
        if not seen_objects or value in seen_objects or not value._has_data:
            return value._to_pointer()
        # TODO

    if isinstance(value, leancloud.ACL):
        return value.dump()

    if isinstance(value, datetime):
        return {
            '__type': 'Date',
            'iso': value.isoformat()
        }

    if isinstance(value, leancloud.GeoPoint):
        return value.dump()

    if isinstance(value, (tuple, list)):
        return [encode(x, seen_objects, disallow_objects) for x in value]

    # TODO: regexp

    if isinstance(value, leancloud.Relation):
        return value.dump()

    if isinstance(value, op.BaseOp):
        return value.dump()

    # TODO: File

    if isinstance(value, dict):
        return {k: encode(v, seen_objects, disallow_objects) for k, v in value.iteritems()}

    return value


def decode(key, value):
    if not isinstance(value, dict):
        return value
    if isinstance(value, (tuple, list)):
        return [decode(x) for x in value]
    # TODO

    if isinstance(value, leancloud.Object):
        return value

    # TODO: File

    if isinstance(value, op.BaseOp):
        return value


iteritems = lambda mapping: getattr(mapping, 'iteritems', mapping.items)()
string_types = (str, unicode) if str is bytes else (str, bytes)


def objwalk(obj, path=(), memo=None):
    if memo is None:
        memo = set()
    iterator = None
    if isinstance(obj, Mapping):
        iterator = iteritems
    elif isinstance(obj, (Sequence, Set)) and not isinstance(obj, string_types):
        iterator = enumerate
    if iterator:
        if id(obj) not in memo:
            memo.add(id(obj))
            for path_component, value in iterator(obj):
                for result in objwalk(value, path + (path_component,), memo):
                    yield result
            memo.remove(id(obj))
    else:
        yield path, obj
