# coding: utf-8

__author__ = 'asaka <lan@leancloud.rocks>'


class Query(object):
    def __init__(self, query_class):
        self.query_class = query_class

        self.where = {}
        self.include = {}
        self.limit = -1
        self.skip = 0
        self.extra = {}
        self.order = []

    def equal_to(self, key, value):
        self.where[key] = value
        return self

    def _add_condition(self, key, condition, value):
        if not self.where.get(key):
            self.where[key] = {}
        self.where[key][condition] = value
        return self

    def not_equal_to(self, key, value):
        self._add_condition(key, '$ne', value)
        return self

    def less_than(self, key, value):
        self._add_condition(key, '$lt', value)
        return self

    def greater_than(self, key, value):
        self._add_condition(key, '$gt', value)
        return self

    def less_than_or_equal_to(self, key, value):
        self._add_condition(key, '$lte', value)
        return self

    def greater_than_or_equal_to(self, key, value):
        self._add_condition(key, '$gte', value)
        return self

    def contained_in(self, key, value):
        self._add_condition(key, '$in', value)
        return self

    def not_contained_in(self, key, value):
        self._add_condition(key, '$nin', value)
        return self

    def contains_all(self, key, value):
        self._add_condition(key, '$all', value)
        return self

    def exists(self, key):
        self._add_condition(key, '$exists', True)
        return self

    def dose_not_exists(self, key):
        self._add_condition(key, '$exists', False)
        return self

    # TODO: reg condition

    def ascending(self, key):
        self.order = [key]
        return self

    def add_ascending(self, key):
        self.order.append(key)
        return self

    def descending(self, key):
        self.order = ['-{}'.format(key)]
        return self

    def add_descending(self, key):
        self.order.append('-{}'.format(key))
        return self

    # TODO: geo query

    def include(self, *keys):
        if len(keys) == 1 and isinstance(keys[0], [list, tuple]):
            keys = keys[0]
        self.include = keys
        return self