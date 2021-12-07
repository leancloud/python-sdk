# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import random
from datetime import datetime

from nose.tools import eq_
from nose.tools import assert_equal
from nose.tools import with_setup
from nose.tools import raises

import leancloud
from leancloud import Query
from leancloud import Object
from leancloud import GeoPoint
from leancloud.file_ import File

__author__ = "asaka <lan@leancloud.rocks>"


class GameScore(Object):
    pass


number = Object.extend("number")
A = Object.extend("A")
B = Object.extend("B")


# unmark the test to clean up the test data
# def test_data_cleanup():
#     olds = Query(GameScore).find()
#     for old in olds:
#         old.destroy()
#     old1 = q_a.find()
#     old2 = q_b.find()
#     for i in old1:
#         i.destroy()
#     for k in old2:
#            k.destroy()


def make_setup_func(use_master_key=False):
    def setup_func():
        leancloud.client.USE_MASTER_KEY = None
        leancloud.client.APP_ID = None
        leancloud.client.APP_KEY = None
        leancloud.client.MASTER_KEY = None
        if use_master_key:
            leancloud.init(os.environ["APP_ID"], master_key=os.environ["MASTER_KEY"])
        else:
            leancloud.init(os.environ["APP_ID"], os.environ["APP_KEY"])

        olds = Query(GameScore).find()
        # make sure the test data does not change, else re-initialize it
        if len(olds) == 10:
            pass
        else:
            for old in olds:
                old.destroy()

            for i in range(10):
                game_score = GameScore()
                game_score.set("score", i)
                game_score.set("playerName", "张三")
                game_score.set("location", GeoPoint(latitude=i, longitude=-i))
                game_score.set("random", random.randrange(100))
                f = File("Blah.txt", open("tests/sample_text.txt", "rb"))
                f.save()
                game_score.set("attachment", f)
                game_score.save()

    return setup_func


def match_key_setup():
    q_a = Query(A)
    q_b = Query(B)

    if q_a.count() == 50 and q_b.count() == 50:
        pass
    else:
        old1 = q_a.find()
        old2 = q_b.find()
        for i in old1:
            i.destroy()
        for k in old2:
            k.destroy()

        for _i in range(5):
            for k in range(10):
                a = A()
                a.set("age", k)
                a.save()
                b = B()
                b.set("work_year", k)
                b.save()


def destroy_func():
    pass
    # albums = Query(GameScore).find()
    # for album in albums:
    #     album.delete()


@raises(ValueError)
def test_query_error():  # type: () -> None
    Query(123)  # type: ignore


# @with_setup(make_setup_func(), destroy_func)
# def test_save():
#     assert game_scores[0].id


@with_setup(make_setup_func(), destroy_func)
def test_save_date():  # type: () -> None
    DateObject = Object.extend("DateObject")
    now = datetime.now()

    d = DateObject(date=now)
    d.save()
    server_date = Query(DateObject).get(d.id).get("date")
    assert now.isoformat().split(".")[0] == server_date.isoformat().split(".")[0]


def test_batch():  # type: () -> None
    foo = Object.create("Foo")
    bar = Object.create("Bar")
    bar.set("baz", "baz")
    foo.set("bar", bar)
    bar.save()
    foo.save()
    # TODO: check if relation is corrected


@with_setup(make_setup_func(), destroy_func)
def test_relation():  # type: () -> None
    foo = Object.extend("Foo")()
    foo.set("a", 1)
    bar = Object.extend("Bar")()
    bar.set("baz", "baz")
    bar.save()
    relation = foo.relation("list")
    relation.add(bar)
    foo.save()


