# coding: utf-8

from nose.tools import with_setup

import leancloud
from leancloud import User
from leancloud import Query
from leancloud import File

__author__ = 'asaka <lan@leancloud.rocks>'


def setup_func():
    leancloud.init(
        '6mnpbdqufkybpfwev1jww7ynrqtzv38vadgzlx37rinn9fwk',
        master_key='ywytewi632vunyolpkytb2f13m6im9hmyckerk1koy6ut9y5',
    )
    users = Query(User).find()
    for u in users:
        u.destroy()

    user1 = User()
    user1.set('username', 'user1')
    user1.set('password', 'password')
    user1.sign_up()

    user2 = User()
    user2.set('username', 'user2')
    user2.set('password', 'password')
    user2.sign_up()


def destroy_func():
    pass


@with_setup(setup_func, destroy_func)
def test_sign_up():
    user = User()
    user.set('username', 'foo')
    user.set('password', 'bar')
    user.sign_up()
    assert user._session_token


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


def test_follower_query():
    query = User.create_follower_query('1')
    assert query._friendship_tag == 'follower'
    assert query.dump() == {
        'where': {
            'user': {
                '__type': 'Pointer',
                'className': '_User',
                'objectId': '1',
            },
        },
    }


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
