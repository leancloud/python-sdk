# coding: utf-8

from leancloud import rest
from leancloud.fields import AnyField


__author__ = 'asaka <lan@leancloud.rocks>'


class InvalidAVObject(Exception):
    pass


class AVObjectMeta(type):
    """Metaclass for build AVObject
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(AVObjectMeta, cls).__new__

        attrs['_class_name'] = name

        if '_fields' in attrs:
            if not isinstance(attrs['_fields'], dict):
                raise InvalidAVObject
        else:
            attrs['_fields'] = {}

        for key, attr in attrs.iteritems():
            if isinstance(attr, AnyField):
                attrs['_fields'][key] = attr

        if 'meta' in attrs:
            attrs['_meta'] = attrs.pop('meta')

        def query(*args, **kwargs):
            from leancloud import AVQuery
            return AVQuery(*args, **kwargs)
        if 'objects' in attrs:
            raise RuntimeError('objects field can\'t override in sub class')
        attrs['objects'] = query

        return super_new(cls, name, bases, attrs)


class AVObject(object):
    __metaclass__ = AVObjectMeta

    def __init__(self, **kwargs):
        self.id = None
        self.created_at = None
        self.updated_at = None

        for k, v in kwargs.iteritems():
            self.set(k, v)

    def __repr__(self):
        return '<{} id: {}>'.format(self._class_name, self.id)

    @classmethod
    def extend(cls, name):
        return type(name, (cls,), {})

    def save(self):
        data = {k: getattr(self, k, None) for k in self._fields.keys()}
        result = rest.post('/classes/%s' % self._class_name, data)
        self.set('id', result['objectId'])

    def delete(self):
        if not self.id:
            return False
        result = rest.delete('/classes/{}/{}'.format(self._class_name, self.id))
        # print result
        # TODO: check the result
        return True

    def set(self, key, value):
        if key not in self._fields:
            self._fields[key] = AnyField
        setattr(self, key, value)

    def get(self, key):
        if key not in self._fields:
            raise AttributeError(key)
        return getattr(self, key)


'''
class AVObject(object):
    def __init__(self, attributes):
        self.id = None

        self._server_data = {}
        self._op_set_queue = []
        self.attributes = {}

        self._hashed_object = {}
        self._escaped_attributes = {}
        self.cid = ''  # TODO
        self.changed = {}
        self._silent = {}
        self._pending = {}

    def get(self, attr):
        return self.attributes[attr]

    def has(self, attr):
        return attr in self.attributes

    def set(self, key, value):
        pass

    def unset(self, attr):
        pass

    def increment(self, attr, amount):
        pass

    def add(self, attr, item):
        pass

    def add_unique(self, attr, item):
        pass

    def remove(self, attr, item):
        pass

    def op(self, attr):
        pass

    def clean(self):
        pass

    def fetch(self):
        pass

    def save(self):
        pass

    def destroy(self):
        if not self.id:  # TODO
            return False
        rest.delete('/classes/{}/{}'.format(self._class_name, self.id))
        return True

    def parse(self, response, status):
        pass

    def clone(self):
        pass

    def is_new(self):
        return True if self.id else False

    def change(self):
        pass
'''
