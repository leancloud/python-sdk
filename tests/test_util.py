# coding: utf-8

from leancloud import Object
from leancloud import ACL
from leancloud import GeoPoint
from leancloud import utils

__author__ = 'asaka <lan@leancloud.rocks>'


def test_encode():
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


def test_decode():
    p =utils.decode('', {
        '__type': 'GeoPoint',
        'longitude': 0,
        'latitude': 0,
    })
    assert isinstance(p, GeoPoint)
    assert p.latitude == 0
    assert p.longitude == 0
