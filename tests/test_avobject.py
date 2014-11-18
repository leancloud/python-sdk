# coding: utf-8

from nose.tools import with_setup
from nose.tools import ok_

import leancloud
from leancloud import AVObject
from leancloud.fields import AnyField

__author__ = 'asaka <lan@leancloud.rocks>'


def setup_func():
    leancloud.init(
        'pgk9e8orv8l9coak1rjht1avt2f4o9kptb0au0by5vbk9upb',
        'hi4jsm62kok2qz2w2qphzryo564rzsrucl2czb0hn6ogwwnd',
    )


def test_extend():
    ok_(AVObject.extend('Album'))


def test_class_extend():
    class Album(AVObject):
        title = AnyField()

    assert 'title' in Album._fields


def test_set():
    Album = AVObject.extend('Album')
    album = Album()
    album.set('title', 'Once')
    assert album.title == 'Once'
    assert 'title' in Album._fields


def test_get():
    Album = AVObject.extend('Album')
    album = Album()
    album.set('title', 'Once')

    assert album.get('title') == 'Once'


@with_setup(setup_func)
def test_save():
    Album = AVObject.extend('Album')
    album = Album()
    album.set('title', 'Once')

    album.save()
