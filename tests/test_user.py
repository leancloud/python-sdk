# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import io
import random

from nose.tools import with_setup  # type: ignore

import leancloud
from leancloud import User
from leancloud import Query
from leancloud import File
from leancloud.errors import LeanCloudError

__author__ = "asaka <lan@leancloud.rocks>"


def only_init():
    leancloud.client.USE_MASTER_KEY = None
    leancloud.client.APP_ID = None
    leancloud.client.APP_KEY = None
    leancloud.client.MASTER_KEY = None
    leancloud.init(os.environ["APP_ID"], master_key=os.environ["MASTER_KEY"])


def get_setup_func(use_master_key=True):
    def setup_func():
        leancloud.client.USE_MASTER_KEY = None
        leancloud.client.APP_ID = None
        leancloud.client.APP_KEY = None
        leancloud.client.MASTER_KEY = None
        leancloud.init(
            os.environ["APP_ID"],
            app_key=os.environ["APP_KEY"],
            master_key=os.environ["MASTER_KEY"],
        )
        users = Query(User).find()
        for u in users:
            u.destroy()

        user1 = User()
        user1.set("username", "user1_name")
        user1.set("password", "password")
        user1.set_email("wow@leancloud.rocks")
        user1.set_mobile_phone_number("18611111111")
        user1.sign_up()
        user1.logout()

        user2 = User()
        user2.set("username", "user2_name")
        user2.set("password", "password")
        user2.sign_up()
        user2.logout()
        leancloud.client.use_master_key(use_master_key)

    return setup_func


def destroy_func():
    pass


@with_setup(only_init)
def test_sign_up():  # type: () -> None
    user = User()
    user.set("username", "foo")
    user.set("password", "bar")
    user.sign_up()
    assert user._session_token


@with_setup(only_init)
def test_sign_out():  # type: () -> None
    user = User()
    user.sign_up("Musen", "password")
    user.logout()
    assert not user.is_current


@with_setup(get_setup_func(), destroy_func)
def test_login():  # type: () -> None
    user = User()
    user.set("username", "user1_name")
    user.set("password", "password")
    user.login()

    user = User()
    user.login("user1_name", "password")


@with_setup(get_setup_func(), destroy_func)
def test_login_with_email():  # type: () -> None

    user = User()
    user.login(email="wow@leancloud.rocks", password="password")


@with_setup(get_setup_func(), destroy_func)
def test_file_field():  # type: () -> None
    user = User()
    user.login("user1_name", "password")
    user.set("xxxxx", File("xxx.txt", io.BytesIO(b"qqqqq")))
    user.save()

    q = Query(User)
    saved_user = q.get(user.id)
    assert isinstance(saved_user.get("xxxxx"), File)
    assert saved_user.get("xxxxx").name == "xxx.txt"


@with_setup(get_setup_func())
def test_follow():  # type: () -> None
    user1 = User()
    user1.set("username", "user1_name")
    user1.set("password", "password")
    user1.login()

    user2 = User()
    user2.set("username", "user2_name")
    user2.set("password", "password")
    user2.login()

    user1.follow(user2.id)


@with_setup(get_setup_func())
def test_follower_query():  # type: () -> None
    user1 = User()
    user1.login("user1_name", "password")
    user2 = User()
    user2.login("user2_name", "password")
    user2.follow(user1.id)
    query = User.create_follower_query(user1.id)
    assert query.first().id == user2.id


def test_followee_query():  # type: () -> None
    query = User.create_followee_query("1")
    assert query._friendship_tag == "followee"
    assert query.dump() == {
        "where": {
            "user": {"__type": "Pointer", "className": "_User", "objectId": "1"},
        },
    }


@with_setup(get_setup_func())
def test_current_user():  # type: () -> None
    user = User()
    user.login("user1_name", "password")
    assert user.is_current
    assert User.get_current().id == user.id


@with_setup(get_setup_func(use_master_key=False))
def test_update_user():  # type: () -> None
    user = User()
    user.login("user1_name", "password")
    user.set("nickname", "test_name")
    user.save()


@with_setup(get_setup_func())
def test_user_become():  # type: () -> None
    existed_user = User()
    existed_user.login("user1_name", "password")
    session_token = existed_user.session_token
    user = User.become(session_token)
    assert user.get("username") == existed_user.get("username")


@with_setup(get_setup_func())
def test_login_with():  # type: () -> None
    data = {"uid": "1", "access_token": "xxx"}
    User.login_with("xxx", data)


@with_setup(get_setup_func())
def test_unlink_from():  # type: () -> None
    data = {"uid": "1", "access_token": "xxx"}
    user = User.login_with("xxx", data)
    user.unlink_from("xxx")


@with_setup(get_setup_func())
def test_is_linked():  # type: () -> None
    data = {"uid": "1", "access_token": "xxx"}
    user = User.login_with("xxx", data)
    assert user.is_linked("xxx")


