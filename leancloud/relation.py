# coding: utf-8

import leancloud
from leancloud import op

__author__ = 'asaka <lan@leancloud.rocks>'


class Relation(object):
    def __init__(self, parent, key=None):
        self.parent = parent
        self.key = key
        self.target_class_name = None

    @classmethod
    def reverse_query(cls, parent_class, relation_key, child):
        q = leancloud.Query(parent_class)
        q.equal_to(relation_key, child._to_pointer())
        return q

    def _ensure_parent_and_key(self, parent, key):
        if self.parent is not None:
            self.parent = parent
        if self.key is not None:
            self.key = key

        if self.parent != parent:
            raise TypeError('relation retrieved from two different object')
        if self.key != key:
            raise TypeError('relation retrieved from two different object')

    def add(self, *obj_or_objs):
        objs = obj_or_objs
        if not isinstance(obj_or_objs, (list, tuple)):
            objs = (obj_or_objs, )
        change = op.Relation(objs, ())
        self.parent.set(self.key, change)
        self.target_class_name = change._target_class_name

    def remove(self, *obj_or_objs):
        objs = obj_or_objs
        if not isinstance(obj_or_objs, (list, tuple)):
            objs = (obj_or_objs, )
        change = op.Relation((), objs)
        self.parent.set(self.key, change)
        self.target_class_name = change._target_class_name

    def dump(self):
        return {
            '__type': 'Relation',
            'className': self.target_class_name
        }

    def query(self):
        if self.target_class_name is None:
            target_class = leancloud.Object._get_subclass(self.parent.class_name)
            query = leancloud.Query(target_class)
            query._extra['redirectClassNameForKey'] = self.key
        else:
            target_class = leancloud.Object._get_subclass(self.target_class_name)
            query = leancloud.Query(target_class)

        query._add_condition('$relatedTo', 'object', self.parent._to_pointer())
        query._add_condition('$relatedTo', 'key', self.key)

        return query
