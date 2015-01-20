# coding: utf-8
import copy

import leancloud
from leancloud import utils
from leancloud import client
from leancloud import operation

__author__ = 'asaka <lan@leancloud.rocks>'


object_class_map = {}


class ObjectMeta(type):
    def __new__(cls, name, bases, attrs):
        if name == 'User':
            name = '_User'

        cached_class = object_class_map.get(name)
        if cached_class:
            return cached_class

        super_new = super(ObjectMeta, cls).__new__
        attrs['_class_name'] = name
        object_class = super_new(cls, name, bases, attrs)
        object_class_map[name] = object_class
        return object_class


class Object(object):
    __metaclass__ = ObjectMeta

    def __init__(self, object_id=None, is_pointer=False):
        self._server_data = {}
        self._op_set = {}
        self._attrs = {}
        self._data_availability = {}
        self._class_name = self._class_name    # for IDE
        self._id = None
        self._created_at = None
        self._updated_at = None
        if object_id and is_pointer:
            self._id = object_id
            self._has_been_fetched = False
        else:
            self._has_been_fetched = True

    def get(self, key):
        if not self._is_data_available(key):
            raise ValueError('leancloud.Object has no data for this key, call fetch() to get the data')
        return self._attrs.get(key, None)

    def has(self, key):
        return key in self._attrs

    def increment(self, key, value=1):
        self._perform_op(key, operation.Increment(value))

    def add(self, key, value):
        self._perform_op(key, operation.Add(value))

    def add_unique(self, key, value):
        self._perform_op(key, operation.AddUnique(value))

    def unset(self, key):
        self._perform_op(key, operation.Unset())

    def is_key_dirty(self, key):
        return key in self._op_set

    def is_data_available(self):
        return self._has_been_fetched

    def _is_data_available(self, key):
        return (self.is_data_available()) or (key in self._data_availability)

    def _is_dirty(self, consider_children):
        if self._op_set:
            return True
        if self.id is None:
            return True
        if consider_children and self.has_dirty_children():
            return True
        return False

    def is_dirty(self):
        return self._is_dirty(True)

    def has_dirty_children(self):
        result = False
        # TODO
        return result

    def set(self, key, value):
        self._perform_op(key, operation.Set(value))

    def remove(self, key, *values):
        self._perform_op(key, operation.Remove(values))

    def revert(self):
        self._op_set = {}
        self._rebuild_estimate_date()

    def clear(self):
        for key in self._attrs:
            self.delete(key)

    def _perform_op(self, key, op):
        old_value = self.attrs.get(key)
        new_value = op._apply(old_value, self, key)
        if new_value is operation._UNSET:
            self._attrs.pop(key, None)
        else:
            self._attrs[key] = new_value

        if key in self._op_set:
            old_op = self._op_set[key]
            new_op = op._merge(old_op)
            self._op_set[key] = new_op
        else:
            self._op_set[key] = op
        self._data_availability[key] = True

    @property
    def class_name(self):
        return self._class_name

    @property
    def id(self):
        return self._id

    @property
    def created_at(self):
        return self._created_at

    @property
    def updated_at(self):
        return self._updated_at

    @classmethod
    def extend(cls, name):
        return type(name, (cls,), {})

    @classmethod
    def create(cls, class_name, obect_id=None, is_pointer=False):
        if isinstance(class_name, basestring):
            class_type = cls.extend(class_name)
        elif issubclass(class_name, cls):
            class_type = class_name
        else:
            raise TypeError('first parameter must be a basestring or leancloud.Object sub class')
        return class_type(obect_id, is_pointer)

    def fetch(self):
        response = client.get('/classes/{}/{}'.format(self._class_name, self._id))
        self._merge_after_fetch(response.json())

    def _merge_after_fetch(self, result, complete_data=True):
        for key in result:
            self._op_set.pop(key, None)

        self._server_data = {}
        self._data_availability = {}
        self.merge_from_server(result, complete_data)
        self._rebuild_estimated_data()

    def _merge_after_fetch_with_selected_keys(self, result, selected_keys):
        self._merge_after_fetch(result, selected_keys)
        for key in selected_keys:
            self._data_availability[key] = True

    def _merge_from_server(self, data, complete_data=True):
        if self._has_been_fetched or complete_data:
            self._has_been_fetched = True
        else:
            self._has_been_fetched = False

        self._merge_magic_field(data)

        for key, value in data.iteritems():
            if key == '__type' and value == 'className':
                continue
            value = utils.decode(value)

            if isinstance(value, dict):
                if ('__type' in value) and (value['__type'] == 'Relation'):
                    class_name = value['className']
                    value = leancloud.Relation(self, key, class_name)  # TODO

                if key == 'ACL':
                    value = leancloud.ACL(value)  # TODO

            self._server_data[key] = value
            self._data_availability[key] = True

        if (not self._updated_at) and self._created_at:
            self._updated_at = copy.copy(self._created_at)

    def _merge_magic_field(self, data):
        if 'objectId' in data:
            self._id = data['objectId']
            del data['objectId']

        if 'createdAt' in data:
            self._created_at = data['createdAt']
            del data['createdAt']

        if 'updatedAt' in data:
            self._updated_at = data['updatedAt']
            del data['updatedAt']

        if 'ACL' in data:
            acl = leancloud.ACL(data)  # TODO
            self._server_data['ACL'] = acl
            del data['ACL']

    def _rebuild_estimated_data(self):
        self._attrs = {}
        for key, value in self._server_data.iteritems():
            self._attrs[key] = value
        self._apply_op(self._op_set, self._attrs)

    def _apply_op(self, op_set, target):
        for key, op in op_set.iteritems():
            old_value = target.get(key)
            new_value = op._apply(old_value, self, key)
            if new_value is operation._UNSET:
                target.pop(key, None)
                self._data_availability.pop(key, None)

    def destroy(self):
        if not self._id:
            return
        client.delete('/classes/{}/{}'.format(self.class_name, self.id))

    # def destroy_all(self):
    #     # TODO

    def dump(self):
        result = {}
        if self.id:
            result['objectId'] = self.id
        if self.created_at:
            result['createdAt'] = self.created_at
        if self.updated_at:
            result['updatedAt'] = self.updated_at

        for key, value in self._server_data:
            result[key] = value

        for key, value in self._attrs:
            result[key] = value
