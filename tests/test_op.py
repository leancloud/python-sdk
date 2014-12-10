# coding: utf-8

from leancloud import op

__author__ = 'asaka <lan@leancloud.rocks>'


def test_set():
    s = op.Set(10)
    assert s.value == 10


def test_unset():
    s = op.Unset()
    assert s._estimate(op.Set(10)) == op._UNSET


def test_increment():
    s = op.Increment(1)
    assert s.amount == 1
    previous = op.Increment(2)
    new = s._merge_with_previous(previous)
    assert isinstance(new, op.Increment)
    assert new.amount == 3
