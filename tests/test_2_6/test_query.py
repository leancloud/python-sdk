# coding: utf-8

from datetime import datetime

from nose.tools import eq_
from nose.tools import with_setup

import leancloud
from leancloud import Query
from leancloud import Object

__author__ = 'asaka <lan@leancloud.rocks>'


class GameScore(Object):
    pass


game_scores = []


def setup_func():
    leancloud.init(
        'pgk9e8orv8l9coak1rjht1avt2f4o9kptb0au0by5vbk9upb',
        'hi4jsm62kok2qz2w2qphzryo564rzsrucl2czb0hn6ogwwnd',
    )

    olds = Query(GameScore).find()
    for old in olds:
        old.destroy()

    global game_scores
    game_scores = []
    for i in xrange(10):
        game_score = GameScore()
        game_score.set('score', i)
        game_score.set('playerName', '张三')
        game_score.save()
        game_scores.append(game_score)


def destroy_func():
    pass
    # albums = Query(GameScore).find()
    # for album in albums:
    #     album.delete()


@with_setup(setup_func, destroy_func)
def test_save():
    assert game_scores[0].id


@with_setup(setup_func, destroy_func)
def test_save_date():
    DateObject = Object.extend('DateObject')
    now = datetime.now()

    d = DateObject(date=now)
    d.save()
    server_date = Query(DateObject).get(d.id).get('date')
    assert now.isoformat().split('.')[0] == server_date.isoformat().split('.')[0]


def test_batch():
    foo = Object.create('Foo')
    bar = Object.create('Bar')
    bar.set('baz', 'baz')
    foo.set('bar', bar)
    bar.save()
    foo.save()
    # TODO: check if relation is corrected


@with_setup(setup_func, destroy_func)
def test_relation():
    foo = Object.extend('Foo')()
    foo.set('a', 1)
    bar = Object.extend('Bar')()
    bar.set('baz', 'baz')
    bar.save()
    relation = foo.relation('list')
    relation.add(bar)
    foo.save()


@with_setup(setup_func, destroy_func)
def test_basic_query():
    # find
    q = Query(GameScore)
    results = q.find()
    eq_(len(results), 10)

    # first
    q = Query(GameScore)
    game_score = q.first()
    assert game_score

    # get
    q = Query(GameScore)
    local_game_score = game_scores[0]
    q.get(local_game_score.id)

    # count
    q = Query(GameScore)
    eq_(q.count(), 10)

    # descending
    q = Query(GameScore).descending('score')
    eq_([x.get('score') for x in q.find()], range(9, -1, -1))

    # greater_than
    q = Query(GameScore).greater_than('score', 5).ascending('score')
    eq_([x.get('score') for x in q.find()], range(6, 10))

    q = Query(GameScore).greater_than_or_equal_to('score', 5).ascending('score')
    eq_([x.get('score') for x in q.find()], range(5, 10))

    q = Query(GameScore).less_than('score', 5).ascending('score')
    eq_([x.get('score') for x in q.find()], range(0, 5))

    q = Query(GameScore).less_than_or_equal_to('score', 5).ascending('score')
    eq_([x.get('score') for x in q.find()], range(0, 6))

    q = Query(GameScore).contained_in('score', [1, 2, 3]).ascending('score')
    eq_([x.get('score') for x in q.find()], range(1, 4))

    q = Query(GameScore).not_contained_in('score', [0, 1, 2, 3]).ascending('score')
    eq_([x.get('score') for x in q.find()], range(4, 10))

    q = Query(GameScore).select('score')
    assert not q.find()[0].has('playerName')


@with_setup(setup_func)
def test_pointer_query():
    foo = Object.create('Foo')
    bar = Object.create('Bar')
    bar.save()
    foo.set('bar', bar)
    foo.save()

    q = Query('Foo').equal_to('bar', bar)
    assert len(q.find()) == 1


def test_matches_query():
    inner_query = leancloud.Query('Post')
    inner_query.exists("image")
    query = leancloud.Query('Comment')
    query.matches_query("post", inner_query)
    assert query.dump() == {'where': {'post': {'$inQuery': {'className': 'Post', 'where': {'image': {'$exists': True}}}}}}
