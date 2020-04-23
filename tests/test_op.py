# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from nose.tools import assert_equal

import leancloud
from leancloud import operation  # type:ignore

__author__ = "asaka <lan@leancloud.rocks>"


def test_set():  # type: () -> None
    s = operation.Set(10)
    assert s.value == 10


def test_unset():  # type: () -> None
    s = operation.Unset()
    assert s._apply(operation.Set(10)) == operation._UNSET


def test_increment():  # type: () -> None
    s = operation.Increment(1)
    assert s.amount == 1
    previous = operation.Increment(2)
    new = s._merge(previous)
    assert isinstance(new, operation.Increment)
    assert new.amount == 3


def test_apply_relation_op():  # type: () -> None
    album = leancloud.Object.create("Album", objectId="abc001", title="variety")
    band1 = leancloud.Object.create("Band", objectId="abc101", name="xxx")
    band2 = leancloud.Object.create("Band", objectId="abc102", name="ooo")

    relation = album.relation("band")

    op = operation.Relation([band1], [band2])
    val = op._apply(None, album, "band")
    assert isinstance(val, leancloud.Relation)
    val._ensure_parent_and_key(album, "band")

    val = op._apply(relation)
    assert isinstance(val, leancloud.Relation)
    val._ensure_parent_and_key(album, "band")


def test_bit_op():  # type: () -> None
    unset = operation.Unset()

    add_ = operation.BitAnd(123)
    assert_equal(add_._merge(unset).value, 0)

    or_ = operation.BitOr(321)
    assert_equal(or_._merge(unset).value, 321)

    xor = operation.BitOr(321)
    assert_equal(xor._merge(unset).value, 321)
