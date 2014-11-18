# coding: utf-8

from nose.tools import ok_

from leancloud import AVObject
from leancloud.fields import AnyField

__author__ = 'asaka <lan@leancloud.rocks>'


def test_extend():
    ok_(AVObject.extend('Album'))


def test_class_extend():
    class Album(AVObject):
        title = AnyField()


def test_set():
    Album = AVObject.extend('Album')
    album = Album()
    album.set('title', 'Once')


def test_get():
    pass
