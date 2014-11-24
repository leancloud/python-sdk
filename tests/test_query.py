# coding: utf-8

from pprint import pprint

from nose.tools import eq_
from nose.tools import with_setup

import leancloud
from leancloud import AVQuery
from leancloud import AVObject

__author__ = 'asaka <lan@leancloud.rocks>'


class GameScore(AVObject):
    pass


game_scores = []


def setup_func():
    leancloud.init(
        'pgk9e8orv8l9coak1rjht1avt2f4o9kptb0au0by5vbk9upb',
        'hi4jsm62kok2qz2w2qphzryo564rzsrucl2czb0hn6ogwwnd',
    )

    albums = AVQuery(GameScore).find()
    for album in albums:
        album.delete()

    global game_scores
    game_scores = []
    for i in xrange(10):
        game_score = GameScore()
        game_score.set('score', i)
        game_score.save()
        game_scores.append(game_score)


def destroy_func():
    pass
    # albums = AVQuery(GameScore).find()
    # for album in albums:
    #     album.delete()


@with_setup(setup_func, destroy_func)
def test_find():
    q = AVQuery(GameScore)
    results = q.find()
    eq_(len(results), 10)


@with_setup(setup_func, destroy_func)
def test_first():
    q = AVQuery(GameScore)
    game_score = q.first()
    assert game_score


@with_setup(setup_func, destroy_func)
def test_get():
    q = AVQuery(GameScore)
    local_game_score = game_scores[0]
    q.get(local_game_score.id)


@with_setup(setup_func, destroy_func)
def test_count():
    q = AVQuery(GameScore)
    eq_(q.count(), 10)
