# coding: utf-8

from leancloud import Query

__author__ = 'asaka'


class Relation(object):
    def __init__(self, parent, key):
        self.parent = parent
        self.key = key
        self.target_class_name = None

    @classmethod
    def reverse_query(cls, parent_class, relation_key, child):
        q = Query(parent_class)
        q.equal_to(relation_key, child._to_pointer())
        return q

    def _ensure_parent_and_key(self, parent=None, key=None):
        if not parent is None:
            self.parent = parent
        if not key is None:
            self.key = key