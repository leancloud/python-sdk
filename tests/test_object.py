# coding: utf-8

from nose.tools import with_setup
from nose.tools import ok_
from nose.tools import eq_

import leancloud
from leancloud import op
from leancloud import Object
from leancloud import Query

__author__ = 'asaka <lan@leancloud.rocks>'


def setup_func():
    leancloud.init(
        'pgk9e8orv8l9coak1rjht1avt2f4o9kptb0au0by5vbk9upb',
        'hi4jsm62kok2qz2w2qphzryo564rzsrucl2czb0hn6ogwwnd',
    )


class Album(Object):
    pass


def test_new():
    album = Album()
    assert album._class_name == 'Album'


def test_set():
    album = Album()
    album.set('title', 'Nightwish')
    eq_(album.attributes, {'title': 'Nightwish'})

    album = Album(title='Nightwish')
    eq_(album.attributes, {'title': 'Nightwish'})


def test_get():
    album = Album()
    album.set('foo', 'bar')
    assert album.get('foo') == 'bar'


def test_unset():
    album = Album()
    album.set('foo', 'bar')
    album.unset('foo')
    assert album.get('foo') is None
    assert album.has('foo') is False


def test_increment():
    album = Album()
    album.set('foo', 1)
    album.increment('foo', 1)
    assert album.get('foo') == 2


def test_add():
    album = Album()
    album.add('foo', 1)
    eq_(album.get('foo'), [1])
    album.add('foo', 2)
    eq_(album.get('foo'), [1, 2])


def test_add_unique():
    album = Album()
    album.add_unique('foo', 1)
    album.add_unique('foo', 1)
    eq_(album.get('foo'), [1])
    album.add_unique('foo', 2)
    eq_(album.get('foo'), [1, 2])


def test_remove():
    album = Album()
    album.set('foo', ['bar', 'baz'])
    album.remove('foo', 'bar')
    eq_(album.get('foo'), ['baz'])


def test_op():
    album = Album()
    album.set('foo', 'bar')
    assert isinstance(album.op('foo'), op.Set)


def test_dump_save():
    album = Album()
    album.set('foo', 'bar')
    eq_(album._dump_save(), {'foo': 'bar'})


def test_extend():
    ok_(Object.extend('Album'))


def test_finish_fetch():
    album = Album()
    album._finish_fetch({'title': 'Once', 'artist': 'nightwish'}, False)
    eq_(album.attributes, {'title': 'Once', 'artist': 'nightwish'})


def test_dump():
    album = Album()
    album.set('foo', 'bar')
    eq_(album.dump(), {'foo': 'bar'})


def test_to_pointer():
    album = Album()
    album.set('foo', 'bar')
    album._to_pointer()


def test_has():
    album = Album()
    album.set('foo', 'bar')
    assert album.has('foo') is True
    assert album.has('bar') is False

def test_get_set_acl():
    album = Album()
    album.set_acl('foo')
    assert album.get_acl() == 'foo'