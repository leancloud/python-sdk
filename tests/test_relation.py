# coding: utf-8

from leancloud import Object
from leancloud import Relation

__author__ = 'asaka <lan@leancloud.rocks>'


class Foo(Object):
    pass


def test_relation():
    foo = Foo()
    r = Relation(foo, 'bar')
