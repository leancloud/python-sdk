# coding: utf-8
from datetime import datetime
import os

from nose.tools import eq_
from nose.tools import with_setup

import leancloud
from leancloud import Query
from leancloud import Object
from leancloud import GeoPoint

__author__ = 'asaka <lan@leancloud.rocks>'


class GameScore(Object):
    pass

number = Object.extend('number')

game_scores = []


def setup_func():
    leancloud.init(
        os.environ['APP_ID'],
        os.environ['APP_KEY']
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
        game_score.set('location', GeoPoint(latitude=i, longitude=-i))
        game_score.save()
        game_scores.append(game_score)

    global n1
    n1 = number()
    n1.set('num', 1)
    n1.save()


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
def test_skip():
    q = Query(GameScore)
    q.skip(5)
    assert q._skip == 5


def test_limit():
    q = Query(GameScore)
    q.limit(121)
    assert q._limit == 121


@with_setup(setup_func)
def test_cloud_query():
    q = Query(GameScore)
    result = q.do_cloud_query('select count(*), * from GameScore where score<11')
#     results = result.results
#     assert all(obj in game_scores for obj in results)
#     assert all(obj in results for obj in game_scores)
    assert result.count == 10
    assert result.class_name == 'GameScore'


@with_setup(setup_func)
def test_or():
    q1 = Query(GameScore).greater_than('score', -1)
    q2 = Query(GameScore).equal_to('name', 'x')
    result = Query.or_(q1, q2).ascending('score').find()
    eq_([i.get('score') for i in result], range(10))


@with_setup(setup_func)
def test_and():
    q1 = Query(GameScore).greater_than('score', 2)
    q2 = Query(GameScore).greater_than('score', 3)
    result = Query.and_(q1, q2).ascending('score').find()
    eq_([i.get('score') for i in result], range(4, 10))


# @with_setup(setup_func)
# def test_dump():
#     q = Query(GameScore)


@with_setup(setup_func)
def not_equal_to():
    q = Query(GameScore)
    assert q.not_equal_to('playerName', '李四')


@with_setup(setup_func)
def test_contains_all():
    q = Query(GameScore).contains_all('score', [5])
    result = q.find()
    eq_([i.get('score') for i in result], [5])


@with_setup(setup_func)
def test_does_not_exists():
    q = Query(GameScore).does_not_exists('oops')
    assert q.find()


# @with_setup(setup_func)
# def test_does_not_match_query():
#     q = Query(GameScore)


# @with_setup(setup_func)
# def test_match_key_in_query():
#     q = Query(GameScore)
#     number_query = Query(number)
#     result = q.matched_key_in_query('score', 'number', number_query).find()
#     eq_(result.get('score'), 1)
#
#
# @with_setup(setup_func)
# def test_does_not_match_key_in_query():
#     q = Query(GameScore)
#     number_query = Query(number)
#     result = q.matched_key_in_query('score', 'number', number_query).find()
#     eq_(len(result), 9)

@with_setup(setup_func)
def test_contains():
    q = Query(GameScore).contains('playerName', '三')
    eq_(len(q.find()), 10)


@with_setup(setup_func)
def test_startswith():
    q = Query(GameScore).startswith('playerName', '张')
    eq_(len(q.find()), 10)


@with_setup(setup_func)
def test_endswith():
    q = Query(GameScore).endswith('playerName', '三')
    eq_(len(q.find()), 10)


@with_setup(setup_func)
def test_add_ascending():
    result = Query(GameScore).add_ascending('score').find()
    eq_([i.get('score') for i in result], range(10))


@with_setup(setup_func)
def test_near():
    result = Query(GameScore).near('location', GeoPoint(latitude=0, longitude=0)).find()
    eq_([i.get('score') for i in result], range(10))


@with_setup(setup_func)
def test_within_radians():
    result = Query(GameScore).within_radians('location', GeoPoint(latitude=0, longitude=0), 1).find()
    eq_([i.get('score') for i in result], range(10))


@with_setup(setup_func)
def test_within_miles():
    result = Query(GameScore).within_miles('location', GeoPoint(latitude=0, longitude=0), 4000).find()
    eq_([i.get('score') for i in result], range(10))


# to_check
@with_setup(setup_func)
def test_within_geobox():
    result = Query(GameScore).within_geo_box('location', (0, 0), (11, 11)).find()
    eq_([i.get('score') for i in result], [0])


@with_setup(setup_func)
def test_select():
    result = Query(GameScore).select('score', 'playerName').find()
    eq_(len(result), 10)


@with_setup(setup_func)
def test_pointer_query():
    foo = Object.create('Foo')
    bar = Object.create('Bar')
    bar.save()
    foo.set('bar', bar)
    foo.save()

    q = Query('Foo').equal_to('bar', bar)
    assert len(q.find()) == 1


# TODO add more tests
    inner_query = leancloud.Query('Post')
    inner_query.exists("image")
    query = leancloud.Query('Comment')
    query.matches_query("post", inner_query)
    assert query.dump() == {'where': {'post': {'$inQuery': {'className': 'Post', 'where': {'image': {'$exists': True}}}}}}


# @with_setup(setup_func)
# def test_destroy_all():
#     result = Query(GameScore).destroy_all()
#     eq_(result.status_code, 200)

# TODO
# def test_FriendshipQuery():
