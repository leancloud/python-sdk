# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from nose.tools import with_setup
from nose.tools import ok_
from nose.tools import eq_
from nose.tools import assert_raises

import leancloud
from leancloud import Object

__author__ = 'asaka <lan@leancloud.rocks>'


def setup_func():
    leancloud.client.USE_MASTER_KEY = None
    leancloud.client.APP_ID = None
    leancloud.client.APP_KEY = None
    leancloud.client.MASTER_KEY = None
    leancloud.init(
        os.environ['APP_ID'],
        os.environ['APP_KEY']
    )


class Album(Object):
    pass


class Band(Object):
    pass


def test_new():
    album = Album()
    assert album._class_name == 'Album'


def test_class_equal():
    AnotherAlbum = Object.extend('Album')
    assert AnotherAlbum is Album
    album = AnotherAlbum()
    assert isinstance(album, AnotherAlbum)


def test_dirty():
    album = Album()
    assert album.is_dirty() is True
    album.id = 123
    assert album.is_dirty() is False
    album.set('foo', 'bar')
    assert album.is_dirty() is True


def test_find_unsaved_children():
    album = Album()
    unsaved_children = []
    unsaved_files = []
    Object._find_unsaved_children(album, unsaved_children, unsaved_files)
    assert unsaved_children == [album]
    assert unsaved_files == []


@with_setup(setup_func)
def test_file_save():
    import cStringIO
    from leancloud.file_ import File
    s1 = cStringIO.StringIO()
    s1.write('blah blah blah')
    f = File('well', s1)
    album = Album()
    album.set('file', f)
    album.save()


def test_find_unsaved_children_2():
    album = Album()
    band = Band()
    album.set('band', band)
    unsaved_children = []
    unsaved_files = []
    Object._find_unsaved_children(album, unsaved_children, unsaved_files)
    assert unsaved_children == [band, album]


def test_set():
    album = Album()
    album.set('title', 'Nightwish')
    eq_(album._attributes, {'title': 'Nightwish'})

    album = Album(title='Nightwish')
    eq_(album._attributes, {'title': 'Nightwish'})


def test_get():
    album = Album()
    album.set('foo', 'bar')
    assert album.get('foo') == 'bar'


def test_get_deafult():
    album = Album()
    assert album.get('foo', 'bar') == 'bar'


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


@with_setup(setup_func)
def test_increment_atfer_save():
    album = Album()
    album.set('foo', 1)
    album.save()
    album.increment('foo', 234)
    assert album.get('foo') == 235
    album.save()
    assert album.get('foo') == 235


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


def test_clear():
    album = Album(foo=1, bar=2, baz=3)
    album.clear()
    assert album.get('foo') is None
    assert album.get('bar') is None
    assert album.get('baz') is None


def test_full_dump():
    album = Album()
    album.set('title', 'Nightwish')
    assert album._dump() == {
        'className': 'Album',
        '__type': 'Object',
        'title': 'Nightwish',
    }
    band = Band()
    album.set('band', band)
    assert album._dump() == {
        'className': 'Album',
        'band': {
            'className': 'Band',
            '__type': 'Pointer',
            'objectId': None,
        },
        '__type': 'Object',
        'title': 'Nightwish'
    }


def test_dump_save():
    album = Album()
    album.set('foo', 'bar')
    eq_(album._dump_save(), {'foo': 'bar'})


def test_extend():
    ok_(Object.extend('Album'))


def test_update_data():
    album = Album()
    album._update_data({'title': 'Once', 'artist': 'nightwish'})
    eq_(album._attributes, {'title': 'Once', 'artist': 'nightwish'})


def test_dump():
    album = Album()
    album.set('foo', 'bar')
    eq_(album.dump(), {'foo': 'bar'})


def test_to_pointer():
    album = Album()
    album.set('foo', 'bar')
    album._to_pointer()


@with_setup(setup_func)
def test_fetch():
    album = Album(title='Once')
    band = Band(name='Nightwish')
    album.set('parent', band)
    album.save()

    query = leancloud.Query(Album)
    album = query.get(album.id)
    assert album.get('parent').get('name') is None

    album.get('parent').fetch()
    assert album.get('parent').get('name') == 'Nightwish'

    album.destroy()
    band.destroy()


def test_has():
    album = Album()
    album.set('foo', 'bar')
    assert album.has('foo') is True
    assert album.has('bar') is False


def test_get_set_acl():
    acl = leancloud.ACL()
    album = Album()
    album.set_acl(acl)
    assert album.get_acl() == acl


def test_invalid_acl():
    album = Album()
    assert_raises(TypeError, album.set, 'ACL', 1)
    assert_raises(TypeError, album.set_acl, 1)


@with_setup(setup_func)
def test_relation():
    album = Album()
    band = Band()
    band.save()
    album.relation('band')
    relation = album.relation('band')
    relation.add(band)
    album.save()


@with_setup(setup_func)
def test_pointer():
    user = leancloud.User.create_without_data('555ed132e4b032867865884e')
    score = leancloud.Object.extend('score')
    s = score()
    s.set('user', user)
    s.save()


@with_setup(setup_func)
def test_save_and_destroy_all():
    ObjToDelete = Object.extend('ObjToDelete')
    objs = [ObjToDelete() for _ in range(3)]
    Object.save_all(objs)
    assert all(not x.is_new() for x in objs)

    Object.destroy_all(objs)

    for obj in objs:
        try:
            leancloud.Query(ObjToDelete).get(obj.id)
        except leancloud.LeanCloudError as e:
            assert e.code == 101


@with_setup(setup_func)
def test_fetch_when_save():
    Foo = Object.extend('Foo')
    foo = Foo()
    foo.fetch_when_save = True
    foo.set('counter', 1)
    foo.save()
    assert foo.get('counter') == 1

    foo_from_other_thread = leancloud.Query(Foo).get(foo.id)
    assert foo_from_other_thread.get('counter') == 1
    foo_from_other_thread.set('counter', 100)
    foo_from_other_thread.save()

    foo.increment('counter', 3)
    foo.save()
    eq_(foo.get('counter'), 103)
    foo.destroy()


@with_setup(setup_func)
def test_save_with_where():
    Foo = Object.extend('Foo')
    foo = Foo(aNumber=1)

    assert_raises(TypeError, foo.save, where=Foo.query)

    assert_raises(TypeError, foo.save, where=leancloud.Query('SomeClassNotEqualToFoo'))

    foo.save()

    foo.set('aNumber', 2)

    try:
        foo.save(where=leancloud.Query('Foo').equal_to('aNumber', 2))
    except leancloud.LeanCloudError as e:
        assert e.code == 305

    foo.save(where=leancloud.Query('Foo').equal_to('aNumber', 1))
    assert leancloud.Query('Foo').get(foo.id).get('aNumber') == 2

@with_setup(setup_func)
def save_object():
    album = Album()
    band = Band()
    album.set('b', band)
    album.set('c', None)
    album.save()

def test_setting_None():
    album = Album()
    album.set('roker', None)
    eq_(album._changes.get('roker', 'no_key'), 'no_key')
