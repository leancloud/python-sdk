# coding: utf-8

import os

from nose.tools import with_setup

import leancloud
from leancloud import User
from leancloud import Query
from leancloud import File
from leancloud.errors import LeanCloudError

__author__ = 'asaka <lan@leancloud.rocks>'


def only_init():
    leancloud.init(
        os.environ['APP_ID'],
        master_key=os.environ['MASTER_KEY']
    )


def setup_func():
    leancloud.init(
        os.environ['APP_ID'],
        master_key=os.environ['MASTER_KEY']
    )
    users = Query(User).find()
    for u in users:
        u.destroy()

    user1 = User()
    user1.set('username', 'user1')
    user1.set('password', 'password')
    user1.set_email('wow@leancloud.rocks')
    user1.set_mobile_phone_number('18611111111')
    user1.sign_up()
    user1.logout()

    user2 = User()
    user2.set('username', 'user2')
    user2.set('password', 'password')
    user2.sign_up()
    user2.logout()


def destroy_func():
    pass


@with_setup(only_init)
def test_sign_up():
    user = User()
    user.set('username', 'foo')
    user.set('password', 'bar')
    user.sign_up()
    assert user._session_token


@with_setup(only_init)
def test_sign_out():
    user = User()
    user.sign_up('Musen', 'password')
    user.logout()
    assert not user.is_current


@with_setup(setup_func, destroy_func)
def test_login():
    user = User()
    user.set('username', 'user1')
    user.set('password', 'password')
    user.login()

    user = User()
    user.login('user1', 'password')


@with_setup(setup_func, destroy_func)
def test_file_field():
    user = User()
    user.login('user1', 'password')
    user.set('xxxxx', File('xxx.txt', buffer('qqqqq')))
    user.save()

    q = Query(User)
    saved_user = q.get(user.id)
    assert isinstance(saved_user.get('xxxxx'), File)
    assert saved_user.get('xxxxx').name == 'xxx.txt'


@with_setup(setup_func)
def test_follow():
    user1 = User()
    user1.set('username', 'user1')
    user1.set('password', 'password')
    user1.login()

    user2 = User()
    user2.set('username', 'user2')
    user2.set('password', 'password')
    user2.login()

    user1.follow(user2.id)


@with_setup(setup_func)
def test_follower_query():
    user1 = User()
    user1.login('user1', 'password')
    user2 = User()
    user2.login('user2', 'password')
    user2.follow(user1.id)
    query = User.create_follower_query(user1.id)
    assert query.first().id == user2.id


def test_followee_query():
    query = User.create_followee_query('1')
    assert query._friendship_tag == 'followee'
    assert query.dump() == {
        'where': {
            'user': {
                '__type': 'Pointer',
                'className': '_User',
                'objectId': '1',
            },
        },
    }


@with_setup(setup_func)
def test_current_user():
    user = User()
    user.login('user1', 'password')
    assert user.is_current
    assert User.get_current().id == user.id


@with_setup(setup_func)
def test_update_user():
    user = User()
    user.login('user1', 'password')
    user.set('nickname', 'test_name')
    user.save()


@with_setup(setup_func)
def test_user_become():
    existed_user = User()
    existed_user.login('user1', 'password')
    session_token = existed_user.get_session_token()
    user = User.become(session_token)
    assert user.get('username') == existed_user.get('username')


@with_setup(setup_func)
def test_login_with():
    data = {
        "openid": "0395BA18A5CD6255E5BA185E7BEBA242",
        "access_token": "12345678-SaMpLeTuo3m2avZxh5cjJmIrAfx4ZYyamdofM7IjU",
        "expires_in": 1382686496
    }
    User.login_with('weixin', data)


@with_setup(setup_func)
def test_unlink_from():
    data = {
        "openid": "0395BA18A5CD6255E5BA185E7BEBA242",
        "access_token": "12345678-SaMpLeTuo3m2avZxh5cjJmIrAfx4ZYyamdofM7IjU",
        "expires_in": 1382686496
    }
    user = User.login_with('weixin', data)
    user.unlink_from('weixin')


@with_setup(setup_func)
def test_is_linked():
    data = {
        "openid": "0395BA18A5CD6255E5BA185E7BEBA242",
        "access_token": "12345678-SaMpLeTuo3m2avZxh5cjJmIrAfx4ZYyamdofM7IjU",
        "expires_in": 1382686496
    }
    user = User.login_with('weixin', data)
    assert user.is_linked('weixin')


@with_setup(setup_func)
def test_signup_or_login_with_mobile_phone():
    try:
        User.signup_or_login_with_mobile_phone('18611111111', '111111')
    except LeanCloudError as e:
        assert e.code == 603


@with_setup(setup_func)
def test_update_password():
    user = User()
    user.login('user1', 'password')
    user.update_password('password', 'new_password')
    user.login('user1', 'new_password')


@with_setup(setup_func)
def test_get_methods():
    user = User()
    user.login('user1', 'password')

    user.set_username('new_user1')
    assert user.get_username() == 'new_user1'

    user.set_mobile_phone_number('18611111111x')
    assert user.get_mobile_phone_number() == '18611111111x'

    user.set_password('new_password')
    assert user.attributes.get('passWord') == 'new_password'

    user.set_email('wow1@leancloud.rocks')
    assert user.get_email() == 'wow1@leancloud.rocks'


@with_setup(setup_func)
def test_request_password_reset():
    User.request_password_reset('wow@leancloud.rocks')


@with_setup(setup_func)
def test_request_email_verify():
    try:
        User.request_email_verify('wow@leancloud.rocks')
    except LeanCloudError as e:
        assert '邮件验证功能' in str(e)


@with_setup(setup_func)
def test_request_mobile_phone_verify():
    try:
        User.request_mobile_phone_verify('18611111111')
    except LeanCloudError as e:
        assert e.code == 212


@with_setup(setup_func)
def test_request_password_reset_by_sms_code():
    try:
        User.request_password_reset_by_sms_code('111111')
    except LeanCloudError as e:
        assert e.code == 212

# cannot be tested without sms code
# @with_setup(setup_func)
# def test_verify_mobile_phone_number():
#     User.verify_mobile_phone_number('111111')


@with_setup(setup_func)
def test_request_login_sms_code():
    try:
        User.request_login_sms_code('18611111111')
    except LeanCloudError as e:
        assert e.code == 215
