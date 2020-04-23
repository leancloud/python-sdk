# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from nose.tools import assert_raises  # type: ignore
from nose.tools import eq_  # type: ignore

from leancloud import GeoPoint


__author__ = "asaka <lan@leancloud.rocks>"


def test_invalid():  # type: () -> None
    assert_raises(ValueError, GeoPoint, 0, 200)
    assert_raises(ValueError, GeoPoint, -100, 10)


def test_setter():  # type: () -> None
    p = GeoPoint()
    p.latitude = 10
    assert p.latitude == 10

    def f():
        p.longitude = 200

    assert_raises(ValueError, f)


def test_dump():  # type: () -> None
    p = GeoPoint(10, 20)
    assert p.dump() == {"latitude": 10, "__type": "GeoPoint", "longitude": 20}


def test_radians_to():  # type: () -> None
    assert GeoPoint(0, 0).radians_to(GeoPoint(10, 10)) - 0.24619691677893205 < 0.00001
    assert (
        GeoPoint(10, 10).radians_to(GeoPoint(14.5, 24.5)) - 0.25938444522905957
        < 0.00001
    )


def test_eq():  # type: () -> None
    eq_(GeoPoint(0, 1) == GeoPoint(0, 1), True)
    eq_(GeoPoint(1, 1) == GeoPoint(1, 0), False)