@with_setup(make_setup_func(), destroy_func)
def test_basic_query():  # type: () -> None
    # find
    results = GameScore.query.find()  # type:ignore
    eq_(len(results), 10)

    # first
    game_score = GameScore.query.first()
    assert game_score
    assert game_score.get("objectId")

    assert isinstance(game_score.get("createdAt"), datetime)
    assert isinstance(game_score.get("updatedAt"), datetime)

    # get
    GameScore.query.get(game_score.id)

    # get nonexist
    assert GameScore.query.get("NonexistentID").is_existed() is False

    # count
    eq_(GameScore.query.count(), 10)

    # descending and add_descending
    q = Query(GameScore).add_descending("score").descending("score")
    eq_([x.get("score") for x in q.find()], list(range(9, -1, -1)))

    # greater_than
    q = Query(GameScore).greater_than("score", 5).ascending("score")
    eq_([x.get("score") for x in q.find()], list(range(6, 10)))

    q = Query(GameScore).greater_than_or_equal_to("score", 5).ascending("score")
    eq_([x.get("score") for x in q.find()], list(range(5, 10)))

    q = Query(GameScore).less_than("score", 5).ascending("score")
    eq_([x.get("score") for x in q.find()], list(range(0, 5)))

    q = Query(GameScore).less_than_or_equal_to("score", 5).ascending("score")
    eq_([x.get("score") for x in q.find()], list(range(0, 6)))

    q = Query(GameScore).contained_in("score", [1, 2, 3]).ascending("score")
    eq_([x.get("score") for x in q.find()], list(range(1, 4)))

    q = Query(GameScore).not_contained_in("score", [0, 1, 2, 3]).ascending("score")
    eq_([x.get("score") for x in q.find()], list(range(4, 10)))

    q = Query(GameScore).select(["score"])
    assert not q.find()[0].has("playerName")


def test_or_and_query():  # type: () -> None
    q1 = Query(GameScore).greater_than("score", 5)
    q2 = Query(GameScore).less_than("score", 10)
    q3 = Query(GameScore).equal_to("playerName", "foobar")

    q = Query.and_(q1, q2, q3)
    assert q.dump() == {
        "where": {
            "$and": [
                {"score": {"$gt": 5}},
                {"score": {"$lt": 10}},
                {"playerName": "foobar"},
            ]
        }
    }

    q = Query.or_(q1, q2, q3)
    assert q.dump() == {
        "where": {
            "$or": [
                {"score": {"$gt": 5}},
                {"score": {"$lt": 10}},
                {"playerName": "foobar"},
            ]
        }
    }


@with_setup(make_setup_func())
def test_query_acl():  # type: () -> None
    TestACLObject = leancloud.Object.extend("TestACLObject")
    o = TestACLObject(content="xxx")
    acl = leancloud.ACL()
    acl.set_public_read_access(True)
    acl.set_public_write_access(True)
    acl.set_write_access("xxxxx", True)
    o.set_acl(acl)
    o.save()
    acl_data = o.get_acl().dump()
    o = TestACLObject.query.include_acl().equal_to("objectId", o.id).first()
    assert_equal(acl_data, o.get_acl().dump())
    o.destroy()


@with_setup(make_setup_func())
def test_multiple_order():  # type: () -> None
    MultipleOrderObject = leancloud.Object.extend("MultipleOrderObject")
    for obj in Query(MultipleOrderObject).find():
        obj.destroy()
    MultipleOrderObject(a=1, b=10).save()
    MultipleOrderObject(a=10, b=20).save()
    MultipleOrderObject(a=1, b=3).save()
    q = Query(MultipleOrderObject)
    q.add_descending("a")
    q.add_descending("b")
    r = q.find()
    for i in range(1, len(r)):
        assert r[i - 1].get("a") >= r[i].get("a")
        assert r[i - 1].get("b") >= r[i].get("b")


@raises(ValueError)
def test_or_erorr():  # type: () -> None
    Query(GameScore).or_("score")  # type: ignore


@with_setup(make_setup_func())
def test_skip():  # type: () -> None
    q = Query(GameScore)
    q.skip(5)
    assert q._skip == 5


