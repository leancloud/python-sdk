# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import warnings

import leancloud
from leancloud import client
from leancloud import utils
from leancloud.object_ import Object
from leancloud.errors import LeanCloudError
from leancloud.errors import LeanCloudWarning
from leancloud._compat import string_types
from leancloud._compat import class_types

__author__ = 'asaka <lan@leancloud.rocks>'


class CQLResult(object):
    """
    CQL 查询结果对象。

    Attributes:
        results: 返回的查询结果

        count: 如果查询语句包含 count，将保存在此字段

        class_name: 查询的 class 名称
    """
    def __init__(self, results, count, class_name):
        self.results = results
        self.count = count
        self.class_name = class_name


class Query(object):
    def __init__(self, query_class):
        """

        :param query_class: 要查询的 class 名称或者对象
        :type query_class: string_types or leancloud.ObjectMeta
        """
        if isinstance(query_class, string_types):
            query_class = Object.extend(query_class)

        if (not isinstance(query_class, (type, class_types))) or (not issubclass(query_class, Object)):
            raise ValueError('Query takes string or LeanCloud Object')

        self._query_class = query_class

        self._where = {}
        self._include = []
        self._limit = -1
        self._skip = 0
        self._extra = {}
        self._order = []
        self._select = []

    def __call__(self):
        warnings.warn('leancloud.Relation.query now is a property, please don\'t call it as a function', LeanCloudWarning)
        return self

    @classmethod
    def or_(cls, *queries):
        """
        根据传入的 Query 对象，构造一个新的 OR 查询。

        :param queries: 需要构造的子查询列表
        :rtype: Query
        """
        if len(queries) < 2:
            raise ValueError('or_ need two queries at least')
        if not all(x._query_class._class_name == queries[0]._query_class._class_name for x in queries):
            raise TypeError('All queries must be for the same class')
        query = Query(queries[0]._query_class._class_name)
        query._or_query(queries)
        return query

    @classmethod
    def and_(cls, *queries):
        """
        根据传入的 Query 对象，构造一个新的 AND 查询。

        :param queries: 需要构造的子查询列表
        :rtype: Query
        """
        if len(queries) < 2:
            raise ValueError('and_ need two queries at least')
        if not all(x._query_class._class_name == queries[0]._query_class._class_name for x in queries):
            raise TypeError('All queries must be for the same class')
        query = Query(queries[0]._query_class._class_name)
        query._and_query(queries)
        return query

    @classmethod
    def do_cloud_query(cls, cql, *pvalues):
        """
        使用 CQL 来构造查询。CQL 语法参考 `这里 <https://cn.avoscloud.com/docs/cql_guide.html>`_。

        :param cql: CQL 语句
        :param pvalues: 查询参数
        :rtype: CQLResult
        """
        params = {'cql': cql}
        if len(pvalues) == 1 and isinstance(pvalues[0], (tuple, list)):
            pvalues = json.dumps(pvalues[0])
        if len(pvalues) > 0:
            params['pvalues'] = json.dumps(pvalues)

        content = client.get('/cloudQuery', params).json()

        objs = []
        query = cls(content['className'])
        for result in content['results']:
            obj = query._new_object()
            obj._finish_fetch(query._process_result(result), True)
            objs.append(obj)

        return CQLResult(objs, content.get('count'), content.get('className'))

    def dump(self):
        """
        :return: 当前对象的序列化结果
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
            params['order'] = ",".join(self._order)
        params.update(self._extra)
        return params

    def _new_object(self):
        return self._query_class()

    def _process_result(self, obj):
        return obj

    def first(self):
        """
        根据查询获取最多一个对象。

        :return: 查询结果
        :rtype: Object
        :raise: LeanCloudError
        """
        params = self.dump()
        params['limit'] = 1
        content = client.get('/classes/{0}'.format(self._query_class._class_name), params).json()
        results = content['results']
        if not results:
            raise LeanCloudError(101, 'Object not found')
        obj = self._new_object()
        obj._finish_fetch(self._process_result(results[0]), True)
        return obj

    def get(self, object_id):
        """
        根据 objectId 查询。

        :param object_id: 要查询对象的 objectId
        :return: 查询结果
        :rtype: Object
        """
        self.equal_to('objectId', object_id)
        return self.first()

    def find(self):
        """
        根据查询条件，获取包含所有满足条件的对象。

        :rtype: list
        """
        content = client.get('/classes/{0}'.format(self._query_class._class_name), self.dump()).json()

        objs = []
        for result in content['results']:
            obj = self._new_object()
            obj._finish_fetch(self._process_result(result), True)
            objs.append(obj)

        return objs

    # def destroy_all(self):
    #     """
    #     在服务器上删除所有满足查询条件的对象。

    #     :raise: LeanCLoudError
    #     """
    #     result = client.delete('/classes/{0}'.format(self._query_class._class_name), self.dump())
    #     return result

    def count(self):
        """
        返回满足查询条件的对象的数量。

        :rtype: int
        """
        params = self.dump()
        params['limit'] = 0
        params['count'] = 1
        response = client.get('/classes/{0}'.format(self._query_class._class_name), params)
        return response.json()['count']

    def skip(self, n):
        """
        查询条件中跳过指定个数的对象，在做分页时很有帮助。

        :param n: 需要跳过对象的个数
        :rtype: Query
        """
        self._skip = n
        return self

    def limit(self, n):
        """
        设置查询返回结果的数量。如果不设置，默认为 100。最大返回数量为 1000，如果超过这个数量，需要使用多次查询来获取结果。

        :param n: 限制结果的数量
        :rtype: Query
        """
        if n > 1000:
            raise ValueError('limit only accept number less than or equal to 1000')
        self._limit = n
        return self

    def equal_to(self, key, value):
        """
        增加查询条件，查询字段的值必须为指定值。

        :param key: 查询条件的字段名
        :param value: 查询条件的值
        :rtype: Query
        """
        self._where[key] = utils.encode(value)
        return self

    def _add_condition(self, key, condition, value):
        if not self._where.get(key):
            self._where[key] = {}
        self._where[key][condition] = utils.encode(value)
        return self

    def not_equal_to(self, key, value):
        """
        增加查询条件，限制查询结果指定字段的值与查询值不同

        :param key: 查询条件字段名
        :param value: 查询条件值
        :rtype: Query
        """
        self._add_condition(key, '$ne', value)
        return self

    def less_than(self, key, value):
        """
        增加查询条件，限制查询结果指定字段的值小于查询值

        :param key: 查询条件字段名
        :param value: 查询条件值
        :rtype: Query
        """
        self._add_condition(key, '$lt', value)
        return self

    def greater_than(self, key, value):
        """
        增加查询条件，限制查询结果指定字段的值大于查询值

        :param key: 查询条件字段名
        :param value: 查询条件值
        :rtype: Query
        """
        self._add_condition(key, '$gt', value)
        return self

    def less_than_or_equal_to(self, key, value):
        """
        增加查询条件，限制查询结果指定字段的值小于等于查询值

        :param key: 查询条件字段名
        :param value: 查询条件值
        :rtype: Query
        """
        self._add_condition(key, '$lte', value)
        return self

    def greater_than_or_equal_to(self, key, value):
        """
        增加查询条件，限制查询结果指定字段的值大于等于查询值

        :param key: 查询条件字段名
        :param value: 查询条件值名
        :rtype: Query
        """
        self._add_condition(key, '$gte', value)
        return self

    def contained_in(self, key, values):
        """
        增加查询条件，限制查询结果指定字段的值在查询值列表中

        :param key: 查询条件字段名
        :param values: 查询条件值
        :type values: list or tuple
        :rtype: Query
        """
        self._add_condition(key, '$in', values)
        return self

    def not_contained_in(self, key, values):
        """
        增加查询条件，限制查询结果指定字段的值不在查询值列表中

        :param key: 查询条件字段名
        :param values: 查询条件值
        :type values: list or tuple
        :rtype: Query
        """
        self._add_condition(key, '$nin', values)
        return self

    def contains_all(self, key, values):
        """
        增加查询条件，限制查询结果指定字段的值全部包含与查询值列表中

        :param key: 查询条件字段名
        :param values: 查询条件值
        :type values: list or tuple
        :rtype: Query
        """
        self._add_condition(key, '$all', values)
        return self

    def exists(self, key):
        """
        增加查询条件，限制查询结果对象包含指定字段

        :param key: 查询条件字段名
        :rtype: Query
        """
        self._add_condition(key, '$exists', True)
        return self

    def does_not_exists(self, key):
        """
        增加查询条件，限制查询结果对象不包含指定字段

        :param key: 查询条件字段名
        :rtype: Query
        """
        self._add_condition(key, '$exists', False)
        return self

    def matched(self, key, regex, ignore_case=False, multi_line=False):
        """
        增加查询条件，限制查询结果对象指定字段满足指定的正则表达式。

        :param key: 查询条件字段名
        :param regex: 查询正则表达式
        :param ignore_case: 查询是否忽略大小写，默认不忽略
        :param multi_line: 查询是否匹配多行，默认不匹配
        :rtype: Query
        """
        if not isinstance(regex, string_types):
            raise TypeError('matched only accept str or unicode')
        self._add_condition(key, '$regex', regex)
        modifiers = ''
        if ignore_case:
            modifiers += 'i'
        if multi_line:
            modifiers += 'm'
        if modifiers:
            self._add_condition(key, '$options', modifiers)
        return self

    def matches_query(self, key, query):
        """
        增加查询条件，限制查询结果对象指定字段的值，与另外一个查询对象的返回结果相同。

        :param key: 查询条件字段名
        :param query: 查询对象
        :type query: Query
        :rtype: Query
        """
        dumped = query.dump()
        dumped['className'] = query._query_class._class_name
        self._add_condition(key, '$inQuery', dumped)
        return self

    def does_not_match_query(self, key, query):
        """
        增加查询条件，限制查询结果对象指定字段的值，与另外一个查询对象的返回结果不相同。

        :param key: 查询条件字段名
        :param query: 查询对象
        :type query: Query
        :rtype: Query
        """
        dumped = query.dump()
        dumped['className'] = query._query_class._class_name
        self._add_condition(key, '$notInQuery', dumped)
        return self

    def matched_key_in_query(self, key, query_key, query):
        warnings.warn(' the query is deprecated, please use matches_key_in_query', LeanCloudWarning)
        return self.matches_key_in_query(key, query_key, query)

    def matches_key_in_query(self, key, query_key, query):
        """
        增加查询条件，限制查询结果对象指定字段的值，与另外一个查询对象的返回结果指定的值相同。

        :param key: 查询条件字段名
        :param query_key: 查询对象返回结果的字段名
        :param query: 查询对象
        :type query: Query
        :rtype: Query
        """
        dumped = query.dump()
        dumped['className'] = query._query_class._class_name
        self._add_condition(key, '$select', {'key': query_key, 'query': dumped})
        return self

    def does_not_match_key_in_query(self, key, query_key, query):
        """
        增加查询条件，限制查询结果对象指定字段的值，与另外一个查询对象的返回结果指定的值不相同。

        :param key: 查询条件字段名
        :param query_key: 查询对象返回结果的字段名
        :param query: 查询对象
        :type query: Query
        :rtype: Query
        """
        dumped = query.dump()
        dumped['className'] = query._query_class._class_name
        self._add_condition(key, '$dontSelect', {'key': query_key, 'query': dumped})
        return self

    def _or_query(self, queries):
        dumped = [q.dump()['where'] for q in queries]
        self._where['$or'] = dumped
        return self

    def _and_query(self, queries):
        dumped = [q.dump()['where'] for q in queries]
        self._where['$and'] = dumped

    def _quote(self, s):
        # return "\\Q" + s.replace("\\E", "\\E\\\\E\\Q") + "\\E"
        return s

    def contains(self, key, value):
        """
        增加查询条件，限制查询结果对象指定最短的值，包含指定字符串。在数据量比较大的情况下会比较慢。

        :param key: 查询条件字段名
        :param value: 需要包含的字符串
        :rtype: Query
        """
        self._add_condition(key, '$regex', self._quote(value))
        return self

    def startswith(self, key, value):
        """
        增加查询条件，限制查询结果对象指定最短的值，以指定字符串开头。在数据量比较大的情况下会比较慢。

        :param key: 查询条件字段名
        :param value: 需要查询的字符串
        :rtype: Query
        """
        self._add_condition(key, '$regex', '^' + self._quote(value))
        return self

    def endswith(self, key, value):
        """
        增加查询条件，限制查询结果对象指定最短的值，以指定字符串结尾。在数据量比较大的情况下会比较慢。

        :param key: 查询条件字段名
        :param value: 需要查询的字符串
        :rtype: Query
        """
        self._add_condition(key, '$regex', self._quote(value) + '$')
        return self

    def ascending(self, key):
        """
        限制查询返回结果以指定字段升序排序。

        :param key: 排序字段名
        :rtype: Query
        """
        self._order = [key]
        return self

    def add_ascending(self, key):
        """
        增加查询排序条件。之前指定的排序条件优先级更高。

        :param key: 排序字段名
        :rtype: Query
        """
        self._order.append(key)
        return self

    def descending(self, key):
        """
        限制查询返回结果以指定字段降序排序。

        :param key: 排序字段名
        :rtype: Query
        """
        self._order = ['-{0}'.format(key)]
        return self

    def add_descending(self, key):
        """
        增加查询排序条件。之前指定的排序条件优先级更高。

        :param key: 排序字段名
        :rtype: Query
        """
        self._order.append('-{0}'.format(key))
        return self

    def near(self, key, point):
        """
        增加查询条件，限制返回结果指定字段值的位置与给定地理位置临近。

        :param key: 查询条件字段名
        :param point: 需要查询的地理位置
        :rtype: Query
        """
        self._add_condition(key, '$nearSphere', point)
        return self

    def within_radians(self, key, point, max_distance, min_distance=None):
        """
        增加查询条件，限制返回结果指定字段值的位置在某点的一段距离之内。

        :param key: 查询条件字段名
        :param point: 查询地理位置
        :param max_distance: 最大距离限定（弧度）
        :param min_distance: 最小距离限定（弧度）
        :rtype: Query
        """
        self.near(key, point)
        self._add_condition(key, '$maxDistance', max_distance)
        if min_distance is not None:
            self._add_condition(key, '$minDistance', min_distance)
        return self

    def within_miles(self, key, point, max_distance, min_distance=None):
        """
        增加查询条件，限制返回结果指定字段值的位置在某点的一段距离之内。

        :param key: 查询条件字段名
        :param point: 查询地理位置
        :param max_distance: 最大距离限定（英里）
        :param min_distance: 最小距离限定（英里）
        :rtype: Query
        """
        if min_distance is not None:
            min_distance = min_distance / 3958.8
        return self.within_radians(key, point, max_distance / 3958.8, min_distance)

    def within_kilometers(self, key, point, max_distance, min_distance=None):
        """
        增加查询条件，限制返回结果指定字段值的位置在某点的一段距离之内。

        :param key: 查询条件字段名
        :param point: 查询地理位置
        :param max_distance: 最大距离限定（千米）
        :param min_distance: 最小距离限定（千米）
        :rtype: Query
        """
        if min_distance is not None:
            min_distance = min_distance / 6371.0
        return self.within_radians(key, point, max_distance / 6371.0, min_distance)

    def within_geo_box(self, key, southwest, northeast):
        """
        增加查询条件，限制返回结果指定字段值的位置在指定坐标范围之内。

        :param key: 查询条件字段名
        :param southwest: 限制范围西南角坐标
        :param northeast: 限制范围东北角坐标
        :rtype: Query
        """
        self._add_condition(key, '$within', {'$box': [southwest, northeast]})
        return self

    def include(self, *keys):
        """
        指定查询返回结果中包含关联表字段。

        :param keys: 关联子表字段名
        :rtype: Query
        """
        if len(keys) == 1 and isinstance(keys[0], (list, tuple)):
            keys = keys[0]
        self._include += keys
        return self

    def select(self, *keys):
        """
        指定查询返回结果中只包含某些字段。可以重复调用，每次调用的包含内容都将会被返回。

        :param keys: 包含字段名
        :rtype: Query
        """
        if len(keys) == 1 and isinstance(keys[0], (list, tuple)):
            keys = keys[0]
        self._select += keys
        return self


class FriendshipQuery(Query):
    def __init__(self, query_class):
        super(FriendshipQuery, self).__init__(query_class)
        if query_class in ('_Follower', 'Follower'):
            self._friendship_tag = 'follower'
        elif query_class in ('_Followee', 'Followee'):
            self._friendship_tag = 'followee'
        else:
            raise TypeError('FriendshipQuery takes only follower or followee')

    def _new_object(self):
        return leancloud.User()

    def _process_result(self, obj):
        content = obj[self._friendship_tag]
        if content['__type'] == 'Pointer' and content['className'] == '_User':
            del content['__type']
            del content['className']
        return content
