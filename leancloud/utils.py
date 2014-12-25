# coding: utf-8

__author__ = 'asaka'

import copy
from datetime import datetime

import iso8601

import leancloud
from leancloud import op


def encode(value, seen_objects=None, disallow_objects=False):
    seen_objects = seen_objects or []
    if isinstance(value, leancloud.Object):
        if disallow_objects:
            raise TypeError('Object is now allowed')
        if (not seen_objects) or (value in seen_objects) or (not value._has_data):
            return value._to_pointer()
        if not value.dirty:
            seen_objects.append(value)
            return encode(value._dump(seen_objects=seen_objects), seen_objects, disallow_objects)

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

    if isinstance(value, leancloud.File):
        if (value.url is None) and (value.id is None):
            raise ValueError('tried to save an unsaved file')
        return {
            '__type': 'File',
            'id': value.id,
            'name': value.name,
            'url': value.url,
        }

    if isinstance(value, dict):
        return {k: encode(v, seen_objects, disallow_objects) for k, v in value.iteritems()}

    return value


def decode(key, value):
    if isinstance(value, (leancloud.Object, leancloud.File, leancloud.op.BaseOp)):
        return value

    if isinstance(value, (tuple, list)):
        return [decode(x, idx) for x, idx in enumerate(value)]

    if not isinstance(value, dict):
        return value

    if '__type' not in value:
        return {k: v for k,v in value.iteritems()}

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
        return iso8601.parse_date(value['iso'])

    if _type == 'GeoPoint':
        return leancloud.GeoPoint(latitude=value['latitude'], longitude=value['longitude'])

    if _type == 'ACL':
        return leancloud.ACL(value)  # TODO

    # TODO: Relation

    if _type == 'File':
        f = leancloud.File(value['name'])
        meta_data = value.get('metaData')
        if meta_data:
            f._metadata = meta_data
        f._url = value['url']
        f.id = value['objectId']
        return f

    return {k: decode(k, v) for k, v in value.iteritems()}


def walk_object(obj, callback, seen=None):
    seen = seen or set()

    if isinstance(obj, leancloud.Object):
        if obj in seen:
            return
        seen.add(obj)
        walk_object(obj.attributes, callback, seen)
        return callback(obj)

    if isinstance(obj, (leancloud.Relation, leancloud.File)):
        return callback(obj)

    if isinstance(obj, (dict, tuple)):
        for child, idx in enumerate(obj):
            new_child = walk_object(child, callback, seen)
            if new_child:
                obj[idx] = new_child
        return callback(obj)

    if isinstance(obj, dict):
        for key, child in obj.iteritems():
            new_child = walk_object(child, callback, seen)
            if new_child:
                obj[key] = new_child
        return callback(obj)

    return callback(obj)
