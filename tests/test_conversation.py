# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from nose.tools import assert_equal

import leancloud
from leancloud import Conversation


def setup():
    leancloud.client.USE_MASTER_KEY = None
    leancloud.client.APP_ID = None
    leancloud.client.APP_KEY = None
    leancloud.client.MASTER_KEY = None
    leancloud.init(
        os.environ['APP_ID'],
        master_key=os.environ['MASTER_KEY']
    )


def test_create_conversation():
    conv = Conversation('testConversation')
    conv.save()
    assert conv.id
    assert not conv.is_system
    assert not conv.is_transient
    conv.destroy()

    conv = Conversation('testConversation', is_system=True, is_transient=True)
    conv.save()
    assert conv.id
    assert conv.is_system
    assert conv.is_transient
    conv.destroy()


def test_members():
    conv = Conversation('test')
    conv.add_member('xxx')
    conv.add_member('qqq')
    conv.save()

    conv = Conversation.query.get(conv.id)
    assert_equal(conv.members, ['xxx', 'qqq'])
    conv.destroy()


def test_send():
    conv = Conversation('test')
    conv.save()
    conv.send('test_user', {'a': 1})
    conv.destroy()


def test_broadcast():
    conv = Conversation('test', is_system=True)
    conv.save()
    conv.broadcast('system', {'b': 2})
