# coding: utf-8

from leancloud.fields import AnyField


__author__ = 'asaka <lan@leancloud.rocks>'


class InvalidAVObject(Exception):
    pass


class AVObjectMeta(type):
    """Metaclass for build AVObject
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(AVObjectMeta, cls).__new__

        if '_fields' in attrs:
            if not isinstance(attrs['_fields'], dict):
                raise InvalidAVObject
        else:
            attrs['_fields'] = {}

        for name, attr in attrs.iteritems():
            if isinstance(attr, AnyField):
                attrs['_fields'][name] = attr

        if 'meta' in attrs:
            attrs['_meta'] = attrs.pop('meta')

        return super_new(cls, name, bases, attrs)


class AVObject(object):
    __metaclass__ = AVObjectMeta

    def __init__(self):
        pass

    @classmethod
    def extend(cls, name):
        return type(name, (cls,), {})

    def save(self):
        pass

    def set(self, key, value):
        if key not in self._fields:
            self._fields[key] = AnyField
        self.key = value

    def get(self, key):
        if key not in self._fileds:
            raise AttributeError(key)
