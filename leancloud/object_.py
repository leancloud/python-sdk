# coding: utf-8

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
            self.id = id
            self._has_been_fetched = False
        else:
            self._has_been_fetched = False

    def get(self, key):
        if not self._is_data_available(key):
            raise ValueError('leancloud.Object has no data for this key, call fetch() to get the data')
        return self._attrs.get(key, None)

    def has(self, key):
        return key in self._attrs

    def is_key_dirty(self, key):
        return key in self._op_set

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