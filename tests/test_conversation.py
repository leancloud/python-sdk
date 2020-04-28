# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from nose.tools import assert_equal

import leancloud
from leancloud import Conversation, LeanCloudError


def setup():
    leancloud.client.USE_MASTER_KEY = None
    leancloud.client.APP_ID = None
    leancloud.client.APP_KEY = None
    leancloud.client.MASTER_KEY = None
    leancloud.init(os.environ["APP_ID"], master_key=os.environ["MASTER_KEY"])


def test_create_conversation():
    conv = Conversation("testConversation")
    conv.save()
    assert conv.id
    assert not conv.is_unique
    assert not conv.is_system
    assert not conv.is_transient
    conv.destroy()

    conv = Conversation(
        "testConversation", is_system=True, is_transient=True, is_unique=True
    )
    conv.save()
    assert conv.id
    assert conv.is_system
    assert conv.is_transient
    assert not conv.is_unique
    conv.destroy()

    conv = Conversation("testConversation", is_unique=True)
    conv.save()
    assert conv.id
    assert conv.is_unique
    conv.destroy()

    conv = Conversation("testConversation", is_unique=False)
    conv.save()
    assert conv.id
    assert not conv.is_unique
    conv.destroy()


def test_members():
    conv = Conversation("test")
    conv.add_member("xxx")
    conv.add_member("qqq")
    conv.save()

    conv = Conversation.query.get(conv.id)
    assert_equal(set(conv.members), set(["xxx", "qqq"]))
    conv.add_member("aaa")
    conv.save()
    conv = Conversation.query.get(conv.id)
    assert_equal(set(conv.members), set(["xxx", "qqq", "aaa"]))
    conv.destroy()


def test_send():
    conv = Conversation("test")
    conv.save()
    conv.send("test_user", {"a": 1})
    conv.destroy()


def test_broadcast():
    conv = Conversation("test", is_system=True)
    conv.save()
    try:
        conv.broadcast("system", {"b": 2})
    except LeanCloudError as e:
        if e.code == 1 and e.error == "The daily quota of system messages is exceeded.":
            pass
