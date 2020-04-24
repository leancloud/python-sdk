# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from nose.tools import raises  # type: ignore

from leancloud import acl
from leancloud import role
from leancloud import user


def test_dump():  # type: () -> None
    user_acl = acl.ACL()
    assert user_acl.dump() == {}


def test_set_access():  # type: () -> None
    user_acl = acl.ACL()
    user_acl._set_access("read", "520", False)
    user_acl.set_read_access("520", True)
    user_acl._set_access("read", "520", False)
    assert user_acl.permissions_by_id.get("read", "Not Exist") == "Not Exist"


def test_get_access():  # type: () -> None
    user_acl = acl.ACL()
    assert user_acl._get_access("read", "520") is False


def test_set_and_get_read_access():  # type: () -> None
    user_acl = acl.ACL()
    user_acl.set_read_access("520", True)
    assert user_acl.permissions_by_id["520"]["read"]
    assert user_acl.get_read_access("520")

    user_acl = acl.ACL()
    test_user = user.User()
    test_user.id = "520"
    user_acl.set_read_access(test_user, True)
    assert user_acl.get_read_access(test_user)

    role_acl = acl.ACL()
    test_role = role.Role("520", role_acl)
    role_acl.set_read_access(test_role, True)
    assert role_acl.get_read_access(test_role)


def test_set_and_get_write_access():  # type: () -> None
    user_acl = acl.ACL()
    user_acl.set_write_access("520", True)
    assert user_acl.permissions_by_id["520"]["write"]
    assert user_acl.get_write_access("520")


def test_set_and_get_public_read_access():  # type: () -> None
    user_acl = acl.ACL()
    user_acl.set_public_read_access(True)
    assert user_acl.permissions_by_id["*"]["read"]
    assert user_acl.get_public_read_access()
    user_acl.set_public_read_access(False)
    assert not user_acl.permissions_by_id.get("*")
    assert not user_acl.get_public_read_access()


def test_set_and_get_public_write_access():  # type: () -> None
    user_acl = acl.ACL()
    user_acl.set_public_write_access(True)
    assert user_acl.permissions_by_id["*"]["write"]
    assert user_acl.get_public_write_access()


def test_first_set_read_ture_and_then_write_false():  # type: () -> None
    user_acl = acl.ACL()
    user_acl.set_read_access("520", True)
    user_acl.set_write_access("520", False)


def test_set_and_get_role_read_access():  # type: () -> None
    role_acl = acl.ACL()
    test_role = role.Role("520", role_acl)
    role_acl.set_role_read_access(test_role, True)
    assert role_acl.permissions_by_id["role:520"]["read"]
    assert role_acl.get_role_read_access(test_role)


@raises(TypeError)
def test_set_role_read_access_error():  # type: () -> None
    role_acl = acl.ACL()
    role_acl.set_role_read_access(510, True)  # type: ignore


@raises(TypeError)
def test_get_role_read_access_error():  # type: () -> None
    role_acl = acl.ACL()
    role_acl.get_role_read_access(510)  # type: ignore


def test_set_and_get_role_write_access():  # type: () -> None
    role_acl = acl.ACL()
    test_role = role.Role("520", role_acl)
    role_acl.set_role_write_access(test_role, True)
    assert role_acl.permissions_by_id["role:520"]["write"]
    assert role_acl.get_role_write_access(test_role)


@raises(TypeError)
def test_set_get_role_write_access_error():  # type: () -> None
    role_acl = acl.ACL()
    role_acl.set_role_write_access(510, True)  # type: ignore


@raises(TypeError)
def test_get_role_write_access_error():  # type: () -> None
    role_acl = acl.ACL()
    role_acl.get_role_write_access(510)  # type: ignore