@with_setup(get_setup_func())
def test_signup_or_login_with_mobile_phone():  # type: () -> None
    try:
        User.signup_or_login_with_mobile_phone("18611111111", "111111")
    except LeanCloudError as e:
        assert e.code == 603


@with_setup(get_setup_func())
def test_update_password():  # type: () -> None
    user = User()
    user.login("user1_name", "password")
    user.update_password("password", "new_password")
    user.login("user1_name", "new_password")


@with_setup(get_setup_func())
def test_get_methods():  # type: () -> None
    user = User()
    user.login("user1_name", "password")

    user.set_username("new_user1")
    assert user.get_username() == "new_user1"

    user.set_mobile_phone_number("18611111111x")
    assert user.get_mobile_phone_number() == "18611111111x"

    user.set_password("new_password")
    assert user._attributes.get("password") == "new_password"

    user.set_email("wow1@leancloud.rocks")
    assert user.get_email() == "wow1@leancloud.rocks"


@with_setup(get_setup_func())
def test_get_roles():  # type: () -> None
    role = leancloud.Role("xxx")
    role.save()

    user = User()
    user.login("user1_name", "password")
    role.get_users().add(user)
    role.save()
    bind_roles = user.get_roles()
    assert len(bind_roles) == 1
    assert bind_roles[0].get("name") == "xxx"

    role.destroy()


@with_setup(get_setup_func())
def test_request_password_reset():  # type: () -> None
    try:
        User.request_password_reset("wow@leancloud.rocks")
    except LeanCloudError as e:
        assert u"请不要往同一个邮件地址发送太多邮件。" in e.error or "Too many emails" in str(e)


@with_setup(get_setup_func())
def test_request_email_verify():  # type: () -> None
    try:
        User.request_email_verify("wow@leancloud.rocks")
    except LeanCloudError as e:
        assert (
            "邮件验证功能" in str(e)
            or "请不要往同一个邮件地址发送太多邮件" in str(e)
            or "Too many emails" in str(e)
            or "Please enable the option to verify user emails in application settings."
            in str(e)
        )


@with_setup(get_setup_func())
def test_request_mobile_phone_verify():  # type: () -> None
    try:
        User.request_mobile_phone_verify("1861111" + str(random.randrange(1000, 9999)))
    except LeanCloudError as e:
        if e.code not in (213, 601):
            raise e


@with_setup(only_init)
def test_request_change_phone_number():  # type: () -> None
    user1 = User()
    user1.set("username", "py_test_change_phone")
    user1.set("password", "password")
    user1.sign_up()
    try:
        # phone number is from http://www.z-sms.com
        User.request_change_phone_number("+8617180655340")
    except LeanCloudError as e:
        if e.code in (119, 213, 601, 605):
            pass
        elif "SMS sending exceeds limit" in e.error:
            pass
        elif "send too frequently" in e.error:
            pass
        else:
            raise e
    finally:
        user1.logout()


@with_setup(only_init)
def test_change_phone_number():  # type: () -> None
    try:
        # phone number is from http://www.z-sms.com
        User.change_phone_number("196784", "+8617180655340")
    except LeanCloudError as e:
        if e.code != 603:
            raise e
    else:
        user1 = User()
        user1.set("username", "py_test_change_phone")
        user1.set("password", "password")
        user1.login()
        assert user1.get_mobile_phone_number() == "+8617180655340"
        user1.destroy()


@with_setup(get_setup_func())
def test_request_password_reset_by_sms_code():  # type: () -> None
    try:
        User.request_password_reset_by_sms_code(
            "1861111" + str(random.randrange(1000, 9999))
        )
    except LeanCloudError as e:
        if e.code not in (213, 601):
            raise e


@with_setup(get_setup_func())
def test_reset_password_by_sms_code():  # type: () -> None
    try:
        User.reset_password_by_sms_code(
            str(random.randrange(100000, 999999)),
            "password",
            "1861111" + str(random.randrange(1000, 9999))
        )
    except LeanCloudError as e:
        if e.code != 603:
            raise e


@with_setup(get_setup_func())
def test_request_login_sms_code():  # type: () -> None
    try:
        User.request_login_sms_code("18611111111")
    except LeanCloudError as e:
        if e.code not in (1, 215, 601):
            raise e


@with_setup(get_setup_func())
def test_refresh_session_token():
    user = User()
    user.set("username", "user1_name")
    user.set("password", "password")
    user.login()
    old_session_token = user.get_session_token()
    user.refresh_session_token()
    assert old_session_token != user.get_session_token()


@with_setup(get_setup_func(use_master_key=False))
def test_is_authenticated():
    user = User()
    assert not user.is_authenticated()

    user._session_token = "invalid-session-token"
    assert not user.is_authenticated()

    user = User()
    user.set("username", "user1_name")
    user.set("password", "password")
    user.login()
    assert user.is_authenticated()
