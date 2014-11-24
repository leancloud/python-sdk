# coding: utf-8

__author__ = 'asaka <lan@leancloud.rocks>'

from leancloud import rest
from leancloud.avobject import AVObject


class QueryError(Exception):
    def __init__(self, code, error):
        self.code = code
        self.error = error

    def __repr(self):
        return '{} {}'.format(self.code, self.error)


class NotExists(Exception):
    pass


class AVQuery(object):
    def __init__(self, query_class):
        if isinstance(query_class, basestring):
            query_class = AVObject.extend(query_class)
        self.query_class = query_class

        self.where = {}
        self.include = {}
        self.limit = -1
        self.skip = 0
        self.extra = {}
        self.order = []
        self.select = []

    def do_cloud_query(self, cql, *pvalues):
        params = {'cql': cql}
        if len(pvalues) == 1 and isinstance(pvalues[0], [tuple, list]):
            pvalues = pvalues[0]
        if len(pvalues) > 0:
            params['pvalues'] = pvalues

        result = rest.get('/cloudQuery', params)
        return result

    def dump(self):
        """
        :return: Returns a dict representation of this query.
        :rtype: dict
        """
        params = {
            'where': self.where,
        }
        if self.include:
            params['include'] = ','.join(self.include)
        if self.select:
            params['keys'] = ','.join(self.select)
        if self.limit >= 0:
            params['limit'] = self.limit
        if self.skip > 0:
            params['skip'] = self.skip
        if self.order:
            params['order'] = self.order
        params.update(self.extra)
        return params

    def parse_result(self, result):
        if 'error' in result:
            raise QueryError(result['code'], result['error'])

        obj = self.query_class
        for k, v in result.iteritems():
            obj.set(k, v)
        obj.id = obj.objectId

        return obj

    def parse_list_result(self, raw):
        if 'error' in raw:
            raise QueryError(raw['code'], raw['error'])

        results = []
        for result in raw['results']:
            obj = self.query_class()
            for k, v in result.iteritems():
                obj.set(k, v)
            obj.id = obj.objectId
            results.append(obj)

        return results

    def first(self):
        params = self.dump()
        params['limit'] = 1
        result = rest.get('/classes/{}'.format(self.query_class._class_name), params)
        if not result:
            raise NotExists
        return self.parse_list_result(result)[0]

    def get(self, object_id):
        self.equal_to('objectId', object_id)
        return self.first()

    def find(self):
        result = rest.get('/classes/{}'.format(self.query_class._class_name), self.dump())
        return self.parse_list_result(result)

    def destory_all(self):
        result = rest.delete('/classes/{}'.format(self.query_class._class_name), self.dump())
        return result

    def count(self):
        params = self.dump()
        params['limit'] = 0
        params['count'] = 1
        result = rest.get('/classes/{}'.format(self.query_class._class_name), params)
        return result['count']

    def skip(self, n):
        self.skip = n
        return self

    def limit(self, n):
        self.limit = n
        return self

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

    # TODO: regex condition

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

    # TODO: GEO query

    def include(self, *keys):
        if len(keys) == 1 and isinstance(keys[0], [list, tuple]):
            keys = keys[0]
        self.include = keys
        return self
