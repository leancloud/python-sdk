# coding: utf-8

from leancloud import operation

__author__ = 'asaka <lan@leancloud.rocks>'


def test_set():
    s = operation.Set(10)
    assert s.value == 10


def test_unset():
    s = operation.Unset()
    assert s._apply(operation.Set(10)) == operation._UNSET


def test_increment():
    s = operation.Increment(1)
    assert s.amount == 1
    previous = operation.Increment(2)
    new = s._merge(previous)
    assert isinstance(new, operation.Increment)
    assert new.amount == 3
