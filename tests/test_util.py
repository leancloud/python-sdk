# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time

from nose.tools import eq_

import leancloud
from leancloud import Object
from leancloud import ACL
from leancloud import GeoPoint
from leancloud import utils

__author__ = 'asaka <lan@leancloud.rocks>'


def test_encode(): # type: () -> None
    Foo = Object.extend('Foo')
    obj = Foo()
    assert utils.encode(obj) == {
        'className': 'Foo',
        '__type': 'Pointer',
        'objectId': None,
    }

    acl = ACL()
    assert utils.encode(acl) == {}
    acl.set_read_access('xxx', True)
    assert utils.encode(acl) == {'xxx': {'read': True}}

    point = GeoPoint()
    assert utils.encode(point) == {
        '__type': 'GeoPoint',
        'longitude': 0,
        'latitude': 0,
    }

    assert utils.encode([obj, acl, point]) == [
        {
            'className': 'Foo',
            '__type': 'Pointer',
            'objectId': None,
        }, {
            'xxx': {'read': True}
        }, {
            '__type': 'GeoPoint',
            'longitude': 0,
            'latitude': 0,
        }
    ]

    assert utils.encode({'a': obj, 'b': acl}) == {
        'a': {
            'className': 'Foo',
            '__type': 'Pointer',
            'objectId': None,
        },
        'b': {
            'xxx': {'read': True}
        },
    }


def test_decode(): # type: () -> None
    p = utils.decode('test_key', {
        '__type': 'GeoPoint',
        'longitude': 0,
        'latitude': 0,
    })
    assert isinstance(p, GeoPoint)
    assert p.latitude == 0
    assert p.longitude == 0


def test_util(): # type: () -> None
    obj = Object.extend('Foo')()

    def callback(o):
        callback.count += 1
        if callback.count == 1:
            assert o == {}
        elif callback.count == 2:
            assert o == obj

    callback.count = 0

    utils.traverse_object(obj, callback)

    assert callback.count == 2


def test_sign_hook(): # type: () -> None
    sign = utils.sign_hook('__before_for_TestClass', 'test-master-key', '1453711871302')
    eq_(sign, '1453711871302,f10c9dd65da84b564f1b9a8b57df4a07774bc77b')
    sign = utils.sign_hook('__before_for_TestClass', 'test-master-key', int(time.time()) * 1000)
    leancloud.engine.utils.verify_hook_sign('__before_for_TestClass', 'test-master-key', sign)
