# coding: utf-8

"""
实时通讯消息相关操作。
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from typing import Any
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional
from typing import Union

import six

from leancloud import client


class Message(object):
    def __init__(self):
        self.bin = None  # type: bool
        self.conversation_id = None  # type: str
        self.data = None  # type: str
        self.from_client = None  # type: str
        self.from_ip = None  # type: str
        self.is_conversation = None  # type: bool
        self.is_room = None  # type: bool
        self.message_id = None  # type: str
        self.timestamp = None  # type: float
        self.to = None  # type: str

    @classmethod
    def _find(cls, query_params):  # type: (dict) -> Generator[Message, None, None]
        content = client.get('/rtm/messages/history', params=query_params).json()
        for data in content:
            msg = cls()
            msg._update_data(data)
            yield msg

    @classmethod
    def find_by_conversation(cls, conversation_id, limit=None, reversed=None, after_time=None, after_message_id=None):
        # type: (str, Optional[int], Optional[bool], Optional[Union[datetime, float]], Optional[str]) -> List[Message]
        """获取某个对话中的聊天记录

        :param conversation_id: 对话 id
        :param limit: 返回条数限制，可选，服务端默认 100 条，最大 1000 条
        :param reversed: 以默认排序相反的方向返回结果，服务端默认为 False
        :param after_time: 查询起始的时间戳，返回小于这个时间(不包含)的记录，服务端默认是当前时间
        :param after_message_id: 起始的消息 id，使用时必须加上对应消息的时间 after_time 参数，一起作为查询的起点
        :return: 符合条件的聊天记录
        """
        query_params = {}  # type: Dict[str, Any]
        query_params['convid'] = conversation_id
        if limit is not None:
            query_params['limit'] = limit
        if reversed is not None:
            query_params['reversed'] = reversed
        if isinstance(after_time, datetime):
            query_params['max_ts'] = after_time.timestamp() * 1000
        elif isinstance(after_time, six.integer_types) or isinstance(after_time, float):
            query_params['max_ts'] = after_time * 1000
        if after_message_id is not None:
            query_params['msgid'] = after_message_id
        return list(cls._find(query_params))

    @classmethod
    def find_by_client(cls, from_client, limit=None, after_time=None, after_message_id=None):
        # type: (str, Optional[int], Optional[Union[datetime, float]], Optional[str]) -> List[Message]
        """获取某个 client 的聊天记录

        :param from_client: 要获取聊天记录的 client id
        :param limit: 返回条数限制，可选，服务端默认 100 条，最大 1000 条
        :param after_time: 查询起始的时间戳，返回小于这个时间(不包含)的记录，服务端默认是当前时间
        :param after_message_id: 起始的消息 id，使用时必须加上对应消息的时间 after_time 参数，一起作为查询的起点
        :return: 符合条件的聊天记录
        """
        query_params = {}  # type: Dict[str, Any]
        query_params['from'] = from_client
        if limit is not None:
            query_params['limit'] = limit
        if isinstance(after_time, datetime):
            query_params['max_ts'] = after_time.timestamp() * 1000
        elif isinstance(after_time, six.integer_types) or isinstance(after_time, float):
            query_params['max_ts'] = after_time * 1000
        if after_message_id is not None:
            query_params['msgid'] = after_message_id
        return list(cls._find(query_params))

    @classmethod
    def find_all(cls, limit=None, after_time=None, after_message_id=None):
        # type: (Optional[int], Optional[Union[datetime, float]], Optional[str]) -> List[Message]
        """获取应用全部聊天记录

        :param limit: 返回条数限制，可选，服务端默认 100 条，最大 1000 条
        :param after_time: 查询起始的时间戳，返回小于这个时间(不包含)的记录，服务端默认是当前时间
        :param after_message_id: 起始的消息 id，使用时必须加上对应消息的时间 after_time 参数，一起作为查询的起点
        :return: 符合条件的聊天记录
        """
        query_params = {}  # type: Dict[str, Any]
        if limit is not None:
            query_params['limit'] = limit
        if isinstance(after_time, datetime):
            query_params['max_ts'] = after_time.timestamp() * 1000
        elif isinstance(after_time, six.integer_types) or isinstance(after_time, float):
            query_params['max_ts'] = after_time * 1000
        if after_message_id is not None:
            query_params['msgid'] = after_message_id
        return list(cls._find(query_params))

    def _update_data(self, server_data):  # type: (dict) -> None
        self.bin = server_data.get('bin')
        self.conversation_id = server_data.get('conv-id')
        self.data = server_data.get('data')
        self.from_client = server_data.get('from')
        self.from_ip = server_data.get('from-ip')
        self.is_conversation = server_data.get('is-conv')
        self.is_room = server_data.get('is-room')
        self.message_id = server_data.get('msg-id')
        self.timestamp = server_data.get('timestamp', 0) / 1000
        self.to = server_data.get('to')
