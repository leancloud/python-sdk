# coding: utf-8

import copy
import json
import gzip
from datetime import datetime
from cStringIO import StringIO

import arrow
import iso8601
from dateutil import tz

import leancloud
from leancloud import operation


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
        return dict([(k, encode(v, disallow_objects)) for k, v in value.iteritems()])

    return value


# def encode(value, seen_objects=None, disallow_objects=False):
#     seen_objects = seen_objects or []
#     if isinstance(value, leancloud.Object):
#         if disallow_objects:
#             raise TypeError('Object is now allowed')
#         if (not seen_objects) or (value in seen_objects) or (not value._has_data):
#             return value._to_pointer()
#         if not value.is_dirty():
#             seen_objects.append(value)
#             return encode(value._dump(seen_objects=seen_objects), seen_objects, disallow_objects)
#
#     if isinstance(value, leancloud.ACL):
#         return value.dump()
#
#     if isinstance(value, datetime):
#         return {
#             '__type': 'Date',
#             'iso': value.isoformat()
#         }
#
#     if isinstance(value, leancloud.GeoPoint):
#         return value.dump()
#
#     if isinstance(value, (tuple, list)):
#         return [encode(x, seen_objects, disallow_objects) for x in value]
#
#     # TODO: regexp
#
#     if isinstance(value, leancloud.Relation):
#         return value.dump()
#
#     if isinstance(value, op.BaseOp):
#         return value.dump()
#
#     if isinstance(value, leancloud.File):
#         if (value.url is None) and (value.id is None):
#             raise ValueError('tried to save an unsaved file')
#         return {
#             '__type': 'File',
#             'id': value.id,
#             'name': value.name,
#             'url': value.url,
#         }
#
#     if isinstance(value, dict):
#         return {k: encode(v, seen_objects, disallow_objects) for k, v in value.iteritems()}
#
#     return value


def decode(key, value):
    if isinstance(value, get_dumpable_types()):
        return value

    if isinstance(value, (tuple, list)):
        return [decode(key, x) for x in value]

    if not isinstance(value, dict):
        return value

    if '__type' not in value:
        return dict([(k, decode(k, v)) for k, v in value.iteritems()])

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
        value.pop('class_name')
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
    # print obj, '>',

    if isinstance(obj, leancloud.Object):
        # print 'is Object'
        if obj in seen:
            return
        seen.add(obj)
        traverse_object(obj.attributes, callback, seen)
        return callback(obj)

    if isinstance(obj, (leancloud.Relation, leancloud.File)):
        # print 'is Relation or File'
        return callback(obj)

    if isinstance(obj, (list, tuple)):
        # print 'is list or tuple'
        for idx, child in enumerate(obj):
            new_child = traverse_object(child, callback, seen)
            if new_child:
                obj[idx] = new_child
        return callback(obj)

    if isinstance(obj, dict):
        # print 'is dict'
        for key, child in obj.iteritems():
            new_child = traverse_object(child, callback, seen)
            if new_child:
                obj[key] = new_child
        return callback(obj)

    # print 'is other'

    return callback(obj)


def response_to_json(response):
    """
    hack for requests in python 2.6
    """

    content = response.content
    # hack for requests in python 2.6
    if 'application/json' in response.headers['Content-Type']:
        if content[:2] == '\x1f\x8b':  # gzip file magic header
            f = StringIO(content)
            g = gzip.GzipFile(fileobj=f)
            content = g.read()
            g.close()
            f.close()
    return json.loads(content)
