# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from datetime import datetime

from dateutil import tz
from nose.tools import assert_equal  # type: ignore
from nose.tools import assert_raises  # type: ignore
from nose.tools import eq_  # type: ignore
from nose.tools import ok_  # type: ignore
from nose.tools import with_setup  # type: ignore

import leancloud
from leancloud import Object
from leancloud import Query

__author__ = "asaka <lan@leancloud.rocks>"


def setup_func():
    leancloud.client.USE_MASTER_KEY = None
    leancloud.client.APP_ID = None
    leancloud.client.APP_KEY = None
    leancloud.client.MASTER_KEY = None
    leancloud.init(os.environ["APP_ID"], os.environ["APP_KEY"])


class Album(Object):
    pass


class Band(Object):
    pass


def test_new():  # type: () -> None
    album = Album()
    assert album._class_name == "Album"


def test_class_equal():  # type: () -> None
    AnotherAlbum = Object.extend("Album")
    assert AnotherAlbum is Album
    album = AnotherAlbum()
    assert isinstance(album, AnotherAlbum)


def test_dirty():  # type: () -> None
    album = Album()
    assert album.is_dirty() is True
    album.id = "123"
    assert album.is_dirty() is False
    album.set("foo", "bar")
    assert album.is_dirty() is True


def test_find_unsaved_children():  # type: ignore
    album = Album()
    unsaved_children = []
    unsaved_files = []
    Object._find_unsaved_children(album, unsaved_children, unsaved_files)
    assert unsaved_children == [album]
    assert unsaved_files == []


def test_find_unsaved_children_2():  # type: ignore
    album = Album()
    band = Band()
    album.set("band", band)
    unsaved_children = []
    unsaved_files = []
    Object._find_unsaved_children(album, unsaved_children, unsaved_files)
    assert unsaved_children == [band, album]


def test_set():  # type: () -> None
    album = Album()
    album.set("title", "Nightwish")
    eq_(album._attributes, {"title": "Nightwish"})

    album = Album(title="Nightwish")
    eq_(album._attributes, {"title": "Nightwish"})


def test_get():  # type: () -> None
    album = Album()
    album.set("foo", "bar")
    assert album.get("foo") == "bar"


def test_get_default():  # type: () -> None
    album = Album()
    assert album.get("foo", "bar") == "bar"
    assert album.get("foo", default="bar") == "bar"
    # for backward compatibility
    assert album.get("foo", deafult="bar") == "bar"
    assert album.get("foo", "bar", deafult="foobar") == "bar"
    assert album.get("foo", deafult="foobar", default="bar") == "bar"


def test_unset():  # type: () -> None
    album = Album()
    album.set("foo", "bar")
    album.unset("foo")
    assert album.get("foo") is None
    assert album.has("foo") is False


def test_increment():  # type: () -> None
    album = Album()
    album.set("foo", 1)
    album.increment("foo", 1)
    assert album.get("foo") == 2


@with_setup(setup_func)
def test_bit_operation():  # type: () -> None
    album = Album()
    album.set("flags", 0b0)
    album.bit_and("flags", 0b1)
    assert_equal(album.get("flags"), 0b0)
    album.save()
    assert_equal(album.get("flags"), 0b0)

    album.bit_or("flags", 0b1)
    assert_equal(album.get("flags"), 0b1)
    album.save()
    assert_equal(album.get("flags"), 0b1)

    album.bit_xor("flags", 0b10)
    assert_equal(album.get("flags"), 0b11)
    album.save()
    assert_equal(album.get("flags"), 0b11)


@with_setup(setup_func)
def test_increment_atfer_save():  # type: () -> None
    album = Album()
    album.set("foo", 1)
    album.save()
    album.increment("foo", 234)
    assert album.get("foo") == 235
    album.save()
    assert album.get("foo") == 235


def test_add():  # type: () -> None
    album = Album()
    album.add("foo", 1)
    eq_(album.get("foo"), [1])
    album.add("foo", 2)
    eq_(album.get("foo"), [1, 2])


def test_add_unique():  # type: () -> None
    album = Album()
    album.add_unique("foo", 1)
    album.add_unique("foo", 1)
    eq_(album.get("foo"), [1])
    album.add_unique("foo", 2)
    eq_(album.get("foo"), [1, 2])


def test_remove():  # type: () -> None
    album = Album()
    album.set("foo", ["bar", "baz"])
    album.remove("foo", "bar")
    eq_(album.get("foo"), ["baz"])


def test_clear():  # type: () -> None
    album = Album(foo=1, bar=2, baz=3)
    album.clear()
    assert album.get("foo") is None
    assert album.get("bar") is None
    assert album.get("baz") is None


def test_full_dump():  # type: ignore
    album = Album()
    album.set("title", "Nightwish")
    assert album._dump() == {
        "className": "Album",
        "__type": "Object",
        "title": "Nightwish",
    }
    band = Band()
    album.set("band", band)
    assert album._dump() == {
        "className": "Album",
        "band": {"className": "Band", "__type": "Pointer", "objectId": None},
        "__type": "Object",
        "title": "Nightwish",
    }


def test_dump_save():  # type: ignore
    album = Album()
    album.set("foo", "bar")
    eq_(album._dump_save(), {"foo": "bar"})


def test_extend():  # type: () -> None
    ok_(Object.extend("Album"))


