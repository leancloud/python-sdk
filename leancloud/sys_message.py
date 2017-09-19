# coding: utf-8

"""
实时通讯会话相关操作。
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import arrow

import leancloud
from leancloud.object_ import Object


class SysMessage(Object):
    @property
    def conversation(self):
        """
        此消息对应的对话，对应 conv 字段。

        :rtype: leancloud.Conversation
        """
        return self.get('conv')

    @property
    def message_id(self):
        """
        此消息 id，对应 msgId 字段。

        :rtype: str
        """
        return self.get('msgId')

    @property
    def is_binary(self):
        """
        此消息内容是否为二进制，对应 bin 字段。

        :rtype: bool
        """
        return self.get('bin')

    @property
    def from_client(self):
        """
        此消息发送者 cliend id，对应 client 字段。

        :rtype: str
        """
        return self.get('from')
    
    @property
    def from_ip(self):
        """
        此消息发送者 IP，对应 fromIp 字段。

        :rtype: str
        """
        return self.get('fromIp')

    @property
    def data(self):
        """
        此消息原始内容，如果需要的话，需要手动进行序列化，对应 data 字段。

        :rtype: str
        """
        return self.get('data')

    @property
    def message_created_at(self):
        """
        此消息发送时间，对应 timestamp 字段。

        :rtype: datetime
        """
        return arrow.get(self.get('timestamp') / 1000).to('local').datetime

    @property
    def ack_at(self):
        """
        此消息送达时间，对应 ackAt 字段。

        :rtype: datetime
        """
        return arrow.get(self.get('ackAt') / 1000).to('local').datetime
