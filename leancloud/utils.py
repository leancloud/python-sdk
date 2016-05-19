# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import copy
import json
import gzip
import hashlib
import hmac
from datetime import datetime

import arrow
import iso8601
from werkzeug import LocalProxy
from dateutil import tz

import leancloud
from leancloud import operation
from leancloud._compat import BytesIO
from leancloud._compat import iteritems
from leancloud._compat import to_bytes

__author__ = 'asaka <lan@leancloud.rocks>'


def get_dumpable_types():
    return (
        leancloud.ACL,
        leancloud.File,
        leancloud.GeoPoint,
        leancloud.Relation,
        operation.BaseOp,
    )


def encode(value, disallow_objects=False):
    if isinstance(value, LocalProxy):
        value = value._get_current_object()

    if isinstance(value, datetime):
        tzinfo = value.tzinfo
        if tzinfo is None:
            tzinfo = tz.tzlocal()
        return {
            '__type': 'Date',
            'iso': arrow.get(value, tzinfo).to('utc').format('YYYY-MM-DDTHH:mm:ss.SSS') + 'Z',
        }

    if isinstance(value, leancloud.Object):
        if disallow_objects:
            raise ValueError('leancloud.Object not allowed')
        return value._to_pointer()

    if isinstance(value, leancloud.File):
        if not value.url and not value.id:
            raise ValueError('Tried to save an object containing an unsaved file.')
        return {
            '__type': 'File',
            'id': value.id,
            'name': value.name,
            'url': value.url,
        }

    if isinstance(value, get_dumpable_types()):
        return value.dump()

    if isinstance(value, (tuple, list)):
        return [encode(x, disallow_objects) for x in value]

    if isinstance(value, dict):
        return dict([(k, encode(v, disallow_objects)) for k, v in iteritems(value)])

    return value


def decode(key, value):
    if isinstance(value, get_dumpable_types()):
        return value

    if isinstance(value, (tuple, list)):
        return [decode(key, x) for x in value]

    if not isinstance(value, dict):
        return value

    if '__type' not in value:
        return dict([(k, decode(k, v)) for k, v in iteritems(value)])

    _type = value['__type']

    if _type == 'Pointer':
        value = copy.deepcopy(value)
        class_name = value['className']
        pointer = leancloud.Object.create(class_name)
        if 'createdAt' in value:
            value.pop('__type')
            value.pop('className')
            pointer._finish_fetch(value, True)
        else:
            pointer._finish_fetch({'objectId': value['objectId']}, False)
        return pointer

    if _type == 'Object':
        value = copy.deepcopy(value)
        class_name = value['className']
        value.pop('__type')
        value.pop('className')
        obj = leancloud.Object.create(class_name)
        obj._finish_fetch(value, True)
        return obj

    if _type == 'Date':
        return arrow.get(iso8601.parse_date(value['iso'])).to('local').datetime

    if _type == 'GeoPoint':
        return leancloud.GeoPoint(latitude=value['latitude'], longitude=value['longitude'])

    if key == 'ACL':
        if isinstance(value, leancloud.ACL):
            return value
        return leancloud.ACL(value)

    if _type == 'Relation':
        relation = leancloud.Relation(None, key)
        relation.target_class_name = value['className']
        return relation

    if _type == 'File':
        f = leancloud.File(value['name'])
        meta_data = value.get('metaData')
        if meta_data:
            f._metadata = meta_data
        f._url = value['url']
        f.id = value['objectId']
        return f


def traverse_object(obj, callback, seen=None):
    seen = seen or set()

    if isinstance(obj, leancloud.Object):
        if obj in seen:
            return
        seen.add(obj)
        traverse_object(obj._attributes, callback, seen)
        return callback(obj)

    if isinstance(obj, (leancloud.Relation, leancloud.File)):
        return callback(obj)

    if isinstance(obj, (list, tuple)):
        for idx, child in enumerate(obj):
            new_child = traverse_object(child, callback, seen)
            if new_child:
                obj[idx] = new_child
        return callback(obj)

    if isinstance(obj, dict):
        for key, child in iteritems(obj):
            new_child = traverse_object(child, callback, seen)
            if new_child:
                obj[key] = new_child
        return callback(obj)

    return callback(obj)


def sign_disable_hook(hook_name, master_key, timestamp):
    sign = hmac.new(to_bytes(master_key),
                    to_bytes('{0}:{1}'.format(hook_name, timestamp)),
                    hashlib.sha1).hexdigest()
    return '{0},{1}'.format(timestamp, sign)