@with_setup(make_setup_func())
def test_size_equal_to():  # type: () -> None
    TestClass = leancloud.Object.extend("TestSizeEqualTo")
    obj1 = TestClass(a=[1, 2, 3])
    obj1.save()
    obj2 = TestClass(a=[1, 2, 3, 4, 5])
    obj2.save()
    result = Query(TestClass).size_equal_to("a", 3).find()
    assert len(result) == 1
    assert result[0].id == obj1.id
    obj1.destroy()
    obj2.destroy()


def test_limit():  # type: () -> None
    q = Query(GameScore)
    q.limit(121)
    assert q._limit == 121


@raises(ValueError)
def test_limit_error():  # type: () -> None
    Query(GameScore).limit(1001)


@with_setup(make_setup_func())
def test_cloud_query():  # type: () -> None
    q = Query(GameScore)
    result = q.do_cloud_query(
        "select count(*), * from GameScore where score<11", ["score"]
    )
    assert result.count == 10
    assert result.class_name == "GameScore"


@with_setup(make_setup_func())
def test_or_():  # type: () -> None
    q1 = Query(GameScore).greater_than("score", -1)
    q2 = Query(GameScore).equal_to("name", "x")
    result = Query.or_(q1, q2).ascending("score").find()
    eq_([i.get("score") for i in result], list(range(10)))


@with_setup(make_setup_func())
def test_and_():  # type: () -> None
    q1 = Query(GameScore).greater_than("score", 2)
    q2 = Query(GameScore).greater_than("score", 3)
    result = Query.and_(q1, q2).ascending("score").find()
    eq_([i.get("score") for i in result], list(range(4, 10)))


@raises(ValueError)
def test_and_error():  # type: () -> None
    Query(GameScore).and_("score")  # type: ignore


# @with_setup(make_setup_func())
# def test_dump():
#     q = Query(GameScore)


@with_setup(make_setup_func())
def test_not_equal_to():  # type: () -> None
    result = Query(GameScore).not_equal_to("playerName", "李四").find()
    assert len(result) == 10


@with_setup(make_setup_func())
def test_contains_all():  # type: () -> None
    q = Query(GameScore).contains_all("score", [5])
    result = q.find()
    eq_([i.get("score") for i in result], [5])


@with_setup(make_setup_func())
def test_exist_and_does_not_exists():  # type: () -> None
    assert Query(GameScore).does_not_exist("oops").find()
    result = Query(GameScore).exists("playerName").find()
    assert len(result) == 10


@with_setup(make_setup_func())
def test_exist_and_does_not_exist():
    assert Query(GameScore).does_not_exist("oops").find()
    result = Query(GameScore).exists("playerName").find()
    assert len(result) == 10


@raises(TypeError)
def test_matched_error():  # type: () -> None
    Query(GameScore).matched("score", 1)  # type: ignore


@with_setup(make_setup_func())
def test_matched():  # type: () -> None
    result = (
        Query(GameScore)
        .matched("playerName", "^张", ignore_case=True, multi_line=True)
        .find()
    )
    assert len(result) == 10


@with_setup(make_setup_func())
def test_does_not_match_query():  # type: () -> None
    q = Query(GameScore).greater_than("score", -1)
    result = Query(GameScore).does_not_match_query("playerName", q).find()
    assert len(result) == 10


@with_setup(make_setup_func(), match_key_setup)
def test_matches_key_in_query():  # type: () -> None
    q1 = Query(A).equal_to("age", 1)
    q2 = Query(B)
    result = q2.matches_key_in_query("work_year", "age", q1).find()
    assert len(result) == 5


@with_setup(make_setup_func(), match_key_setup)
def test_does_not_match_key_in_query():  # type: () -> None
    q1 = Query(A).equal_to("age", 1)
    q2 = Query(B)
    result = q2.does_not_match_key_in_query("work_year", "age", q1).find()
    assert len(result) == 45


@with_setup(make_setup_func())
def test_contains():  # type: () -> None
    q = Query(GameScore).contains("playerName", "三")
    eq_(len(q.find()), 10)


@with_setup(make_setup_func())
def test_startswith():  # type: () -> None
    q = Query(GameScore).startswith("playerName", "张")
    eq_(len(q.find()), 10)