def test_update_data():  # type: ignore
    album = Album()
    album._update_data({"title": "Once", "artist": "nightwish"})
    eq_(album._attributes, {"title": "Once", "artist": "nightwish"})


def test_dump():  # type: () -> None
    album = Album()
    album.set("foo", "bar")
    eq_(album.dump(), {"foo": "bar"})


def test_to_pointer():  # type: ignore
    album = Album()
    album.set("foo", "bar")
    album._to_pointer()


@with_setup(setup_func)
def test_fetch():  # type: () -> None
    album = Album(title="Once")
    band = Band(name="Nightwish")
    album.set("parent", band)
    album.save()

    album_1 = Album.create_without_data(album.id)
    assert album_1.is_existed() is False
    album_1.fetch(include=["parent"], select=["name", "parent"])
    assert album_1.is_existed() is True
    assert album_1.get("parent").get("name") == "Nightwish"
    assert not album_1.has("title")

    album.destroy()
    band.destroy()


def test_has():  # type: () -> None
    album = Album()
    album.set("foo", "bar")
    assert album.has("foo") is True
    assert album.has("bar") is False


def test_existence():  # type: () -> None
    album = Album()
    assert album.is_existed() is False


def test_get_set_acl():  # type: () -> None
    acl = leancloud.ACL()
    album = Album()
    album.set_acl(acl)
    assert album.get_acl() == acl


def test_invalid_acl():  # type: () -> None
    album = Album()
    assert_raises(TypeError, album.set, "ACL", 1)
    assert_raises(TypeError, album.set_acl, 1)


@with_setup(setup_func)
def test_relation():  # type: () -> None
    album = Album()
    band = Band()
    band.save()
    album.relation("band")
    relation = album.relation("band")
    relation.add(band)
    album.save()


@with_setup(setup_func)
def test_pointer():  # type: () -> None
    user = leancloud.User.create_without_data("555ed132e4b032867865884e")
    score = leancloud.Object.extend("score")
    s = score()
    s.set("user", user)
    s.save()


@with_setup(setup_func)
def test_save_and_destroy_all():  # type: () -> None
    ObjToDelete = Object.extend("ObjToDelete")
    objs = [ObjToDelete() for _ in range(3)]
    already_saved_obj = ObjToDelete()
    already_saved_obj.save()
    objs.append(already_saved_obj)
    Object.save_all(objs)
    assert all(not x.is_new() for x in objs)

    Object.destroy_all(objs)

    for obj in objs:
        try:
            leancloud.Query(ObjToDelete).get(obj.id)
        except leancloud.LeanCloudError as e:
            assert e.code == 101


@with_setup(setup_func)
def test_fetch_when_save():  # type: () -> None
    Foo = Object.extend("Foo")
    foo = Foo()
    foo.set("counter", 1)
    foo.save()
    assert foo.created_at == foo.updated_at
    assert foo.get("counter") == 1

    foo_from_other_thread = leancloud.Query(Foo).get(foo.id)
    assert foo_from_other_thread.get("counter") == 1
    foo_from_other_thread.set("counter", 100)
    foo_from_other_thread.save()

    foo.increment("counter", 3)
    foo.save(fetch_when_save=True)
    eq_(foo.get("counter"), 103)
    foo.destroy()


@with_setup(setup_func)
def test_save_with_where():  # type: () -> None
    Foo = Object.extend("Foo")
    foo = Foo(aNumber=1)

    assert_raises(TypeError, foo.save, where=Foo.query)  # type: ignore

    assert_raises(TypeError, foo.save, where=leancloud.Query("SomeClassNotEqualToFoo"))

    foo.save()

    foo.set("aNumber", 2)

    try:
        foo.save(where=leancloud.Query("Foo").equal_to("aNumber", 2))
    except leancloud.LeanCloudError as e:
        assert e.code == 305

    foo.save(where=leancloud.Query("Foo").equal_to("aNumber", 1))
    assert leancloud.Query("Foo").get(foo.id).get("aNumber") == 2


@with_setup(setup_func)
def test_modify_class_name():  # type: () -> None
    class Philosopher(Object):
        class_name = "Teacher"

    @Object.as_class("Student")
    class Physicist(Object):
        pass

    plato = Philosopher()
    plato.save()
    aristotle = Physicist()
    aristotle.save()

    assert Query("Teacher").get(plato.id)
    assert Query("Student").get(aristotle.id)

    plato.destroy()
    aristotle.destroy()


@with_setup(setup_func)
def test_create_without_data():  # type: () -> None
    Foo = Object.extend("Foo")
    foo1 = Foo(aNumber=2)
    foo1.save()
    foo2 = Foo.create_without_data(foo1.id)
    foo2.set("aNumber", 3)
    foo2.save()
    assert foo1.id == foo2.id
    assert Foo.query.get(foo1.id).get("aNumber") == 3
    foo1.destroy()


@with_setup(setup_func)
def test_time_zone():
    TestTimeZone = Object.extend("TestTimeZone")
    now = datetime.now()
    obj = TestTimeZone()
    obj.set("date", now)
    obj.save()

    obj = TestTimeZone.query.get(obj.id)
    assert obj.created_at.tzinfo == tz.tzlocal()
    assert obj.updated_at.tzinfo == tz.tzlocal()
    assert obj.get("date").tzinfo == tz.tzlocal()

    obj.destroy()
