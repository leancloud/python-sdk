# coding: utf-8

"""
实时通讯会话相关操作。
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
from datetime import datetime

import arrow

from leancloud import client
from leancloud.object_ import Object


class Conversation(Object):
    """
    :param name: 会话名称
    :param is_system: 是否系统会话
    :param is_transient: 是否暂态会话
    :param is_unique: 是否重用成员相同的会话（暂停会话不支持此参数）
    """

    def __init__(self, name=None, is_system=False, is_transient=False, is_unique=None):
        super(Conversation, self).__init__()
        if name:
            self.set("name", name)
        if is_system:
            self.set("sys", True)

        if is_transient:
            self.set("tr", True)
        else:
            if is_unique is not None:
                self.set("unique", is_unique)

    @property
    def name(self):
        """
        获取此会话名称。
        """
        return self.get("name")

    @property
    def creator(self):
        """
        获取此会话创建者。
        """
        return self.get("c")

    @property
    def last_message_read_at(self):
        """
        获取此会话最后一条已读消息时间。
        """
        return self.get("lm")

    @property
    def members(self):
        """
        获取此会话所有参与者。
        """
        return self.get("m")

    @property
    def muted_members(self):
        """
        获取所有将此会话设置为静音的参与者。
        """
        return self.get("mu")

    @property
    def is_system(self):
        """
        是否为系统会话。
        """
        return self.get("sys")

    @property
    def is_transient(self):
        """
        是否为暂态会话。
        """
        return self.get("tr")

    @property
    def is_unique(self):
        """
        是否为 unique 会话。
        """
        return self.get("unique")

    def add_member(self, client_id):
        """
        将指定参与者加入会话。
        """
        return self.add("m", client_id)

    def send(
        self, from_client, message, to_clients=None, transient=False, push_data=None
    ):
        """
        在指定会话中发送消息。

        :param from_client: 发送者 id
        :param message: 消息内容
        :param to_clients: 接受者 id，只在系统会话中生效
        :param transient: 是否以暂态形式发送消息
        :param push_data: 推送消息内容，参考：https://url.leanapp.cn/pushData
        """
        if isinstance(message, dict):
            message = json.dumps(message)
        params = {
            "from_peer": from_client,
            "conv_id": self.id,
            "transient": transient,
            "message": message,
        }
        if to_clients:
            params["to_peers"] = to_clients
        if push_data:
            params["push_data"] = push_data
        client.post("/rtm/messages", params=params).json()

    def broadcast(self, from_client, message, valid_till=None, push_data=None):
        """
        发送广播消息，只能以系统会话名义发送。全部用户都会收到此消息，不论是否在此会话中。

        :param from_client: 发送者 id
        :param message: 消息内容
        :param valid_till: 指定广播消息过期时间
        :param puhs_data: 推送消息内容，参考：https://url.leanapp.cn/pushData
        """
        if isinstance(message, dict):
            message = json.dumps(message)
        params = {
            "from_peer": from_client,
            "conv_id": self.id,
            "message": message,
        }
        if push_data:
            params["push_data"] = push_data
        if valid_till:
            if isinstance(valid_till, datetime):
                valid_till = arrow.get(valid_till).datetime
            params["valid_till"] = valid_till
        client.post("/rtm/broadcast", params=params).json()
