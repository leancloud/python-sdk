# coding: utf-8

import copy

from leancloud import rest
from leancloud.fields import AnyField
from leancloud import op


__author__ = 'asaka <lan@leancloud.rocks>'


class InvalidAVObject(Exception):
    pass


class ObjectMeta(type):
    """Metaclass for build AVObject
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(ObjectMeta, cls).__new__

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
            from leancloud import Query
            return Query(*args, **kwargs)
        if 'objects' in attrs:
            raise RuntimeError('objects field can\'t override in sub class')
        attrs['objects'] = query

        return super_new(cls, name, bases, attrs)


class Object(object):
    __metaclass__ = ObjectMeta

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


class AVObject(object):
    def __init__(self, attributes=None):
        if not attributes:
            attributes = {}

        # TODO: get defaults

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

        self._fetch_when_save = False

    def fetch_when_save(self, enable):
        self._fetch_when_save = enable

    def dump(self):
        obj = self._dump()
        obj.pop('__type')
        obj.pop('className')
        return obj

    def _dump(self, seen_objects=False):
        obj = copy.deepcopy(self.attributes)
        for k, v in obj:
            obj[k] = encode(v, seen_objects)

        for k, v in self._operations:
            obj[k] = v

        if hasattr(self, 'id'):
            obj['objectId'] = self.id

        if hasattr(self, 'createdAt'):
            # TODO: parse date
            obj['createdAt'] = self.createdAt

        if hasattr(self, 'updatedAt'):
            # TODO: parse date
            obj['updatedAt'] = self.updatedAt

        obj['__type'] = 'Object'
        obj['className'] = self.__class__.__name__
        return obj

    def save(self):
        pass
        self._refresh_cache()
        unsaved_children = []
        unsaved_files = []
        self._find_unsaved_children(self.attributes, unsaved_children, unsaved_files)
        if len(unsaved_children) + len(unsaved_files) > 0:
            self._deep_save(self.attributes)

        self._start_save()
        self._saving = getattr(self, '_saving', 0) + 1

    def _refresh_cache(self):
        # TODO
        if hasattr(self, '_refreshing_cache'):
            return
        self._refreshing_cache = True
        for k, v in self.attributes:
            if isinstance(v, AVObject):
                v._refresh_cache()
            elif isinstance(v, dict):
                if self._refresh_cache_for_key(k):
                    self.set(k, op.Set(v), silent=True)
        del self._refreshing_cache

    def dirty(self, attr=None):
        self._refresh_cache()
        current_changes = self._op_set_queue[-1]
        if attr is not None:
            #TODO
            pass

        if not hasattr(self, 'id'):
            return True

        # TODO: handle current changes

        return False

    def _to_pointer(self):
        return {
            '__type': 'Pointer',
            'className': self.__class__.__name__,
            'objectId': self.id,
        }

    def get(self, attr):
        return self.attributes[attr]

    def relation(self, attr):
        # TODO
        pass

    def has(self, attr):
        return attr in self.attributes

    def _merge_magic_field(self, attrs):
        pass

    def _start_save(self):
        self._op_set_queue.append({})

    def _cancel_save(self):
        failed_changes = self._op_set_queue.pop(0)
        next_changes = self._op_set_queue[0]
        for key, op in failed_changes.iteritems():
            op1 = failed_changes[key]
            op2 = next_changes[key]
            # TODO

    def set(self, key, value):
        pass

    def unset(self, attr):
        pass

    def increment(self, attr, amount=1):
        return self.set(attr, op.Increment(amount))

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
