# coding: utf-8

from nose.tools import eq_
from nose.tools import with_setup

import leancloud
from leancloud import AVQuery
from leancloud import AVObject

__author__ = 'asaka <lan@leancloud.rocks>'


class Album(AVObject):
    pass


def setup_func():
    leancloud.init(
        'pgk9e8orv8l9coak1rjht1avt2f4o9kptb0au0by5vbk9upb',
        'hi4jsm62kok2qz2w2qphzryo564rzsrucl2czb0hn6ogwwnd',
    )


@with_setup(setup_func)
def test_basic():
    pass


@with_setup(setup_func)
def test_count():
    q = Query(Album)
    eq_(q.count(), 7)