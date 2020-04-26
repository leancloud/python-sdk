# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy
import functools
from datetime import datetime
from datetime import timedelta

import arrow
import six
import iso8601
from werkzeug.local import LocalProxy
import dateutil.tz as tz

import leancloud
from leancloud import operation

__author__ = "asaka <lan@leancloud.rocks>"


def get_dumpable_types():
    return (
        leancloud.ACL,
        leancloud.File,
        leancloud.GeoPoint,
        leancloud.Relation,
        operation.BaseOp,
    )


def encode(value, disallow_objects=False, dump_objects=False):
    if isinstance(value, LocalProxy):
        value = value._get_current_object()

    if isinstance(value, datetime):
        tzinfo = value.tzinfo
        if tzinfo is None:
            tzinfo = tz.tzlocal()
        return {
            "__type": "Date",
            "iso": arrow.get(value, tzinfo).to("utc").format("YYYY-MM-DDTHH:mm:ss.SSS")
            + "Z",
        }

    if isinstance(value, leancloud.Object):
        if disallow_objects:
            raise ValueError("leancloud.Object not allowed")
        if dump_objects:
            return value._dump()
        return value._to_pointer()

    if isinstance(value, leancloud.File):
        if not value.url and not value.id:
            raise ValueError("Tried to save an object containing an unsaved file.")
        return {
            "__type": "File",
            "id": value.id,
            "name": value.name,
            "url": value.url,
        }

    if isinstance(value, get_dumpable_types()):
        return value.dump()

    if isinstance(value, (tuple, list)):
        return [encode(x, disallow_objects, dump_objects) for x in value]

    if isinstance(value, dict):
        return dict(
            [
                (k, encode(v, disallow_objects, dump_objects))
                for k, v in six.iteritems(value)
            ]
        )

    return value


def decode(key, value):
    if isinstance(value, get_dumpable_types()):
        return value

    if isinstance(value, (tuple, list)):
        return [decode(key, x) for x in value]

    if not isinstance(value, dict):
        return value

    if key == "ACL":
        if isinstance(value, leancloud.ACL):
            return value
        return leancloud.ACL(value)

    if "__type" not in value:
        return dict([(k, decode(k, v)) for k, v in six.iteritems(value)])

    _type = value["__type"]

    if _type == "Pointer":
        value = copy.deepcopy(value)
        class_name = value["className"]
        pointer = leancloud.Object.create(class_name)
        if "createdAt" in value:
            value.pop("__type")
            value.pop("className")
            pointer._update_data(value)
        else:
            pointer._update_data({"objectId": value["objectId"]})
        return pointer

    if _type == "Object":
        value = copy.deepcopy(value)
        class_name = value["className"]
        value.pop("__type")
        value.pop("className")
        obj = leancloud.Object.create(class_name)
        obj._update_data(value)
        return obj

    if _type == "Date":
        return arrow.get(iso8601.parse_date(value["iso"])).to("local").datetime

    if _type == "GeoPoint":
        return leancloud.GeoPoint(
            latitude=value["latitude"], longitude=value["longitude"]
        )

    if _type == "Relation":
        relation = leancloud.Relation(None, key)
        relation.target_class_name = value["className"]
        return relation

    if _type == "File":
        f = leancloud.File(value["name"])
        meta_data = value.get("metaData")
        if meta_data:
            f._metadata = meta_data
        f._url = value["url"]
        f.id = value["objectId"]
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
        for key, child in six.iteritems(obj):
            new_child = traverse_object(child, callback, seen)
            if new_child:
                obj[key] = new_child
        return callback(obj)

    return callback(obj)


class throttle(object):
    def __init__(self, seconds=0, minutes=0, hours=0):
        self.throttle_period = timedelta(seconds=seconds, minutes=minutes, hours=hours)
        self.time_of_last_call = datetime.min

    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            now = datetime.now()
            time_since_last_call = now - self.time_of_last_call
            if time_since_last_call > self.throttle_period:
                self.time_of_last_call = now
                return fn(*args, **kwargs)

        return wrapper


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)
