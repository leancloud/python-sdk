# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from datetime import datetime

from nose.tools import assert_equal

import leancloud
from leancloud import Conversation
from leancloud import SysMessage


def setup():
    leancloud.client.USE_MASTER_KEY = None
    leancloud.client.APP_ID = None
    leancloud.client.APP_KEY = None
    leancloud.client.MASTER_KEY = None
    leancloud.init(os.environ["APP_ID"], master_key=os.environ["MASTER_KEY"])


def test_sys_message():
    conv = Conversation("testConversation", is_system=True)
    conv.save()
    msg = SysMessage()
    msg.set("conv", conv)
    msg.set("bin", False)
    msg.set("msgId", "testmsgid")
    msg.set("from", "testfromclient")
    msg.set("fromIp", "0.0.0.0")
    msg.set("data", '{"_lctext":"test!","_lctype":-1}')
    msg.set("timestamp", 1503908409224)
    msg.set("ackAt", 1503908409237)
    msg.save()

    savedMsg = SysMessage.query.get(msg.id)
    assert_equal(msg.conversation.id, savedMsg.conversation.id)
    assert_equal(msg.message_id, savedMsg.message_id)
    assert_equal(msg.from_client, savedMsg.from_client)
    assert_equal(msg.from_ip, savedMsg.from_ip)
    assert_equal(msg.data, savedMsg.data)
    assert_equal(type(savedMsg.message_created_at), datetime)
    assert_equal(type(savedMsg.ack_at), datetime)

    msg.destroy()