@with_setup(make_setup_func())
def test_endswith():  # type: () -> None
    q = Query(GameScore).endswith("playerName", "三")
    eq_(len(q.find()), 10)


@with_setup(make_setup_func())
def test_add_ascending():  # type: () -> None
    result = Query(GameScore).add_ascending("score").find()
    eq_([i.get("score") for i in result], list(range(10)))


@with_setup(make_setup_func())
def test_near():  # type: () -> None
    result = Query(GameScore).near("location", GeoPoint(latitude=0, longitude=0)).find()
    eq_([i.get("score") for i in result], list(range(10)))


@with_setup(make_setup_func())
def test_within_radians():  # type: () -> None
    result = (
        Query(GameScore)
        .within_radians("location", GeoPoint(latitude=0, longitude=0), 1)
        .find()
    )
    eq_([i.get("score") for i in result], list(range(10)))


@with_setup(make_setup_func())
def test_within_miles():  # type: () -> None
    result = (
        Query(GameScore)
        .within_miles("location", GeoPoint(latitude=0, longitude=0), 4000)
        .find()
    )
    eq_([i.get("score") for i in result], list(range(10)))


@with_setup(make_setup_func())
def test_within_kilometers():  # type: () -> None
    result = (
        Query(GameScore)
        .within_kilometers("location", GeoPoint(latitude=0, longitude=0), 4000)
        .find()
    )
    assert len(result) == 10


# to_check
@with_setup(make_setup_func())
def test_within_geobox():  # type: () -> None
    result = Query(GameScore).within_geo_box("location", (0, 0), (11, 11)).find()
    eq_([i.get("score") for i in result], [0])


@with_setup(make_setup_func())
def test_include():  # type: () -> None
    result = Query(GameScore).include(["score"]).find()
    assert len(result) == 10

@with_setup(make_setup_func())
def test_attachment():  # type: () -> None
    result = Query(GameScore).first()
    print(result.dump())
    attachment = result.get('attachment')
    assert attachment.url

@with_setup(make_setup_func())
def test_select():  # type: () -> None
    result = Query(GameScore).select(["score", "playerName"]).find()
    eq_(len(result), 10)


@with_setup(make_setup_func())
def test_pointer_query():  # type: () -> None
    foo = Object.create("Foo")
    bar = Object.create("Bar")
    bar.save()
    foo.set("bar", bar)
    foo.save()

    q = Query("Foo").equal_to("bar", bar)
    assert len(q.find()) == 1

    inner_query = leancloud.Query("Post")
    inner_query.exists("image")
    query = leancloud.Query("Comment")
    query.matches_query("post", inner_query)
    assert query.dump() == {
        "where": {
            "post": {
                "$inQuery": {"className": "Post", "where": {"image": {"$exists": True}}}
            }
        }
    }


@raises(ValueError)
def test_near_not_none():  # type: () -> None
    Query("test").near("oops", None)


@with_setup(make_setup_func())
def test_query_include_acl():
    with_acl = Query(GameScore).include_acl(True).first()
    assert with_acl.get_acl() is not None
    explicit_without_acl = Query(GameScore).include_acl(False).first()
    assert explicit_without_acl.get_acl() is None
    implicit_without_acl = Query(GameScore).first()
    assert implicit_without_acl.get_acl() is None


@with_setup(make_setup_func())
def test_save_with_query():
    Account = leancloud.Object.extend("Account")
    account = Account(balance=10)
    account.save()
    account.increment("balance", -100)
    try:
        account.save(where=Account.query.greater_than_or_equal_to("balance", 100))
    except leancloud.LeanCloudError as e:
        assert e.code == 305
    else:
        raise Exception("305 error not raised")
    account.destroy()


@with_setup(make_setup_func(use_master_key=True))
def test_scan():
    cursor = GameScore.query.scan(batch_size=2, scan_key="random")
    r = 0
    for i in cursor:
        assert r <= i.get("random")
        r = i.get("random")
