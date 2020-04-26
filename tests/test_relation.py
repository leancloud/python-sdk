# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from nose.tools import with_setup

import leancloud
from leancloud import Object
from leancloud import Relation

__author__ = "asaka <lan@leancloud.rocks>"


def setup_func():
    leancloud.init(os.environ["APP_ID"], os.environ["APP_KEY"])


class Band(Object):
    pass


class Album(Object):
    pass


def test_create_relation():  # type: () -> None
    album = Album()
    r = Relation(album, "band")
    assert r


@with_setup(setup_func)
def test_query_relation():  # type: () -> None
    album = Album(title="variety")
    band1 = Band(name="xxx")
    band1.save()
    band2 = Band(name="ooo")
    band2.save()

    relation = album.relation("band")
    relation.add(band1)
    relation.add(band2)
    album.save()

    album = leancloud.Query("Album").get(album.id)
    relation = album.relation("band")
    bands = relation.query.find()
    assert band1.id in [x.id for x in bands]
    assert band2.id in [x.id for x in bands]

    bands = relation.query.find()
    assert band1.id in [x.id for x in bands]
    assert band2.id in [x.id for x in bands]

    album.destroy()
    band1.destroy()
    band2.destroy()
