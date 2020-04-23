# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import leancloud
from leancloud import operation

__author__ = "asaka <lan@leancloud.rocks>"


class Relation(object):
    def __init__(self, parent, key=None):
        self.parent = parent
        self.key = key
        self.target_class_name = None

    @classmethod
    def reverse_query(cls, parent_class, relation_key, child):
        """
        创建一个新的 Query 对象，反向查询所有指向此 Relation 的父对象。

        :param parent_class: 父类名称
        :param relation_key: 父类中 Relation 的字段名
        :param child: 子类对象
        :return: leancloud.Query
        """
        q = leancloud.Query(parent_class)
        q.equal_to(relation_key, child._to_pointer())
        return q

    def _ensure_parent_and_key(self, parent=None, key=None):
        if self.parent is None:
            self.parent = parent
        if self.key is None:
            self.key = key

        if self.parent != parent:
            raise TypeError("relation retrieved from two different object")
        if self.key != key:
            raise TypeError("relation retrieved from two different object")

    def add(self, *obj_or_objs):
        """
        添加一个新的 leancloud.Object 至 Relation。

        :param obj_or_objs: 需要添加的对象或对象列表
        """
        objs = obj_or_objs
        if not isinstance(obj_or_objs, (list, tuple)):
            objs = (obj_or_objs,)
        change = operation.Relation(objs, ())
        self.parent.set(self.key, change)
        self.target_class_name = change._target_class_name

    def remove(self, *obj_or_objs):
        """
        从一个 Relation 中删除一个 leancloud.Object 。

        :param obj_or_objs: 需要删除的对象或对象列表
        :return:
        """
        objs = obj_or_objs
        if not isinstance(obj_or_objs, (list, tuple)):
            objs = (obj_or_objs,)
        change = operation.Relation((), objs)
        self.parent.set(self.key, change)
        self.target_class_name = change._target_class_name

    def dump(self):
        return {"__type": "Relation", "className": self.target_class_name}

    @property
    def query(self):
        """
        获取指向 Relation 内容的 Query 对象。

        :rtype: leancloud.Query
        """

        if self.target_class_name is None:
            target_class = leancloud.Object.extend(self.parent._class_name)
            query = leancloud.Query(target_class)
            query._extra["redirectClassNameForKey"] = self.key
        else:
            target_class = leancloud.Object.extend(self.target_class_name)
            query = leancloud.Query(target_class)

        query._add_condition("$relatedTo", "object", self.parent._to_pointer())
        query._add_condition("$relatedTo", "key", self.key)

        return query
