# coding: utf-8

import leancloud
from leancloud import client
from leancloud.object_ import Object

__author__ = 'asaka <lan@leancloud.rocks>'


class Query(object):
    def __init__(self, query_class):
        if isinstance(query_class, basestring):
            query_class = Object.extend(query_class)
        self._query_class = query_class

        self._where = {}
        self._include = {}
        self._limit = -1
        self._skip = 0
        self._extra = {}
        self._order = []
        self._select = []

    @classmethod
    def do_cloud_query(cls, cql, *pvalues):
        params = {'cql': cql}
        if len(pvalues) == 1 and isinstance(pvalues[0], [tuple, list]):
            pvalues = pvalues[0]
        if len(pvalues) > 0:
            params['pvalues'] = pvalues

        result = client.get('/cloudQuery', params)
        return result

    def dump(self):
        """
        :return: Returns a dict representation of this query.
        :rtype: dict
        """
        params = {
            'where': self._where,
        }
        if self._include:
            params['include'] = ','.join(self._include)
        if self._select:
            params['keys'] = ','.join(self._select)
        if self._limit >= 0:
            params['limit'] = self._limit
        if self._skip > 0:
            params['skip'] = self._skip
        if self._order:
            params['order'] = self._order
        params.update(self._extra)
        return params

    def _new_object(self):
        return self._query_class()

    def _process_result(self, obj):
        return obj

    def first(self):
        params = self.dump()
        params['limit'] = 1
        content = client.get('/classes/{}'.format(self._query_class._class_name), params).json()
        if 'error' in content:
            raise leancloud.LeanCloudError(content['code'], content['error'])
        results = content['results']
        if not results:
            raise leancloud.LeanCloudError(101, 'Object not found')
        obj = self._new_object()
        obj._finish_fetch(self._process_result(results[0]), True)
        return obj

    def get(self, object_id):
        self.equal_to('objectId', object_id)
        return self.first()

    def find(self):
        content = client.get('/classes/{}'.format(self._query_class._class_name), self.dump()).json()
        if 'error' in content:
            raise leancloud.LeanCloudError(content['code'], content['error'])

        objs = []
        for result in content['results']:
            obj = self._new_object()
            obj._finish_fetch(self._process_result(result), True)
            objs.append(obj)

        return objs

    def destroy_all(self):
        result = client.delete('/classes/{}'.format(self._query_class._class_name), self.dump())
        return result

    def count(self):
        params = self.dump()
        params['limit'] = 0
        params['count'] = 1
        response = client.get('/classes/{}'.format(self._query_class._class_name), params)
        return response.json()['count']

    def skip(self, n):
        self._skip = n
        return self

    def limit(self, n):
        self._limit = n
        return self

    def equal_to(self, key, value):
        self._where[key] = value
        return self

    def _add_condition(self, key, condition, value):
        if not self._where.get(key):
            self._where[key] = {}
        self._where[key][condition] = value
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

    def does_not_exists(self, key):
        self._add_condition(key, '$exists', False)
        return self

    # TODO: regex condition

    def ascending(self, key):
        self._order = [key]
        return self

    def add_ascending(self, key):
        self._order.append(key)
        return self

    def descending(self, key):
        self._order = ['-{}'.format(key)]
        return self

    def add_descending(self, key):
        self._order.append('-{}'.format(key))
        return self

    # TODO: GEO query

    def include(self, *keys):
        if len(keys) == 1 and isinstance(keys[0], [list, tuple]):
            keys = keys[0]
        self._include = keys
        return self


class FriendshipQuery(Query):
    def __init__(self, query_class):
        if query_class in ('_Follower', 'Follower'):
            self._friendship_tag = 'follower'
        elif query_class in ('_Followee', 'Followee'):
            self._friendship_tag = 'followee'
        super(FriendshipQuery, self).__init__(leancloud.User)

    def _new_object(self):
        return leancloud.User()

    def _process_result(self, obj):
        content = obj[self._friendship_tag]
        if content['__type'] == 'Pointer' and content['className'] == '_User':
            del content['__type']
            del content['className']
        return content
