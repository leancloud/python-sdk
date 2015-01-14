# coding: utf-8

import copy
import logging
from datetime import datetime

import iso8601

import leancloud
from leancloud import utils
from leancloud import rest
from leancloud import op


__author__ = 'asaka <lan@leancloud.rocks>'


logging.getLogger('iso8601.iso8601').disabled = True


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

    def __init__(self, **attributes):
        if not attributes:
            attributes = {}

        # TODO: get defaults

        self.id = None
        self._class_name = self._class_name  # for IDE

        self._server_data = {}
        self._op_set_queue = [{}]
        self.attributes = attributes

        # self._hashed_object = {}
        # self._escaped_attributes = {}
        # self.cid = ''  # TODO
        # self.changed = {}
        # self._silent = {}
        # self._pending = {}

        self._existed = False
        # self._fetch_when_save = False

    @classmethod
    def extend(cls, name):
        return type(name, (cls,), {})

    @classmethod
    def create(cls, class_name, **attributes):
        object_class = cls.extend(class_name)
        return object_class(**attributes)

    # def fetch_when_save(self, enable):
    #     self._fetch_when_save = enable

    def dump(self):
        obj = self._dump()
        obj.pop('__type')
        obj.pop('className')
        return obj

    def _dump(self, seen_objects=None):
        seen_objects = seen_objects or []
        obj = copy.deepcopy(self.attributes)
        for k, v in obj.iteritems():
            obj[k] = utils.encode(v, seen_objects)

        # TODO
        # for k, v in self._operations:
        #     obj[k] = v

        if self.id is not None:
            obj['objectId'] = self.id

        for key in ['createdAt', 'updatedAt']:
            value = getattr(self, key, None)
            if value is None:
                continue
            if isinstance(value, datetime):
                setattr(self, key, value.isoformat())

        obj['__type'] = 'Object'
        obj['className'] = self.__class__.__name__
        return obj

    def destroy(self):
        if not self.id:
            return False
        result = rest.delete('/classes/{}/{}'.format(self._class_name, self.id))

        content = result.json()
        if 'error' in content:
            raise leancloud.LeanCloudError(content['code'], content['error'])
        return True

    def save(self):
        # self._refresh_cache()

        unsaved_children = []
        unsaved_files = []

        self._find_unsaved_children(self.attributes, unsaved_children, unsaved_files)

        if len(unsaved_children) + len(unsaved_files) > 0:
            self._deep_save(self.attributes)

        self._start_save()

        data = self._dump_save()

        method = 'PUT' if self.id is not None else 'POST'

        if method == 'PUT':
            response = rest.put('/classes/{}/{}'.format(self._class_name, self.id), data)
        else:
            response = rest.post('/classes/{}'.format(self._class_name), data)

        self._finish_save(self.parse(response.json(), response.status_code))

    def _deep_save(self, exclude=None):
        # TODO: chunk
        unsaved_children = []
        unsaved_files = []
        self._find_unsaved_children(self.attributes, unsaved_children, unsaved_files)

        if exclude:
            unsaved_children = [x for x in unsaved_children if x != exclude]

        for f in unsaved_files:
            f.save()

        dumped_objs = []
        for obj in unsaved_children:
            obj._start_save()
            method = 'POST' if obj.id is None else 'PUT'
            path = '/{}/classes/{}'.format(rest.SERVER_VERSION, obj._class_name)
            body = obj._dump_save()
            dumped_obj = {
                'method': method,
                'path': path,
                'body': body,
            }
            dumped_objs.append(dumped_obj)

        response = rest.post('/batch', params={'requests': dumped_objs}).json()

        errors = []
        for idx, obj in enumerate(unsaved_children):
            content = response[idx]
            if not content.get('success'):
                errors.append(leancloud.LeanCloudError(content.get('code'), content.get('error')))
                obj._cancel_save()
            else:
                result = obj.parse(content['success'])
                obj._finish_save(result)

            if errors:
                # TODO: how to handle list of errors?
                pass


    @classmethod
    def _find_unsaved_children(cls, obj, children, files):

        def callback(o):
            if isinstance(o, Object):
                if o.is_dirty():
                    children.append(o)
                return

            if isinstance(o, leancloud.File):
                if o.url is None and o.id is None:
                    files.append(o)
                return

        utils.walk_object(obj, callback)

    def is_dirty(self, attr=None):
        # self._refresh_cache()
        current_changes = self._op_set_queue[-1]

        if attr is not None:
            return True if attr in current_changes else False

        if self.id is None:
            return True

        if current_changes:
            return True

        return False

    def _to_pointer(self):
        return {
            '__type': 'Pointer',
            'className': self.__class__.__name__,
            'objectId': self.id,
        }

    def _merge_magic_field(self, attrs):
        for key in ['id', 'objectId', 'createdAt', 'updatedAt']:
            if attrs.get(key) is None:
                continue
            if key == 'objectId':
                self.id = attrs[key]
            elif key == 'createdAt' or key == 'updatedAt':
                if not isinstance(attrs[key], datetime):
                    dt = iso8601.parse_date(attrs[key])
                else:
                    dt = attrs[key]
                if key == 'createdAt':
                    setattr(self, 'created_at', dt)
                elif key == 'updatedAt':
                    setattr(self, 'updated_at', dt)
            del attrs[key]

    def _start_save(self):
        self._op_set_queue.append({})

    def _cancel_save(self):
        failed_changes = self._op_set_queue.pop(0)
        next_changes = self._op_set_queue[0]
        for key, op in failed_changes.iteritems():
            op1 = failed_changes[key]
            op2 = next_changes[key]
            # TODO

    def validate(self, attrs):
        if 'ACL' in attrs and not isinstance(attrs['ACL'], leancloud.ACL):
            raise TypeError('acl must be a ACL')
        return False

    def _validate(self, attrs, silent=True):
        # TODO
        if silent or not self.validate:
            return True

        return True

    def get(self, attr):
        return self.attributes.get(attr)

    def relation(self, attr):
        value = self.get(attr)
        if value is not None:
            if not isinstance(value, leancloud.Relation):
                raise TypeError('field %s is not Relation'.format(attr))
            value._ensure_parent_and_key(self, attr)
            return value
        return leancloud.Relation(self, attr)

    def has(self, attr):
        return attr in self.attributes

    def set(self, key, value=None, unset=False, silent=True):
        if isinstance(key, dict) and value is None:
            attrs = key
        else:
            attrs = {key: utils.decode(key, value)}

        if unset:
            for k in attrs.keys():
                attrs[k] = op.Unset()

        # data_to_validate = copy.deepcopy(attrs)
        # for k, v in data_to_validate.iteritems():
        #     if isinstance(v, op.BaseOp):
        #         data_to_validate[key] = v._estimate(self.attributes[k], self, k)
        #         if data_to_validate[key] == op._UNSET:
        #             del data_to_validate[key]

        if not self._validate(attrs):
            return False

        self._merge_magic_field(attrs)

        keys = attrs.keys()
        for k in keys:
            v = attrs[k]
            # TODO: Relation

            if not isinstance(v, op.BaseOp):
                v = op.Set(v)

            is_real_change = True
            if isinstance(v, op.Set) and self.attributes.get(k) == v:  # TODO: equal
                is_real_change = False

            current_changes = self._op_set_queue[-1]
            current_changes[k] = v._merge_with_previous(current_changes.get(k))
            self._rebuild_estimated_data_for_key(k)

        return self

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
        return self._op_set_queue[-1][attr]

    def clear(self):
        self.set(self.attributes, unset=True)

    def _dump_save(self):
        result = copy.deepcopy(self._op_set_queue[0])
        for k, v in result.iteritems():
            result[k] = v.dump()
        return result

    def fetch(self):
        response = rest.get('/classes/{}/{}'.format(self._class_name, self.id))
        result = self.parse(response)
        self._finish_fetch(result)

    def parse(self, content, status_code=None):
        if 'error' in content:
            raise leancloud.LeanCloudError(content['code'], content['error'])

        self._existed = True
        if status_code == 201:
            self._existed = False

        return content

    def clone(self):
        pass

    def is_new(self):
        return True if self.id else False

    def is_existed(self):
        return self._existed

    def change(self):
        pass

    def get_acl(self):
        return self.get('ACL')

    def set_acl(self, acl):
        return self.set('ACL', acl)

    def _finish_save(self, server_data):
        # TODO: traverse obj

        saved_changes = self._op_set_queue[0]
        self._op_set_queue = self._op_set_queue[1:]
        self._apply_op_set(saved_changes, self._server_data)
        self._merge_magic_field(server_data)
        for key, value in server_data.iteritems():
            self._server_data[key] = utils.decode(key, value)

            # TODO:

            self._rebuild_all_estimated_data()

    def _finish_fetch(self, server_data, has_data):
        self._op_set_queue = [{}]

        self._merge_magic_field(server_data)

        for key, value in server_data.iteritems():
            self._server_data[key] = utils.decode(key, value)

        self._rebuild_all_estimated_data()

        self._op_set_queue = [{}]

        self._has_data = has_data

    def _rebuild_estimated_data_for_key(self, key):
        if self.attributes.get(key):
            del self.attributes[key]

        for op_set in self._op_set_queue:
            o = op_set.get(key)
            if o is None:
                continue
            self.attributes[key] = o._estimate(self.attributes.get(key), self, key)
            if self.attributes[key] is op._UNSET:
                del self.attributes[key]

    def _rebuild_all_estimated_data(self):
        # TODO
        previous_attributes = copy.deepcopy(self.attributes)
        self.attributes = copy.deepcopy(self._server_data)

        for op_set in self._op_set_queue:
            # apply local changes
            self._apply_op_set(op_set, self.attributes)


    def _apply_op_set(self, op_set, target):
        for key, change in op_set.iteritems():
            target[key] = change._estimate(target.get(key), self, key)
            if target[key] == op._UNSET:
                del target[key]
