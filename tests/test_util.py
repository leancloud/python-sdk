# coding: utf-8

from leancloud import Object
from leancloud import GeoPoint
from leancloud import utils

__author__ = 'asaka <lan@leancloud.rocks>'


def test_encode():
    obj = Object.extend('Foo')
    utils.encode(obj)