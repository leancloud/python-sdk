# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import time

from nose.tools import assert_equal
from nose.tools import assert_true

import leancloud
from leancloud import Message
from leancloud import Conversation


def setup():
    leancloud.init(os.environ["APP_ID"], master_key=os.environ["MASTER_KEY"])


def test_message_find_by_conversation():
    conv = Conversation(name="test")
    conv.save()
    conv.send("foo", "what the hell")
    time.sleep(2)  # wait for server sync
    msgs = Message.find_by_conversation(conv.id, limit=1000, reversed=False)
    assert_equal(len(msgs), 1)
    msg = msgs[0]
    assert_equal(msg.bin, False)
    assert_equal(msg.conversation_id, conv.id)
    assert_equal(msg.data, "what the hell")
    assert_equal(msg.from_client, "foo")
    assert_equal(msg.is_conversation, True)
    assert_equal(msg.is_room, False)
    assert_true(msg.message_id)
    assert_equal(msg.to, conv.id)
    conv.destroy()


def test_message_find_by_client():
    conv = Conversation(name="test")
    conv.save()
    conv.send("foo", "what the hell")
    time.sleep(1)  # wait for server sync
    msgs = Message.find_by_client("foo", limit=123)
    assert len(msgs) > 0
    conv.destroy()


def test_message_find_all():
    conv = Conversation(name="test")
    conv.save()
    conv.send("foo", "what the hell")
    time.sleep(1)  # wait for server sync
    msgs = Message.find_all(limit=1000)
    assert len(msgs) > 0
    conv.destroy()
