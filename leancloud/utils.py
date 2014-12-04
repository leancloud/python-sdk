# coding: utf-8

__author__ = 'asaka'

from datetime import datetime

import leancloud
from leancloud import op


def encode(value, seen_objects=False, disallow_objects=False):
    if type(value) == leancloud.Object:
        if disallow_objects:
            raise TypeError('Object is now allowed')
        if not seen_objects or value in seen_objects or not value._has_data:
            return value._to_pointer()
        # TODO

    # TODO: ACL

    if isinstance(value, datetime):
        return {
            '__type': 'Date',
            'iso': value.isoformat()
        }

    # TODO: GEOPoint

    if isinstance(value, (tuple, list)):
        return [encode(x, seen_objects, disallow_objects) for x in value]

    # TODO: regexp

    if isinstance(value, leancloud.Relation):
        return value.dump()

    if isinstance(value, op.BaseOperation):
        return value.dump()

    # TODO: File

    if isinstance(value, dict):
        return {k: encode(v, seen_objects, disallow_objects) for k, v in value.iteritems()}

    return value