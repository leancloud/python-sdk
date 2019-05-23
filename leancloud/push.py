# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import arrow
import dateutil.tz as tz

from leancloud.object_ import Object
from leancloud.errors import LeanCloudError
from leancloud import client


__author__ = 'asaka <lan@leancloud.rocks>'


class Installation(Object):
    pass


class Notification(Object):
    def fetch(self, *args, **kwargs):
        """同步服务器的 Notification 数据
        """
        response = client.get('/tables/Notifications/{0}'.format(self.id))
        self._update_data(response.json())

    def save(self, *args, **kwargs):
        raise LeanCloudError(code=1, error='Notification does not support modify')


def _encode_time(time):
    tzinfo = time.tzinfo
    if tzinfo is None:
        tzinfo = tz.tzlocal()
    return arrow.get(time, tzinfo).to('utc').format('YYYY-MM-DDTHH:mm:ss.SSS') + 'Z'


def send(data, channels=None, push_time=None, expiration_time=None, expiration_interval=None, where=None, cql=None):
    """
    发送推送消息。返回结果为此条推送对应的 _Notification 表中的对象，但是如果需要使用其中的数据，需要调用 fetch() 方法将数据同步至本地。

    :param channels: 需要推送的频道
    :type channels: list or tuple
    :param push_time: 推送的时间
    :type push_time: datetime
    :param expiration_time: 消息过期的绝对日期时间
    :type expiration_time: datetime
    :param expiration_interval: 消息过期的相对时间，从调用 API 的时间开始算起，单位是秒
    :type expiration_interval: int
    :param where: 一个查询 _Installation 表的查询条件 leancloud.Query 对象
    :type where: leancloud.Query
    :param cql: 一个查询 _Installation 表的查询条件 CQL 语句
    :type cql: string_types
    :param data: 推送给设备的具体信息，详情查看 https://leancloud.cn/docs/push_guide.html#消息内容_Data
    :rtype: Notification
    """
    if expiration_interval and expiration_time:
        raise TypeError('Both expiration_time and expiration_interval can\'t be set')

    params = {
        'data': data,
    }

    if client.USE_PRODUCTION == '0':
        params['prod'] = 'dev'

    if channels:
        params['channels'] = channels
    if push_time:
        params['push_time'] = _encode_time(push_time)
    if expiration_time:
        params['expiration_time'] = _encode_time(expiration_time)
    if expiration_interval:
        params['expiration_interval'] = expiration_interval
    if where:
        params['where'] = where.dump().get('where', {})
    if cql:
        params['cql'] = cql

    result = client.post('/push', params=params).json()

    notification = Notification.create_without_data(result['objectId'])
    return notification
