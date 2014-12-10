# coding: utf-8

import copy

from leancloud import utils
from leancloud import rest
from leancloud.fields import AnyField
from leancloud import op


__author__ = 'asaka <lan@leancloud.rocks>'


class ObjectMeta(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(ObjectMeta, cls).__new__

        if name == 'User':
            name = '_User'

        attrs['_class_name'] = name
        return super_new(cls, name, bases, attrs)


class Object(object):

    __metaclass__ = ObjectMeta

    def __init__(self, attributes=None):
        if not attributes:
            attributes = {}

        # TODO: get defaults

        self.id = None

        self._server_data = {}
        self._op_set_queue = []
        self.attributes = {}

        # self._hashed_object = {}
        # self._escaped_attributes = {}
        # self.cid = ''  # TODO
        # self.changed = {}
        # self._silent = {}
        # self._pending = {}

        # self._fetch_when_save = False

    @classmethod
    def extend(cls, name):
        return type(name, (cls,), {})

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
            obj[k] = utils.encode(v, seen_objects)

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

    def destroy(self):
        if not self.id:
            return False
        result = rest.delete('/classes/{}/{}'.format(self._class_name, self.id))
        # print result
        # TODO: check the result
        return True

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
        if hasattr(self, '_refreshing_cache'):
            return
        setattr(self, '_refreshing_cache', True)
        for k, v in self.attributes.iteritems():
            if isinstance(v, Object):
                v._refresh_cache()
            elif isinstance(v, dict):
                if self._reset_cache_for_key(k):
                    self.set(k, op.Set(v), silent=True)
        delattr(self, '_refreshing_cache')

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

    def _validate(self, attrs):
        # TODO
        return True

    def set(self, key, value, unset=False, silent=True):
        if unset:
            attrs = {key: op.Unset()}
        else:
            attrs = {key: utils.decode(key, value)}

        data_to_validate = copy.deepcopy(attrs)
        for k, v in data_to_validate.iteritems():
            if isinstance(v, op.BaseOp):
                data_to_validate[key] = v._estimate(self.attributes[k], self, k)
                if data_to_validate[key] == op._UNSET:
                    del data_to_validate[key]

        if not self._validate(attrs):
            return False

        self._merge_magic_field(attrs)

        for k, v in attrs.iteritems():
            # TODO: Relation

            if not isinstance(v, op.BaseOp):
                v = op.Set(v)

            is_real_change = True
            if isinstance(v, op.Set) and self.attributes[k] == v:  # TODO: equal
                is_real_change = False

    def unset(self, attr):
        return self.set(attr, None, unset=True)

    def increment(self, attr, amount=1):
        return self.set(attr, op.Increment(amount))

    def add(self, attr, item):
        return self.set(attr, op.Add([item]))

    def add_unique(self, attr, item):
        return self.set(attr, op.AddUnique([item]))

    def remove(self, attr, item):
        return self.set(attr, op.Remove([item]))

    def op(self, attr):
        return self._op_set_queue[attr][-1]

    def clear(self):
        pass

    def fetch(self):
        response = rest.get('/classes/{}/{}'.format(self._class_name, self.id))
        result = self.parse(response)
        self._finish_fetch(result)

    def destroy(self):
        if not self.id:  # TODO
            return False
        rest.delete('/classes/{}/{}'.format(self._class_name, self.id))
        return True

    def parse(self, response):
        print response

    def clone(self):
        pass

    def is_new(self):
        return True if self.id else False

    def change(self):
        pass

    def _finish_fetch(self, server_data, has_data):
        self._op_set_queue = [{}]

        self._merge_magic_field(server_data)

        for key, value in server_data.iteritems():
            self._server_data[key] = utils.decode(key, value)

        self._rebuild_all_estimated_data()  # TODO

        self._refresh_cache()

        self._op_set_queue = [{}]

        self._has_data = has_data

    def _rebuild_estimated_data_for_key(self, key):
        pass

    def _rebuild_all_estimated_data(self):
        # TODO
        previous_attributes = copy.deepcopy(self.attributes)
        self.attributes = copy.deepcopy(self._server_data)

        for op_set in self._op_set_queue:
            # apply local changes
            self._apply_op_set(op_set, self.attributes)
            for key in op_set.iterkeys():
                self._reset_cache_for_key(key)

        # TODO: triger change event

    def _apply_op_set(self, op_set, target):
        for key, change in op_set.iteritems():
            target[key] = change._estimate(target[key], self, key)
            if target[key] == op._UNSET:
                del target[key]